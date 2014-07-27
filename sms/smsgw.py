import sys
from thialfi import settings

try:
    sys.path.append(settings.SMS_CLI_PATH)
except:
    pass

from Sms.Config import Config
from Sms.Sender import SmsSender
from Sms.SimpleObjects import SmsMessage

## Create config object
cfg = Config(open(settings.SMS_CLI_CONF), settings.SMS_CLI_PROFILE)

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
