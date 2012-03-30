import sys
from thialfi import settings

try:
	sys.path.append(settings.SMS_CLI_PATH)
except:
	pass

from Sms.Config import Config
from Sms.Sender import SmsSender

## Create config object
cfg = Config(settings.SMS_CLI_CONF, settings.SMS_CLI_PROFILE)

def despatch(message, contact):
	sender = SmsSender()
	sms_ok, sms_ids = sender.send(message.sms_body, [contact.sms_number])
	return sms_ids[0], get_status(sms_ids[0])

def get_status(sms_id):
	"""
	get_status(sms_id) -> returns Sms.Sender.SmsStatus() object
	"""
	sender = SmsSender()
	try:
		status = sender.get_status(sms_id)
	except AttributeError, e:
		return "UNKNOWN"
	return status
