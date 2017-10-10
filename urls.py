from django.conf.urls.defaults import *
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', 'app.views.index', { 'template' : 'thialfi/index.html' }),
    (r'^messages/$', 'app.views.messages', { 'template' : 'thialfi/messages.html' }),
    (r'^detail/(?P<message_id>\d+)/$', 'app.views.detail', { 'template' : 'thialfi/detail.html' }),
    (r'^group/(?P<group_id>\d+)/$', 'app.views.group', { 'template' : 'thialfi/group.html' }),
    (r'^tw/(?P<phonecall_id>\w+)/$', 'app.views.twilio', { 'template' : 'thialfi/twilio.xml' }),
    (r'^report.csv$', 'app.views.report_csv', { 'template' : 'thialfi/report.csv' }),
    (r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
    ## Serve static files only in debug mode
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.PROJECT_ROOT + '/doc_root/static'}),
    )

