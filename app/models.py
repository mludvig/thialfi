from django.db import models

# Recipient-related models
class Contact(models.Model):
	name = models.CharField(max_length=200)
	sms_number = models.CharField(max_length=200)

class Group(models.Model):
	name = models.CharField(max_length=200)
	description = models.TextField()
	contacts = models.ManyToManyField(Contact)
	contact_primary = models.ForeignKey(Contact, related_name = "contact_primary")

class Recipient(models.Model):
	address = models.CharField(max_length=500)
	description = models.TextField()
	group = models.ForeignKey(Group)

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

class Delivery(models.Model):
	message = models.ForeignKey(Message)
	contact = models.ForeignKey(Contact)
	sms_id = models.CharField(max_length=100)
	dt_despatched = models.DateTimeField(auto_now = True)
	dt_status = models.DateTimeField()
	status = models.CharField(max_length=100)
