from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
	(r'^$', 'app.views.index'),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    ## Serve static files only in debug mode
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.PROJECT_ROOT + '/doc_root/static'}),
    )

