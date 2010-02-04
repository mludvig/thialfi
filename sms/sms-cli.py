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
import logging

from optparse import OptionParser
from logging import debug, info, warning, error

from Sms.Config import Config
from Sms.Sender import SmsSender

## Parse command line options
default_verbosity = Config().verbosity
optparser = OptionParser()
optparser.set_defaults(verbosity = default_verbosity)

optparser.add_option(      "--debug", dest="verbosity", action="store_const", const=logging.DEBUG, help="Enable debug output.")
optparser.add_option(      "--quiet", dest="verbosity", action="store_const", const=logging.WARNING, help="Suppres most messages. Only Warnings and Errors are printed.")
optparser.add_option(      "--dump-config", dest="dump_config", action="store_true", help="Dump current configuration after parsing config files and command line options and exit.")
optparser.add_option("-r", "--recipient", dest="sms_recipients", action="append", metavar="PHONE-NUM", help="Cell phone number of message recipient. Can be used multiple times.")
optparser.add_option("-m", "--message", dest="message", action="store", metavar="MESSAGE", help="Message to send to given Recipient(s)")

(options, args) = optparser.parse_args()

## Create config object
cfg = Config()

## And again some logging level adjustments
## according to configfile and command line parameters
if options.verbosity != default_verbosity:
	cfg.verbosity = options.verbosity

## Initialise settings
cfg.update_option("sms_engine", settings.SMS_ENGINE)
cfg.update_option("sms_url_pattern", settings.SMS_URL_PATTERN)

## Update Config with other parameters
for option in cfg.option_list():
	try:
		if getattr(options, option) != None:
			debug("Updating %s -> %s" % (option, getattr(options, option)))
			cfg.update_option(option, getattr(options, option))
	except AttributeError:
		## Some Config() options are not settable from command line
		pass

logging.root.setLevel(cfg.verbosity)

if not options.message or not cfg.sms_recipients:
	sys.stderr.write('Message and at least one recipient must be set!\n')
	sys.exit(1)

sms = SmsSender(cfg.sms_recipients)
sms.send(options.message)
