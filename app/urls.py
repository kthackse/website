from django.conf.urls import url
from django.contrib import admin
from django.urls import include

from app import views

urlpatterns = [
    url("admin/", admin.site.urls),
    url(r"^djga/", include("google_analytics.urls")),
    url(r"^user/", include("user.urls")),
    url(r"^page/", include("page.urls")),
    url(r"^event/", include("event.urls")),
    url(r"^$", views.home, name="app_home"),
    url(r"^dashboard/$", views.dashboard, name="app_dashboard"),
    url(r'^files/(?P<file_>.*)$', views.files, name="app_files"),
]
