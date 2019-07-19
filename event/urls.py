from django.conf.urls import url

from event import views

urlpatterns = [
    url(r'^(?P<code>.*)/apply$', views.apply, name="event_apply"),
]
