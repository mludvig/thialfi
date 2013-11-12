from django.conf import settings
from django.db import models
from django.core.exceptions import ObjectDoesNotExist

from thialfi.logger import *
import datetime
from sms import smsgw

__all__ = []
# Recipient-related models
class Contact(models.Model):
    name = models.CharField(max_length=200)
    sms_number = models.CharField(max_length=200)

    def __unicode__(self):
        return u"%s (%s)" % (self.name, self.sms_number)
__all__.append("Contact")

class Group(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank = True)
    contacts = models.ManyToManyField(Contact)
    contact_primary = models.ForeignKey(Contact, related_name = "contact_primary", help_text = "On-call contact")

    def __unicode__(self):
        return unicode(self.name)
__all__.append("Group")

class Recipient(models.Model):
    address = models.CharField(max_length=500)
    description = models.TextField(blank = True)
    group = models.ForeignKey(Group)
    require_ack_min = models.IntegerField(default = 0, help_text = "Require ACK withing X minutes. 0 means ACK not required.")
    escalation_group = models.ForeignKey(Group, related_name = "escalation_group", null = True, blank = True, help_text = "Non-ACKed messages will be escalated to this group's primary contact.")

    def __unicode__(self):
        return unicode(self.address)
    def domain(self):
        return settings.RCPT_DOMAIN
__all__.append("Recipient")

# Message-related models
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
        info("Performing escalation...")
        if self.dt_acked or not self.recipient.require_ack_min:
            # ACKed or ACK not required -> nothing to do
            return False

        # We need ACK - is it due yet?
        if not self.older_than(self.dt_received, self.recipient.require_ack_min):
            # Received less than ACK-mins ago -> nothing to do
            return False

        # ACK overdue
        if not self.dt_called:
            # Not yet called -> call now
            if not dry_run:
                self.make_call(self.recipient.group)
                self.dt_called = datetime.datetime.now()
                self.save()
            return True

        # Already called -> are we in CALL_GRACE period?
        if not self.older_than(self.dt_called, settings.CALL_GRACE_MIN):
            # Yes we are, called less than CALL_GRACE_MIN ago -> nothing to do
            return False

        # Call to Primary Contact not ACKed in time
        if not self.dt_escalated:
            # Not yet escalated -> escalate now
            if not dry_run:
                self.make_call(self.recipient.escalation_group)
                self.dt_escalated = datetime.datetime.now()
                self.save()
            return True

        # Escalated more than CALL_GRACE_MIN mins ago and not ACKed? -> Now what???
        #if self.older_than(self.dt_escalated, settings.CALL_GRACE_MIN):
        #    # TODO: Now What??
        return True

    def make_call(self, group):
        info("Calling '%s' [%s]" % (group, group.contact_primary))
__all__.append("Message")

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
                if not self.message.dt_acked or reply.dt_received > self.message.dt_acked:
                    self.message.dt_acked = reply.dt_received
                    self.message.save()

__all__.append("Delivery")

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
__all__.append("Reply")

class PhoneCall(models.Model):
    message = models.ForeignKey(Message)
    contact = models.ForeignKey(Contact)
    message_url = models.CharField(max_length = 500)
    number_called = models.CharField(max_length = 200)
    call_id = models.CharField(max_length = 200)
    status = models.CharField(max_length = 200)
    duration = models.IntegerField(null = True)
    dt_queued = models.DateTimeField(auto_now_add = True)
    dt_called = models.DateTimeField(blank = True, null = True)
    dt_answered = models.DateTimeField(blank = True, null = True)
    dt_acked = models.DateTimeField(blank = True, null = True)
