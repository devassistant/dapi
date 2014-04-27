from django.conf.urls import patterns, include, url
from rest_framework import routers
from dapi import views
from django.contrib import admin


admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'metadaps', views.MetaDapViewSet)
router.register(r'daps', views.DapViewSet)

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('dapi.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^search/', include('haystack.urls')),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/search/', views.SearchView.as_view(), name='search'),
    url(r'^api/', include(router.urls)),
)
