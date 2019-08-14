from django.conf.urls import url

from event import views

urlpatterns = [
    url(r"^(?P<code>.*)/apply$", views.apply, name="event_apply"),
    url(r"^(?P<code>.*)/applications$", views.applications, name="event_applications"),
    url(r"^subscribe/(?P<id>[\w-]+)$", views.subscribe, name="event_subscribe"),
    url(r"^unsubscribe/(?P<id>[\w-]+)$", views.unsubscribe, name="event_unsubscribe"),
]
