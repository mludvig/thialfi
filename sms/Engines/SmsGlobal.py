## Michal Ludvig <mludvig@logix.net.nz>
## http://www.logix.cz/michal/devel/sms-cli
## License: GPL Version 2

from logger import *
from sms.Exceptions import SmsError
from sms.SimpleObjects import SmsDeliveryStatus
from . import GenericHttp

class SmsDriver(GenericHttp.SmsDriver):
    url_pattern = "https://www.smsglobal.com/http-api.php?action=sendsms&user=%(username)s&password=%(password)s&from=%(sender)s&to=%(recipient)s&text=%(message)s"

    def sendOne(self, message, recipient):
        debug("SmsGlobal.sendOne(%s)" % recipient)
        ret = GenericHttp.SmsDriver.sendOneLowLevel(self, message, recipient)
        arr = ret.split("\n")[0].split(" ", 1)
        if arr[0].startswith("OK"):
            mid = arr[1].split(":")[-1]
            debug("SMS(SmsGlobal) sent to %s with ID: %s" % (recipient, mid))
            return SmsDeliveryStatus(message, recipient = recipient, despatched = True, mid = mid)
        else:
            debug("SMS(SmsGlobal) failed to %s: %s" % (recipient, ret))
            return SmsDeliveryStatus(message, recipient = recipient, despatched = False, comment = ret)
