from django.http import HttpResponse
from utils import render_template, get_object_or_404
from models import *
from datetime import timedelta, datetime
from thialfi.logger import *

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
            phonecall.message.acknowledge()
            phonecall.save()
    return render_template(request, template, {
        "text_to_say" : text_to_say,
        "say_press_1" : not acked,
    })
