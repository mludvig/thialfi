## Michal Ludvig <mludvig@logix.net.nz>
## http://www.logix.cz/michal/devel/sms-cli
## License: GPL Version 2

from sms.Exceptions import *
from sms.GenericSmsDriver import GenericSmsDriver

class SmsDriver(GenericSmsDriver):
    def __init__(self, options = {}):
        GenericSmsDriver.__init__(self, options)
