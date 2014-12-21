from django.conf import settings
from django.conf.urls import patterns, url

urlpatterns = patterns(
    'dapi.views',
    url(r'^$', 'index'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/$', 'dap'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/stable/$', 'dap_stable'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/devel/$', 'dap_devel'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/(?P<version>([0-9]|[1-9][0-9]*)(\.([0-9]|[1-9][0-9]*))*(dev|a|b)?)/$', 'dap_version'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/(?P<version>([0-9]|[1-9][0-9]*)(\.([0-9]|[1-9][0-9]*))*(dev|a|b)?)/delete/$', 'dap_version_delete'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/admin/$', 'dap_admin'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/leave/$', 'dap_leave'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/tags/$', 'dap_tags'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/report/$', 'dap_report'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/reports/$', 'dap_reports'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/rank/(?P<rank>[0-5])/$', 'dap_rank'),
    url(r'^report-toggle/(?P<report_id>[0-9]+)/$', 'report_toggle_solve'),
    url(r'^user/(?P<user>[^/]+)/$', 'user'),
    url(r'^user/(?P<user>[^/]+)/edit/$', 'user_edit'),
    url(r'^upload/$', 'upload'),
    url(r'^login/$', 'login'),
    url(r'^terms/$', 'terms'),
    url(r'^logout/$', 'logout'),
    url(r'^all/$', 'all'),
    url(r'^tag/(?P<tag>[^/]+)/$', 'tag'),
)

if settings.DEBUG:
    urlpatterns += patterns(
        '',
        (r'^download/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),
    )
