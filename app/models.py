from django.db import models

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
__all__.append("Recipient")

# Message-related models
class Message(models.Model):
	header = models.TextField()
	body = models.TextField()
	# The "body" converted to sms format
	sms_body = models.TextField()
	# Some useful headers extracted
	hdr_recipient = models.CharField(max_length=500)
	hdr_message_id = models.CharField(max_length=500)
	# Resolved recipient
	recipient = models.ForeignKey(Recipient)
	# Timestamps
	dt_received = models.DateTimeField(auto_now = True)
	dt_delivered = models.DateTimeField()
	dt_escalated = models.DateTimeField()
	dt_expired = models.DateTimeField()

	def __unicode__(self):
		return self.sms_body[:100]
__all__.append("Message")

class Delivery(models.Model):
	message = models.ForeignKey(Message)
	contact = models.ForeignKey(Contact)
	sms_id = models.CharField(max_length=100)
	dt_despatched = models.DateTimeField(auto_now = True)
	dt_status = models.DateTimeField()
	status = models.CharField(max_length=100)

	class Meta:
		verbose_name_plural = "Deliveries"
	
	def __unicode__(self):
		return u"to:%s @%s" % (self.contact, self.dt_despatched)
__all__.append("Delivery")
