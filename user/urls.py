from django.conf.urls import url

from user import views

urlpatterns = [
    url(r'^login/$', views.login, name='user_login'),
    url(r'^signup/$', views.signup, name='user_signup'),
    url(r'^logout/$', views.logout, name='user_logout'),
    url(r'^profile/$', views.profile, name='user_profile'),
    url(r'^profile/(?P<id>[\w-]+)$', views.profile_other, name='user_profileother'),
]
