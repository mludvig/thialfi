from django.conf.urls import url
from django.conf import settings
from django.contrib import admin
import app.views

admin.autodiscover()

urlpatterns = [
    url(r'^$', app.views.index, { 'template' : 'thialfi/index.html' }, name = "views_index"),
    url(r'^messages/$', app.views.messages, { 'template' : 'thialfi/messages.html' }, name = "views_messages"),
    url(r'^detail/(?P<message_id>\d+)/$', app.views.detail, { 'template' : 'thialfi/detail.html' }, name = "views_detail"),
    url(r'^group/(?P<group_id>\d+)/$', app.views.group, { 'template' : 'thialfi/group.html' }, name = "views_group"),
    url(r'^tw/(?P<phonecall_id>\w+)/$', app.views.twilio, { 'template' : 'thialfi/twilio.xml' }, name = "views_twilio"),
    url(r'^report.csv$', app.views.report_csv, { 'template' : 'thialfi/report.csv' }),
    url(r'^admin/', admin.site.urls),
]

if settings.DEBUG:
    ## Serve static files only in debug mode
    import django.views.static
    urlpatterns.append(
        url(r'^static/(?P<path>.*)$', django.views.static.serve, {'document_root': settings.PROJECT_ROOT + '/doc_root/static'}),
    )

