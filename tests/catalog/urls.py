from django.conf.urls import url

from . import views


urlpatterns = [
    url(r'^(?P<path>[a-z0-9/_-]+)/$', views.Catalog.as_view(), name='router'),
    url(r'', views.Catalog.as_view(), name='router')
]