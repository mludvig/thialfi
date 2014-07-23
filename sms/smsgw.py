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

def despatch(message, contact):
    sender = SmsSender()
    smsmessage = SmsMessage(message = message, recipients = [contact.sms_number])
    return sender.send(smsmessage)[0]

def get_status(sms_id):
    sender = SmsSender()
    status = sender.get_status(mids = [sms_id], keep = False)
    try:
        return status[0]
    except:
        return None

def get_replies(delivery_id):
    sender = SmsSender()
    return sender.receive(in_reply_to = [delivery_id], keep = False)
