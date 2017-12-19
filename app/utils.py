import django.shortcuts
import django.http

from django.template import RequestContext
from django.conf import settings

from exceptions import *

def render_template(request, *args, **kwargs):
    """
    render_template(request, *args, **kwargs)

    Wrapper around django.shortcuts.render()
    that always adds MEDIA_REV parameter
    """
    ## Add settings.MEDIA_REV to Context
    if len(args) > 1:
        args[1].update(MEDIA_REV = settings.MEDIA_REV)
    else:
        ## Convert from tuple to list and add list member
        args = [ args[0], {'MEDIA_REV' : settings.MEDIA_REV} ]
    return django.shortcuts.render(request, *args, **kwargs)

def get_object_or_404(*args, **kwargs):
    verbose_object_id = kwargs.has_key('verbose_object_id') and kwargs.pop('verbose_object_id') or ""

    try:
        return django.shortcuts.get_object_or_404(*args, **kwargs)
    except django.http.Http404, e:
        raise exceptions.Http404(id = verbose_object_id)

