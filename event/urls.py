from django.conf.urls import url

from event import views

urlpatterns = [
    url(r"^(?P<code>.*)/apply$", views.apply, name="event_apply"),
    url(r"^(?P<code>.*)/apply/remove$", views.apply_remove, name="event_applyremove"),
    url(
        r"^(?P<code>.*)/apply/remove/confirm$",
        views.apply_remove_confirm,
        name="event_applyremoveconfirm",
    ),
    url(r"^(?P<code>.*)/applications$", views.applications, name="event_applications"),
    url(r"^(?P<code>.*)/applications/review$", views.applications_review, name="event_applicationsreview"),
    url(r"^(?P<code>.*)/live$", views.live, name="event_live"),
    url(r"^subscribe/(?P<id>[\w-]+)$", views.subscribe, name="event_subscribe"),
    url(r"^unsubscribe/(?P<id>[\w-]+)$", views.unsubscribe, name="event_unsubscribe"),
]
