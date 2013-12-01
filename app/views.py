from django.http import HttpResponse
from django.template import RequestContext
from utils import render_template, get_object_or_404
from models import *
from datetime import timedelta, datetime
from thialfi.logger import *

def index(request, template):
    # Display only last 1 week worth of messages
    msg_epoch = datetime.now() - timedelta(weeks=1)

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
            phonecall.message.acknowledge(phonecall.dt_acked, "PhoneCall %s (%s)" % (phonecall.id, phonecall.contact))
            phonecall.save()
    return render_template(request, template, {
        "text_to_say" : text_to_say,
        "say_press_1" : not acked,
    })

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
        },
        context_instance =  RequestContext(request)
    )
