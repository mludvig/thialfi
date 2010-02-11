import re
from Sender import SmsError, SmsStatus
import GwGenericHttp

status_table = {
 1 : SmsStatus("UNKNOWN",   "001 Message unknown", "The message ID is incorrect or reporting is delayed."),
 2 : SmsStatus("TRANSIT",   "002 Message queued", "The message could not be delivered and has been queued for attempted redelivery."),
 3 : SmsStatus("TRANSIT",   "003 Delivered to gateway", "Delivered to the upstream gateway or network (delivered to the recipient)."),
 4 : SmsStatus("DELIVERED", "004 Received by recipient", "Confirmation of receipt on the handset of the recipient."),
 5 : SmsStatus("ERROR",     "005 Error with message", "There was an error with the message, probably caused by the content of the message itself."),
 6 : SmsStatus("EXPIRED",   "006 User cancelled message delivery", "The message was terminated by a user (stop message command) or by our staff."),
 7 : SmsStatus("ERROR",     "007 Error delivering message", "An error occurred delivering the message to the handset."),
 8 : SmsStatus("TRANSIT",   "008 OK", "Message received by gateway."),
 9 : SmsStatus("ERROR",     "009 Routing error", "The routing gateway or network has had an error routing the message."),
10 : SmsStatus("EXPIRED",   "010 Message expired", "Message has expired before we were able to deliver it to the upstream gateway. No charge applies."),
11 : SmsStatus("TRANSIT",   "011 Message queued for later delivery", "Message has been queued at the gateway for delivery at a later time (delayed delivery)."),
12 : SmsStatus("ERROR",     "012 Out of credit", "The message cannot be delivered due to a lack of funds in your account. Please re-purchase credits."),
}

class SmsDriver(GwGenericHttp.SmsDriver):
	def send(self, message, recipient):
		ret = super(self.__class__, self).send(message, recipient)
		arr = ret.split("\n")[0].split(" ", 1)
		if arr[0].startswith("ID"):
			#print("SMS(Clickatell) sent to %s with ID: %s" % (recipient, arr[1]))
			return arr[1]
		else:
			raise SmsError("SMS(Clickatell): %s" % arr[1])

	def get_status(self, messageid):
		ret = super(self.__class__, self).get_status(messageid)
		m = re.match("ID: ([0-9a-fA-F]+) Status: (\d+)", ret)
		if m and m.group(1) == messageid:
			try:
				return status_table[int(m.group(2))]
			except KeyError:
				return SmsStatus("UNKNOWN", "Unknown status code: %s" % m.group(2))
		else:
			raise SmsError("SMS(Clickatell): queried msgid=%s got reply: %s" % (messageid, ret))
