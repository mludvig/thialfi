from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.core.validators import RegexValidator
from django.contrib import admin
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone

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

    class Meta:
        ordering = ['name']

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

    class Meta:
        ordering = ['name']

    def __unicode__(self):
        return unicode(self.name)

    def set_contact_primary(self, contact):
        assert(contact in self.contacts.all())
        old_contact = self.contact_primary
        self.contact_primary = contact
        self.save()
        return old_contact

class GroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_primary')

admin.site.register(Group, GroupAdmin)

### Recipient model

__all__.append("Recipient")
class Recipient(models.Model):
    address = models.CharField(max_length=500, help_text = 'Use only lowercase letters, digits and hyphens', validators = [ RegexValidator(r'^[a-z][a-z0-9\._-]+$', 'Use only lowercase letters, digits and hyphens') ])
    description = models.TextField(blank = True)
    group = models.ForeignKey(Group)
    require_ack_min = models.IntegerField(default = 0, help_text = "Require ACK within X minutes or trigger Escalation. 0 means ACK not required.")
    escalation_group = models.ForeignKey(Group, related_name = "escalation_group", null = True, blank = True, help_text = "Non-ACKed messages will be escalated to this group's primary contact. If not set call the main Group again.")
    dt_last_called = models.DateTimeField(null = True)

    class Meta:
        ordering = ['address']

    def __unicode__(self):
        return unicode(self.address)

    def domain(self):
        return settings.RCPT_DOMAIN

    def update_last_called(self):
        self.dt_last_called = timezone.now()
        self.save()

    def can_call(self):
        if not self.dt_last_called:
            return True
        return (timezone.now() - self.dt_last_called).total_seconds() > settings.CALL_GRACE_MIN * 60

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
    # Timestamp
    dt_received = models.DateTimeField(auto_now_add = True)

    def __unicode__(self):
        return self.sms_body

    def acknowledge(self, ack_by = "<unknown>"):
        info("{%d} ACK by %s" % (self.id, ack_by))
        self.add_status('acked', note = ack_by)

    def despatch(self):
        if self.get_status('delivered') or self.get_status('expired') or self.get_status('ignored'):
            return
        recent_timestamp = timezone.now() - datetime.timedelta(minutes = settings.RECENT_MINUTES)
        recent_messages = MessageStatus.objects.filter(
                status = 'received',
                message__recipient = self.recipient,
                message__dt_received__gt = recent_timestamp)
        if recent_messages.count() > settings.RECENT_MESSAGES:
            message = '%d messages received in the last %d minutes' % (recent_messages.count(), settings.RECENT_MINUTES)
            info("Ignoring message for %s: %s" % (self.recipient, message))
            self.add_status('ignored', note = message)
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
        ms_set = self.messagestatus_set.order_by("-pk")
        if ms_set:
            return ms_set[0]

    def add_status(self, status, note = ""):
        dt_status = timezone.now()
        MessageStatus(message = self, status = status, dt_status = dt_status, note = note).save()

    def get_status(self, status):
        ms_set = self.messagestatus_set.filter(status = status).order_by("-pk")
        if ms_set:
            return ms_set[0]
        return None

    def get_timestamp(self, status):
        ms = self.get_status(status)
        if ms:
            return ms.dt_status
        return None

    def older_than(self, timestamp, minutes):
        return bool(timestamp) and timestamp + datetime.timedelta(minutes = minutes) < timezone.now()

    def is_overdue(self):
        return self.process_escalation(dry_run = True)

    def sync_acks(self):
        for delivery in self.delivery_set.all():
            for reply in delivery.reply_set.all():
                self.acknowledge("Reply %d from %s @ %s" % (reply.id, reply.delivery.contact, reply.dt_received))
        for phonecall in self.phonecall_set.all():
            if phonecall.dt_acked:
                self.acknowledge("PhoneCall %s - %s @ %s" % (phonecall.id, phonecall.contact, phonecall.dt_acked))

    def perform_escalation(self, dry_run = False):
        self.sync_acks()
        if self.get_status('acked') or not self.recipient.require_ack_min:
            return False

        debug("{%d} Performing escalation...", self.id)
        if not self.older_than(self.dt_received, self.recipient.require_ack_min):
            debug("Received less than ACK-mins ago -> nothing to do")
            return False

        if not self.get_status('called'):
            debug("Not yet called -> call now")
            if not dry_run:
                self.call_group()
            return True

        debug("Already called -> are we in CALL_GRACE period?")
        if not self.older_than(self.get_timestamp('called'), settings.CALL_GRACE_MIN):
            debug("Yes we are, called less than CALL_GRACE_MIN ago -> nothing to do")
            return False

        debug("Call to Primary Contact not ACKed in time")
        if not self.get_status('escalated'):
            debug("Not yet escalated -> escalate now")
            if not dry_run:
                return self.call_escalation_group()
            return True

        if self.older_than(self.get_timestamp('escalated'), settings.CALL_GRACE_MIN):
            debug("Escalated more than CALL_GRACE_MIN mins ago and not ACKed? -> Try again!")
            if not dry_run:
                # Call both the Group and Escalation Group if they are different
                self.call_group()
                if not self.recipient.escalation_group or self.recipient.escalation_group.contact_primary.sms_number == self.recipient.group.contact_primary.sms_number:
                    debug("Escalation Group not set or same as Primary Contact")
                else:
                    self.call_escalation_group()

        return True

    def call_group(self):
        message = "Alert for recipient %s. Group %s" % (self.recipient, self.recipient.group)
        return self.make_call(self.recipient.group, message)

    def call_escalation_group(self):
        if not self.recipient.escalation_group:
            self.add_status('escalated', note = "No escalation group set - call Primary Contact again")
            return self.make_call(self.recipient.group, "Alert for recipient %s. Group %s" % (self.recipient, self.recipient.group))
        else:
            self.add_status('escalated', note = "Calling escalation group %s" % self.recipient.escalation_group)
            return self.make_call(self.recipient.escalation_group, "Escalating alert for group %s. Was unable to contact %s." % (self.recipient.group.name, self.recipient.group.contact_primary.name))

    def make_call(self, group, text_to_say):
        if not self.recipient.can_call():
            self.add_status("not-called", note = "Call already in progress for recipient %s" % self.recipient)
            return False
        info("Calling '%s' [%s]: %s" % (group, group.contact_primary, text_to_say))
        pc = PhoneCall(message = self, contact = group.contact_primary, text_to_say = text_to_say)
        pc.save()
        self.recipient.update_last_called()
        self.add_status('called', note = text_to_say)
        pc.call()
        return True

