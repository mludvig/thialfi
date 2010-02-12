from django.http import HttpResponse
from utils import render_template, get_object_or_404
from models import *

def index(request, template):
	recipients = Recipient.objects.all()
	groups = Group.objects.all()
	messages = Message.objects.order_by('-dt_received')

	#for group in Group.objects.all():
	#	for contact in group.contacts.all():
	#		is_primary = (contact == group.contact_primary)
	#		print u" %s %s" % (is_primary and ">" or " ", contact.name)
	#	if group.contact_primary not in group.contacts.all():
	#		print u"!> %s" % group.contact_primary.name
	return render_template(request, template, {
		"groups" : groups,
		"recipients" : recipients,
		"messages" : messages
	})

def detail(request, template, message_id):
	message = get_object_or_404(Message, pk=message_id)
	return render_template(request, template, {
		"message" : message
	})
