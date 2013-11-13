import sys
from thialfi import settings
from thialfi.logger import *
from twilio.rest import TwilioRestClient

__all__ = []
client = TwilioRestClient(settings.TWILIO_SID, settings.TWILIO_TOKEN)

__all__.append('make_call')
def make_call(to, url):
    debug("calling: %s (url: %s)" % (to, url))
    call = client.calls.create(from_ = settings.TWILIO_FROM, to = to, url = url)
    debug("call-result: %s %s %s %s %s %s" % (call.start_time, call.duration, call.sid, call.from_, call.to, call.status))
    return call

__all__.append('list_calls')
def list_calls(**kwargs):
    calls = client.calls.list(**kwargs)
    debug("thialfi.list(): Found %d calls..." % len(calls))
    for call in calls:
        debug("call: %s %s %s %s %s %s" % (call.start_time, call.duration, call.sid, call.from_, call.to, call.status))
    return calls

if __name__ == "__main__":
    make_call("+64210742741", "http://tmp.logix.cz/voice.xml")
