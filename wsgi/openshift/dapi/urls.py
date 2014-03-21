from django.conf.urls import patterns, url

urlpatterns = patterns('dapi.views',
    url(r'^$', 'index'),
    url(r'^dap/(?P<dap>[a-z][a-z0-9\-_]*[a-z0-9]|[a-z])/$', 'dap'),
)
