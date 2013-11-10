from django.conf import settings
from django.db import models

from datetime import datetime
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
	contact_primary = models.ForeignKey(Contact, related_name = "contact_primary")

	def __unicode__(self):
		return unicode(self.name)
__all__.append("Group")

class Recipient(models.Model):
	address = models.CharField(max_length=500)
	description = models.TextField(blank = True)
	group = models.ForeignKey(Group)

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
	dt_received = models.DateTimeField(auto_now = True)
	dt_delivered = models.DateTimeField(blank = True, null = True)
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

__all__.append("Message")

class Delivery(models.Model):
	message = models.ForeignKey(Message)
	contact = models.ForeignKey(Contact)
	sms_id = models.CharField(max_length=100)
	dt_despatched = models.DateTimeField(auto_now = True)
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
__all__.append("Delivery")
