from django.http import HttpResponse
from utils import render_template
from models import *

def index(request):
	recipients = Recipient.objects.all()
	groups = Group.objects.all()
	messages = Message.objects.all()

	#for group in Group.objects.all():
	#	for contact in group.contacts.all():
	#		is_primary = (contact == group.contact_primary)
	#		print u" %s %s" % (is_primary and ">" or " ", contact.name)
	#	if group.contact_primary not in group.contacts.all():
	#		print u"!> %s" % group.contact_primary.name

	return render_template(request, "thialfi/index.html", {
		"groups" : groups,
		"recipients" : recipients,
		"messages" : messages
	})
