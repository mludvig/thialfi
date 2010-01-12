import django.shortcuts
import django.http

from django.template import RequestContext
from django.conf import settings

from exceptions import *

def render_template(request, *args, **kwargs):
	"""
	render_template(request, *args, **kwargs)

	Wrapper around django.shortcuts.render_to_response()
	that always adds RequestContext parameter
	"""
	## Add RequestContext to arguments
	kwargs.update(context_instance = RequestContext(request))
	## Add settings.MEDIA_REV to Context
	if len(args) > 1:
		args[1].update(MEDIA_REV = settings.MEDIA_REV)
	else:
		args.append({'MEDIA_REV' : settings.MEDIA_REV})
	return django.shortcuts.render_to_response(*args, **kwargs)

def get_object_or_404(*args, **kwargs):
	verbose_object_id = kwargs.has_key('verbose_object_id') and kwargs.pop('verbose_object_id') or ""

	try:
		return django.shortcuts.get_object_or_404(*args, **kwargs)
	except django.http.Http404, e:
		raise exceptions.Http404(id = verbose_object_id)

