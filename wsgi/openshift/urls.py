from django.conf import settings
from django.conf.urls import patterns, include, url
from rest_framework import routers
from dapi import views
from dapi import forms
from django.contrib import admin
from haystack.forms import ModelSearchForm
from haystack.query import SearchQuerySet
from haystack.views import search_view_factory


router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'metadaps', views.MetaDapViewSet)
router.register(r'daps', views.DapViewSet)
router.register(r'search', views.SearchViewSet, base_name='search')
router.register(r'upload', views.UploadViewSet, base_name='upload')

urlpatterns = patterns(
    '',
    url(r'^', include('dapi.urls')),
    url('', include('social.apps.django_app.urls', namespace='social')),
    url(r'^captcha/', include('captcha.urls')),
    url(r'^api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/', include(router.urls)),
)


urlpatterns += patterns('haystack.views',
    url(r'^search/', search_view_factory(
        view_class=views.ExtraContextSearchView,
        form_class=forms.MetaDapSearchForm
    ), name='haystack_search'),
)


if settings.DEBUG:
    admin.autodiscover()
    urlpatterns += patterns(
        '',
        url(r'^admin/', include(admin.site.urls)),
    )
