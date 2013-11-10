from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'app.views.index', { 'template' : 'thialfi/index.html' }),
    (r'^detail/(?P<message_id>\d+)/$', 'app.views.detail', { 'template' : 'thialfi/detail.html' }),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    ## Serve static files only in debug mode
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.PROJECT_ROOT + '/doc_root/static'}),
    )

