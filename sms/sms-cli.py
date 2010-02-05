#!/usr/bin/env python

# sms-cli.py - SMS sender command line client
# Michal Ludvig <mludvig@logix.net.nz>

## -- Python Setup -- ##
import os.path
import sys

PROJECT_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, '..'))

## -- Django Setup -- ##
from django.core.management import setup_environ
from thialfi import settings
setup_environ(settings)

## -- Here comes the script -- ##
import os
import sys

import datetime

from optparse import OptionParser

from Sms.Sender import SmsSender

## Parse command line options
optparser = OptionParser()

optparser.add_option("-r", "--recipient", dest="sms_recipients", action="append", metavar="PHONE-NUM", help="Cell phone number of message recipient. Can be used multiple times.")
optparser.add_option("-m", "--message", dest="message", action="store", metavar="MESSAGE", help="Message to send to given Recipient(s)")

(options, args) = optparser.parse_args()

if not options.message or not options.sms_recipients:
	sys.stderr.write('Message and at least one recipient must be set!\n')
	sys.exit(1)

sms = SmsSender()
for recipient in options.sms_recipients:
	print sms.send(options.message, recipient)
