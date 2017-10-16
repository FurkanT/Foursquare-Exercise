from django.conf.urls import url

from . import views

urlpatterns = [

    # url(r'(?P<search_id>[0-9]+)/$', views.searchshortcut, name='searchById'),
    url(r'^$', views.search, name='search'),
    
]
