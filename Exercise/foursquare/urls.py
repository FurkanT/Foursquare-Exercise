from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [

    url(r'^signup/$', views.register, name='signup'),
    # url(r'(?P<search_id>[0-9]+)/$', views.searchshortcut, name='searchById'),
    url(r'^$', views.search, name='search'),
    url(r'^login/$', auth_views.login, {'template_name': 'foursquare/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
