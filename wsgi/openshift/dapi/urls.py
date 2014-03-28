from django.conf.urls import patterns, url

urlpatterns = patterns('dapi.views',
    url(r'^$', 'index'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/$', 'dap'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/stable/$', 'dap_stable'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/devel/$', 'dap_devel'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/(?P<version>([0-9]|[1-9][0-9]*)(\.([0-9]|[1-9][0-9]*))*(dev|a|b)?)$', 'dap_version'),
    url(r'^user/(?P<user>[^/]+)/$', 'user'),
    url(r'^user/(?P<user>[^/]+)/edit/$', 'user_edit'),
    url(r'^upload/$', 'upload'),
    url(r'^login/$', 'login'),
    url(r'^logout/$', 'logout'),
)
