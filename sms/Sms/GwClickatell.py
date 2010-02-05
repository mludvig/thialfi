from Sender import SmsError
import GwGenericHttp

class SmsDriver(GwGenericHttp.SmsDriver):
	def send(self, message, recipient):
		ret = super(self.__class__, self).send(message, recipient)
		arr = ret.split("\n")[0].split(" ", 1)
		if arr[0].startswith("ID"):
			print("SMS(Clickatell) sent to %s with ID: %s" % (recipient, arr[1]))
			return arr[1]
		else:
			raise SmsError("SMS(Clickatell): %s" % arr[1])
