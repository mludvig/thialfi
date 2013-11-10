from django.http import HttpResponse
from utils import render_template, get_object_or_404
from models import *
from datetime import timedelta, datetime

def index(request, template):
    # Display only last 4 weeks worth of messages
    msg_epoch = datetime.now() - timedelta(weeks=4)

    recipients = Recipient.objects.all()
    groups = Group.objects.all()
    messages = Message.objects.filter(dt_received__gt=msg_epoch).order_by('-dt_received')

    #for group in Group.objects.all():
    #    for contact in group.contacts.all():
    #        is_primary = (contact == group.contact_primary)
    #        print u" %s %s" % (is_primary and ">" or " ", contact.name)
    #    if group.contact_primary not in group.contacts.all():
    #        print u"!> %s" % group.contact_primary.name
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
