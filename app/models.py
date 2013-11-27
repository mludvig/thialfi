from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.contrib import admin

from thialfi.logger import *
from thialfi.voice import twiliogw
import datetime
from sms import smsgw
from random_primary import RandomPrimaryIdModel

__all__ = []

### Contact model

__all__.append("Contact")
class Contact(models.Model):
    name = models.CharField(max_length=200)
    sms_number = models.CharField(max_length=200)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.sms_number)

admin.site.register(Contact)

### Group model

__all__.append("Group")
class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    contacts = models.ManyToManyField(Contact)
    contact_primary = models.ForeignKey(Contact, related_name = "contact_primary", help_text = "On-call contact")

    def __unicode__(self):
        return unicode(self.name)

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_primary')

admin.site.register(Group, GroupAdmin)

### Recipient model

__all__.append("Recipient")
class Recipient(models.Model):
    address = models.CharField(max_length=500, help_text = 'Use only lowercase letters, digits and hyphens', validators = [ RegexValidator(r'^[a-z][a-z0-9-]+$', 'Use only lowercase letters, digits and hyphens') ])
    description = models.TextField(blank = True)
    group = models.ForeignKey(Group)
    require_ack_min = models.IntegerField(default = 0, help_text = "Require ACK within X minutes or trigger Escalation. 0 means ACK not required.")
    escalation_group = models.ForeignKey(Group, related_name = "escalation_group", null = True, blank = True, help_text = "Non-ACKed messages will be escalated to this group's primary contact. If not set call the main Group again.")

    def __unicode__(self):
        return unicode(self.address)

    def domain(self):
        return settings.RCPT_DOMAIN

class RecipientAdmin(admin.ModelAdmin):
    list_display = ('address', 'group', 'escalation_group')

admin.site.register(Recipient, RecipientAdmin)

### Message model

__all__.append("Message")
class Message(models.Model):
    header = models.TextField()
    body = models.TextField()
    # The "body" converted to sms format
    sms_body = models.TextField()
    # Some useful headers extracted
    hdr_subject = models.CharField(max_length=500)
    hdr_sender = models.CharField(max_length=500)
    hdr_recipient = models.CharField(max_length=500)
    hdr_message_id = models.CharField(max_length=500)
    # Resolved recipient
    recipient = models.ForeignKey(Recipient)
    # Timestamps
    dt_received = models.DateTimeField(auto_now_add = True)
    dt_delivered = models.DateTimeField(blank = True, null = True)
    dt_acked = models.DateTimeField(blank = True, null = True)
    dt_called = models.DateTimeField(blank = True, null = True)
    dt_escalated = models.DateTimeField(blank = True, null = True)
    dt_expired = models.DateTimeField(blank = True, null = True)

    def __unicode__(self):
        return self.sms_body

    def acknowledge(self, dt_acked = None, ack_by = "<unknown>"):
        if dt_acked is None:
            dt_acked = datetime.datetime.now()
        info("{%d} ACK by %s @ %s" % (self.id, ack_by, dt_acked))
        if not self.dt_acked or dt_acked > self.dt_acked:
            self.dt_acked = dt_acked
        self.save()

    def despatch(self):
        if self.dt_delivered or self.dt_expired:
            return
        if self.delivery_set.all():
            ## Delivery in progress
            ## - update delivery status
            ## - if too old escalate or expire message
            self.update_status()
        else:
            ## No delivery attempted yet
            ## - despatch now
            delivery = Delivery(message = self, contact = self.recipient.group.contact_primary)
            status = smsgw.despatch(self, delivery.contact)
            if status.despatched:
                delivery.sms_id = status.mid
                delivery.status = status.status
                delivery.dt_despatched = status.timestamp
                delivery.save()

    def update_status(self):
        for delivery in self.delivery_set.all():
            delivery.update_status()

    def newest_status(self):
        try:
            delivery = self.delivery_set.order_by('dt_status')[0]
            return delivery.status.split(" ")[0].lower()
        except IndexError:
            return "unknown"

    def older_than(self, timestamp, minutes):
        return bool(timestamp) and timestamp + datetime.timedelta(minutes = minutes) < datetime.datetime.now()

    def is_overdue(self):
        return self.process_escalation(dry_run = True)

    def perform_escalation(self, dry_run = False):
        info("{%d} Performing escalation...", self.id)
        if self.dt_acked or not self.recipient.require_ack_min:
            debug("ACKed or ACK not required -> nothing to do")
            return False

        debug("We need ACK - is it due yet?")
        if not self.older_than(self.dt_received, self.recipient.require_ack_min):
            debug("Received less than ACK-mins ago -> nothing to do")
            return False

        debug("ACK overdue")
        if not self.dt_called:
            debug("Not yet called -> call now")
            if not dry_run:
                self.call_group()
            return True

        debug("Already called -> are we in CALL_GRACE period?")
        if not self.older_than(self.dt_called, settings.CALL_GRACE_MIN):
            debug("Yes we are, called less than CALL_GRACE_MIN ago -> nothing to do")
            return False

        debug("Call to Primary Contact not ACKed in time")
        if not self.dt_escalated:
            debug("Not yet escalated -> escalate now")
            if not dry_run:
                self.call_escalation_group()
            return True

        if self.older_than(self.dt_escalated, settings.CALL_GRACE_MIN):
            error("Escalated more than CALL_GRACE_MIN mins ago and not ACKed? -> Try again!")
            if not dry_run:
                self.call_group()
                if not self.recipient.escalation_group or self.recipient.escalation_group.contact_primary.sms_number == self.recipient.group.contact_primary.sms_number:
                    info("Escalation Group not set or same as Primary Contact")
                else:
                    self.call_escalation_group()

        return True

    def call_group(self):
        self.make_call(self.recipient.group, "Alert for recipient %s. Group %s" % (self.recipient, self.recipient.group))
        self.dt_called = datetime.datetime.now()
        self.save()

    def call_escalation_group(self):
        if not self.recipient.escalation_group:
            debug("No escalation group set - call Primary Contact again")
            self.make_call(self.recipient.group, "Alert for recipient %s. Group %s" % (self.recipient, self.recipient.group))
        else:
            self.make_call(self.recipient.escalation_group, "Escalating alert for group %s. Was unable to contact %s." % (self.recipient.group.name, self.recipient.group.contact_primary.name))
        self.dt_escalated = datetime.datetime.now()
        self.save()

    def make_call(self, group, text_to_say):
        info("Calling '%s' [%s]: %s" % (group, group.contact_primary, text_to_say))
        pc = PhoneCall(message = self, contact = group.contact_primary, text_to_say = text_to_say)
        pc.save()
        pc.call()

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sms_body', 'recipient', 'dt_received', 'dt_acked')
    list_filter = ('recipient', 'dt_received')

