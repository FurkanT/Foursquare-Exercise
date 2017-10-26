from django.conf.urls import url
from django.contrib.auth import views as auth_views
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    url(r'^change-email/$', views.change_email, name='change_email'),
    url(r'^upload-image/$', views.upload_image, name='upload_image'),
    url(r'^password/$', views.change_password, name='change_password'),
    url(r'^birthday-page/$', TemplateView.as_view(template_name="foursquare/birthdaypage.html"), name='birthday'),
    url(r'^delete-user/(?P<pk>\d+)/$', views.delete_user, name='delete_user'),
    url(r'^signup/$', views.register, name='signup'),
    url(r'^$', views.search, name='search'),
    url(r'delete/(?P<pk>\d+)/$', views.SearchQueryDelete.as_view(), name='delete_entry'),
    url(r'^login/$', auth_views.login, {'template_name': 'foursquare/login.html'}, name='login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/'}, name='logout'),
]
