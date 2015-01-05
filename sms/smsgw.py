from thialfi import settings
from sms.Sender import SmsSender
from sms.SimpleObjects import SmsMessage

## Cache sender object
_sender = None

def _get_sender():
    global _sender
    if not _sender:
        _sender = SmsSender()
    return _sender

def despatch(message, contact):
    sender = _get_sender()
    smsmessage = SmsMessage(message = message, recipients = [contact.sms_number])
    return sender.send(smsmessage)[0]

def get_status(sms_id):
    sender = _get_sender()
    status = sender.get_status(mids = [sms_id], keep = False)
    try:
        return status[0]
    except:
        return None

def get_replies(delivery_id):
    sender = _get_sender()
    return sender.receive(in_reply_to = [delivery_id], keep = False)
