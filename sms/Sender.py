## Michal Ludvig <mludvig@logix.net.nz>
## http://www.logix.cz/michal/devel/sms-cli
## License: GPL Version 2

from django.conf import settings

from sms.Exceptions import *
from sms.SimpleObjects import SmsDeliveryStatus

from logger import *

class SmsSender(object):
    def __init__(self, recipients = [], engine_options = {}, **kwargs):
        assert(type(recipients) == type([]))
        debug("Importing engine: %s" % settings.SMS_ENGINE)
        driver_module = __import__("sms.Engines." + settings.SMS_ENGINE, fromlist = ["sms.Engines"])
        self._driver = driver_module.SmsDriver(options = settings.SMS_ENGINE_OPTIONS, **kwargs)

    def send(self, message):
        return self._driver.send(message)

    def receive(self, senders = [], in_reply_to = [], keep = False):
        assert(type(senders) == list)
        assert(type(in_reply_to) == list)

        if 'receive' not in dir(self._driver):
            raise SmsError(message = "Not implemented in engine: %s" % self._driver.__module__)

        return self._driver.receive(senders = senders, in_reply_to = in_reply_to, keep = keep)

    def get_status(self, mids = [], keep = False):
        if 'get_status' not in dir(self._driver):
            raise SmsError(message = "Not implemented in engine: %s" % self._driver.__module__)

        return self._driver.get_status(mids = mids, keep = keep)
