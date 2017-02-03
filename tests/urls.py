from django.conf.urls import url, include


urlpatterns = [
    url(r'', include('catalog.urls', namespace='catalog')),
]