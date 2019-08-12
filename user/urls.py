from django.conf.urls import url

from user import views

urlpatterns = [
    url(r'^login/$', views.login, name='user_login'),
    url(r'^signup/$', views.signup, name='user_signup'),
    url(r'^logout/$', views.logout, name='user_logout'),
    url(r'^profile/$', views.profile, name='user_profile'),
    url(r'^profile/(?P<id>[\w-]+)$', views.profile_other, name='user_profileother'),
    url(r'^verify/$', views.verify, name='user_verify'),
    url(r'^verify/(?P<verification_key>.+)$', views.verify_key, name='user_verifykey'),
    url(r'^send-verification/$', views.send_verification, name='user_sendverification'),
    url(r'^download-personal-data/$', views.download_personal_data, name='user_downloadpersonaldata'),
    url(r'^deactivate/$', views.deactivate, name='user_deactivate'),
]