admin.site.register(Message, MessageAdmin)

### Delivery model

__all__.append("Delivery")
class Delivery(models.Model):
    message = models.ForeignKey(Message)
    contact = models.ForeignKey(Contact)
    sms_id = models.CharField(max_length=100)
    dt_despatched = models.DateTimeField(auto_now_add = True)
    dt_status = models.DateTimeField(blank = True, null = True)
    status = models.CharField(max_length=100)

    class Meta:
        verbose_name_plural = "Deliveries"

    def __unicode__(self):
        return u"to:%s @%s (%s)" % (self.contact, self.dt_despatched, self.status.split(" ")[0])

    def update_status(self):
        if not self.status.startswith("DELIVERED"):
            status = smsgw.get_status(self.sms_id)
            if not status:
                return
            if status.status != self.status:
                self.status = status.status
                self.dt_status = status.timestamp
                self.save()
        if self.status.startswith("DELIVERED") and not self.message.dt_delivered:
            self.message.dt_delivered = self.dt_status
            self.message.save()

    def get_replies(self, force = False):
        if force or not self.reply_set.all():
            # Only run if we have no replies or if force==True
            rcvd_replies = smsgw.get_replies(self.sms_id)
            for r_reply in rcvd_replies:
                try:
                    if r_reply.mid and self.reply_set.get(reply_id = r_reply.mid):
                        continue
                except ObjectDoesNotExist:
                    reply = self.reply_set.create()
                    reply.message = r_reply.message
                    reply.dt_received = r_reply.timestamp
                    reply.reply_id = r_reply.mid
                    reply.sender = r_reply.sender
                    reply.save()
        if not self.message.dt_acked:
            for reply in self.reply_set.all():
                self.message.acknowledge(reply.dt_received, "Reply %d (%s)" % (reply.id, reply.delivery.contact))

admin.site.register(Delivery)

### Reply model

__all__.append("Reply")
class Reply(models.Model):
    delivery = models.ForeignKey(Delivery)
    sender = models.CharField(max_length=100)
    reply_id = models.CharField(max_length=100)
    dt_received = models.DateTimeField(auto_now_add = True)
    message = models.TextField()

    class Meta:
        verbose_name_plural = "Replies"

    def __unicode__(self):
        return u"%s [%s] %s" % (self.sender, self.dt_received, self.message)

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('dt_received', 'message', 'sender', 'delivery_message')
    list_filter = ('dt_received',)

    def delivery_message(self, object):
        return "%s" % (object.delivery.message)
    delivery_message.short_description = "Alert Message"

admin.site.register(Reply, ReplyAdmin)

### PhoneCall model

__all__.append("PhoneCall")
class PhoneCall(RandomPrimaryIdModel):
    message = models.ForeignKey(Message)
    contact = models.ForeignKey(Contact)
    number_called = models.CharField(max_length = 200)
    call_id = models.CharField(max_length = 200, null = True)
    status = models.CharField(max_length = 200, null = True)
    text_to_say = models.CharField(max_length = 500, null = True)
    numbers_gathered = models.CharField(max_length = 50, null = True)
    duration = models.IntegerField(null = True)
    dt_queued = models.DateTimeField(auto_now_add = True)
    dt_called = models.DateTimeField(blank = True, null = True)
    dt_answered = models.DateTimeField(blank = True, null = True)
    dt_acked = models.DateTimeField(blank = True, null = True)

    class Meta:
        abstract = False
        ordering = ('-dt_queued',)

    def __unicode__(self):
        return u"%s:%s@%s" % (self.status, self.number_called, self.dt_queued)

    def call(self):
        if not self.number_called:
            self.number_called = self.contact.sms_number
        voice_url = "http://%s%s" % (settings.RCPT_DOMAIN, reverse('app.views.twilio', kwargs={ 'phonecall_id' : self.id }))
        debug("voice_url=%s" % voice_url)
        c = twiliogw.make_call(self.number_called, voice_url)
        self.status = c.status
        self.call_id = c.sid
        self.number_called = c.to
        self.save()

class PhoneCallAdmin(admin.ModelAdmin):
    list_display = ('dt_queued', 'status', 'message', 'contact')
    list_filter = ('status', 'contact')

admin.site.register(PhoneCall, PhoneCallAdmin)
