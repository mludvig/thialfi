import urllib
import urllib2

## Must be full path because this module is imported via __import__()
from Config import Config
from Sender import SmsError

class SmsDriver(object):
	def callurl(self, url):
		u = urllib2.urlopen(url)
		if u.code != 200:
			raise SmsError("HTTP Return code = %d" % u.code)
		return u.read()

	def send(self, message, recipient):
		url = Config().sms_send_pattern.strip('"\'') % { 'message' : urllib.quote(message), 'recipient' : recipient }
		return self.callurl(url)

	def get_status(self, messageid):
		url = Config().sms_status_pattern.strip('"\'') % { 'messageid' : urllib.quote(messageid) }
		return self.callurl(url)
