import os

from django.http import (
    HttpResponseRedirect,
    StreamingHttpResponse,
    HttpResponseNotFound,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from app import settings
from event.models import Event
from event.utils import get_next_or_past_event
from user.enums import UserType
from user.models import User


def files(request, file_):
    path, file_name = os.path.split(file_)
    if request.user.is_authenticated:
        if path in ["/files/user/picture", "/files/__sized__/user/picture"]:
            response = StreamingHttpResponse(open(settings.BASE_DIR + file_, "rb"))
            response["Content-Type"] = ""
            return response
        else:
            HttpResponseNotFound()
    else:
        if path in ["/files/event/picture", "/files/__sized__/event/picture"]:
            response = StreamingHttpResponse(open(settings.BASE_DIR + file_, "rb"))
            response["Content-Type"] = ""
            return response
        else:
            HttpResponseNotFound()
    return HttpResponseRedirect(reverse("user_login"))


def home(request):
    current_data = dict()
    event = get_next_or_past_event()
    if event:
        current_data["event"] = event
        if event.custom_home:
            return render(request, "custom/" + event.code + "/index.html", current_data)
    return render(request, "home.html", current_data)


def redirect_to(request):
    try:
        return request.headers["Referer"]
    except KeyError:
        return reverse("app_home")
