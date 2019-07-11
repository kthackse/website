from django.conf.urls import url
from django.contrib import admin
from django.urls import include

from app import views

urlpatterns = [
    url("admin/", admin.site.urls),
    url(r"^user/", include("user.urls")),
    url(r"^$", views.root, name="app_root"),
]