@receiver(post_save, sender = Message)
def message_add_default_status(sender, instance, created, **kwargs):
    if created and not instance.get_status('received'):
        instance.add_status('received')

class MessageAdmin(admin.ModelAdmin):
    list_display = ('sms_body', 'recipient', 'dt_received')
    list_filter = ('recipient', 'dt_received')

admin.site.register(Message, MessageAdmin)

### MessageStatus model

__all__.append("MessageStatus")
class MessageStatus(models.Model):
    STATUSES = (
        ('unknown', 'unknown'),
        ('received', 'received'),
        ('ignored', 'ignored'),
        ('transit', 'transit'),
        ('expired', 'expired'),
        ('delivered', 'delivered'),
        ('called', 'called'),
        ('escalated', 'escalated'),
        ('acked', 'acked'),
    )
    message = models.ForeignKey(Message)
    status = models.CharField(max_length = 20, choices = STATUSES, null = False, editable = False)
    dt_status = models.DateTimeField(null = False, editable = False)
    note = models.CharField(max_length = 500, default = "", editable = False)

    def __unicode__(self):
        return u"%s %s [%s]" % (self.dt_status.strftime("%Y-%m-%d %H:%M:%S"), self.status, self.note)

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
                self.message.add_status(self.status.lower(), note = "SMSC timestamp: %s" % self.dt_status)
        if self.status.startswith("DELIVERED") and not self.message.get_status('delivered'):
            self.message.add_status('delivered', note = "SMSC timestamp: %s" % self.dt_status)

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
        if not self.message.get_status('acked'):
            for reply in self.reply_set.all():
                self.message.acknowledge("SMS: %s (%s)" % (reply.message, reply.delivery.contact))

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
        ordering = ['-dt_queued']

    def __unicode__(self):
        return u"%s:%s@%s" % (self.status, self.number_called, self.dt_queued)

    def call(self):
        if not self.number_called:
            self.number_called = self.contact.sms_number
        voice_url = settings.VOICE_URL % {'path': reverse('app.views.twilio', kwargs={ 'phonecall_id' : self.id })}
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
