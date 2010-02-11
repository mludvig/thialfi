from Sms.Config import Config
from Sms.Sender import SmsSender

## Create config object
cfg = Config()

def despatch(message, contact):
	sender = SmsSender()
	sms_id = sender.send(message.sms_body, contact.sms_number)
	return sms_id, sender.get_status(sms_id)

def get_status(sms_id):
	"""
	get_status(sms_id) -> returns Sms.Sender.SmsStatus() object
	"""
	sender = SmsSender()
	status = sender.get_status(sms_id)
	return status
