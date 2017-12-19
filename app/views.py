from django.http import HttpResponse
from django.shortcuts import render
from django.template import RequestContext
from django.conf import settings
from utils import render_template, get_object_or_404
from models import *
from datetime import timedelta, datetime
from thialfi.logger import *

def index(request, template):
    recipients = Recipient.objects.all()
    groups = Group.objects.all()

    return render_template(request, template, {
        "groups" : groups,
        "recipients" : recipients,
    })

def messages(request, template):
    # Display only last 1 week worth of messages
    msg_epoch = datetime.now() - timedelta(weeks=1)
    messages = Message.objects.filter(dt_received__gt=msg_epoch).order_by('-dt_received')
    groups = Group.objects.all()

    return render_template(request, template, {
        "groups" : groups,
        "messages" : messages
    })

def detail(request, template, message_id):
    message = get_object_or_404(Message, pk=message_id)
    return render_template(request, template, {
        "message" : message
    })

def twilio(request, template, phonecall_id):
    debug("twilio request for PhoneCall=%s" % phonecall_id)
    debug("GET: %r" % request.GET)
    phonecall = get_object_or_404(PhoneCall, pk=phonecall_id)
    text_to_say = phonecall.text_to_say
    acked = False
    if request.GET.get("Digits") == "1":
        acked = True
        text_to_say = "Call acknowledged. Thank You."
        if request.GET.get('CallSid') != phonecall.call_id:
            error("Received SID != stored SID: '%s' != '%s'" % (request.GET.get('CallSid'), phonecall.call_id))
        else:
            phonecall.status = request.GET.get('CallStatus')
            phonecall.dt_acked = datetime.now()
            phonecall.message.acknowledge("PhoneCall %s (%s)" % (phonecall.status, phonecall.contact))
            phonecall.save()
    return render_template(request, template, {
        "text_to_say" : text_to_say,
        "say_press_1" : not acked,
    })

def report_csv(request, template):
    msg_epoch = datetime.now() - timedelta(weeks=1)
    messages = Message.objects.filter(dt_received__gt=msg_epoch).order_by('-dt_received')

    return render(request, template, { "messages": messages }, content_type = "text/plain")

def group(request, template, group_id):
    group = get_object_or_404(Group, pk = group_id)
    error_message = ""
    if request.POST.has_key('contact'):
        try:
            contact = group.contacts.get(pk = request.POST['contact'])
            if contact == group.contact_primary:
                error_message = "Primary contact not changed: %s" % contact.name
            else:
                old_contact = group.set_contact_primary(contact)
                error_message = "Primary contact changed from %s to %s" % (old_contact.name, contact.name)

        except Contact.DoesNotExist:
            # Re-display the form
            error_message = "Selected contact is not a member of this Group"
    return render_template(request, template, {
            "group" : group,
            "error_message" : error_message,
            "domain" : settings.RCPT_DOMAIN,
        }
    )
