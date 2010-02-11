## Author: Michal Ludvig <michal@logix.cz>
##         http://www.logix.cz/michal
## License: GPL Version 2

from django.conf import settings

import re

class Config(object):
	_instance = None
	_parsed_files = []

	sms_engine = settings.SMS_ENGINE
	#sms_send_pattern = settings.SMS_SEND_PATTERN % { 'auth' : settings.SMS_AUTH_DATA }
	#sms_status_pattern = settings.SMS_STATUS_PATTERN % { 'auth' : settings.SMS_AUTH_DATA }
	sms_send_pattern = settings.SMS_SEND_PATTERN.replace("%(auth)s", settings.SMS_AUTH_DATA)
	sms_status_pattern = settings.SMS_STATUS_PATTERN.replace("%(auth)s", settings.SMS_AUTH_DATA)
	sms_timestamp_format = "%m/%d %H:%M"
	## Example config for Clickatell:
	## sms_engine = "Sms.GwClickatell"
	## sms_send_pattern = "https://api.clickatell.com/http/sendmsg?api_id=APIID&user=USERNAME&password=PASSWORD&to=%(recipient)s&text=%(message)s"
	## sms_query_pattern = "https://api.clickatell.com/http/querymsg?api_id=APIID&user=USERNAME&password=PASSWORD&apimsgid=%(messageid)s"
	## replace APIID, USERNAME and PASSWORD with the values of your Clickatell account

	## Creating a singleton
	def __new__(self, configfile = None):
		if self._instance is None:
			self._instance = object.__new__(self)
		return self._instance

	def __init__(self, configfile = None):
		if configfile:
			self.read_config_file(configfile)

	def option_list(self):
		retval = []
		for option in dir(self):
			## Skip attributes that start with underscore or are not string, int or bool
			option_type = type(getattr(Config, option))
			if option.startswith("_") or \
			   not (option_type in (
			   		type("string"),	# str
			        	type(42),	# int
					type(True),	# bool
					type([]))):	# list
				continue
			retval.append(option)
		return retval

	def update_option(self, option, value):
		if value is None:
			return
		#### Special treatment of some options
		## allow yes/no, true/false, on/off and 1/0 for boolean options
		elif type(getattr(Config, option)) is type(True):	# bool
			if str(value).lower() in ("true", "yes", "on", "1"):
				setattr(Config, option, True)
			elif str(value).lower() in ("false", "no", "off", "0"):
				setattr(Config, option, False)
			else:
				print("Config: value of option '%s' must be Yes or No, not '%s'" % (option, value))
		elif type(getattr(Config, option)) is type(42):		# int
			try:
				setattr(Config, option, int(value))
			except ValueError, e:
				print("Config: value of option '%s' must be an integer, not '%s'" % (option, value))
		else:							# string
			setattr(Config, option, value)

