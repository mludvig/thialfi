import sys, os
from Config import Config

class SmsError(Exception):
	pass

class SmsStatus(object):
	def __init__(self, code, descr = "", verbose = ""):
		assert(code in [ "UNKNOWN", "TRANSIT", "ERROR", "EXPIRED", "DELIVERED" ])
		self.code = code
		self.descr = descr
		self.verbose = verbose
	
	def __str__(self):
		return "%s - %s" % (self.code, self.descr)

class SmsSender(object):
	def __init__(self, **kwargs):
		sys.path.insert(0, os.path.dirname(__file__))
		driver_module = __import__(Config().sms_engine.replace(".","/"))
		self._driver = driver_module.SmsDriver(**kwargs)

	def send(self, message = None, recipient = None):
		assert(message and recipient)

		return self._driver.send(message, recipient)
	
	def get_status(self, message_id):
		return self._driver.get_status(message_id)
		#try:
		#	return self._driver.get_status(message_id)
		#except:
		#	return "<???>"
