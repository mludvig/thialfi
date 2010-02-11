# Django settings for thialfi project.

## -- Python Setup -- ##
import os.path
import sys

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, '..'))

### Figure out media revision to avoid caching problems
#try:
#	print "MEDIA_REV=%s (cached)" % MEDIA_REV
#except:
#	try:
#		MEDIA_REV = os.popen("/usr/bin/hg identify -i").readline().strip()
#	except:
#		import datetime
#		MEDIA_REV = datetime.datetime.now().strftime("%s")
#	print "MEDIA_REV=%s" % MEDIA_REV
MEDIA_REV="fixme"

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'              # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'thialfi'              # Or path to database file if using sqlite3.
DATABASE_USER = 'thialfi'              # Not used with sqlite3.
DATABASE_PASSWORD = 'thialfi'     # Not used with sqlite3.
DATABASE_HOST = 'localhost' # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

RCPT_DOMAIN = "sms.your.domain"

SMS_ENGINE = "GwClickatell"		# Only Clickatell is supported for now
# Fill in APIID, USERNAME and PASSWORD of your Clickatell account
SMS_AUTH_DATA = "api_id=APIID&user=USERNAME&password=PASSWORD"
# Don't change the following SMS_* settings 
SMS_SEND_PATTERN = "https://api.clickatell.com/http/sendmsg?%(auth)s&to=%(recipient)s&text=%(message)s&concat=3&escalate=1&queue=1"
SMS_STATUS_PATTERN = "https://api.clickatell.com/http/querymsg?%(auth)s&apimsgid=%(messageid)s"

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Pacific/Auckland'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-nz'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = ''

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = ''

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'mzgp$h^)fq8k4_75j)i^mzkvh-#8eeh987a0d7!zcetq4(c&g3'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
	PROJECT_ROOT+'/templates',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
	'django.contrib.admin',
	'app',
)

from settings_local import *
