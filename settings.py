# Django settings for thialfi project.

## -- Python Setup -- ##
from os import getenv as os_getenv
import os.path
import sys

import dj_database_url

def force_getenv(var_name):
    var_value = os_getenv(var_name)
    if var_value == None:
        raise Exception("Environ variable $%s not set" % var_name)
    return var_value

PROJECT_ROOT = os.path.dirname(__file__)
sys.path.insert(0, PROJECT_ROOT)
sys.path.insert(0, os.path.join(PROJECT_ROOT, '..'))

### Figure out media revision to avoid caching problems
#try:
#    print "MEDIA_REV=%s (cached)" % MEDIA_REV
#except:
#    try:
#        MEDIA_REV = os.popen("/usr/bin/hg identify -i").readline().strip()
#    except:
#        import datetime
#        MEDIA_REV = datetime.datetime.now().strftime("%s")
#    print "MEDIA_REV=%s" % MEDIA_REV
MEDIA_REV="fixme"

DEBUG = True

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

# Configure database from $DATABASE_URL:
DATABASES = {
    'default': dj_database_url.config(default=force_getenv('DATABASE_URL'), conn_max_age=600)
}

RCPT_DOMAIN = force_getenv('RCPT_DOMAIN')

VOICE_URL = "https://" + RCPT_DOMAIN + "/%(path)s"

ALLOWED_HOSTS = [ RCPT_DOMAIN ]

## SMS Engine setup
SMS_ENGINE = "MessageMedia"
# Various engines may have different options.
SMS_ENGINE_OPTIONS = { "username": "abc123", "password": "Blah Blah" }

# How many messages in a given timeframe can be passed through?
# Excess messages will be ignored
# E.g. to only pass through 5 messages every 15 minutes per Recipient
#    RECENT_MINUTES = 15
#    RECENT_MESSAGES = 5
RECENT_MINUTES = 15
RECENT_MESSAGES = 5

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
USE_L10N = False

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
ADMIN_MEDIA_PREFIX = '/media/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'mzgp$h^)fq8k4_75j)i^mzkvh-#8eeh987a0d7!zcetq4(c&g3'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            PROJECT_ROOT+'/templates',
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'app',
)

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Pacific/Auckland'
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'

from settings_local import *
