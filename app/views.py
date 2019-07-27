import os

from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseRedirect,
    StreamingHttpResponse,
    HttpResponseNotFound,
)
from django.shortcuts import render
from django.urls import reverse

from app import settings
from event.utils import get_next_or_past_event, get_next_events, get_application_by_resume
from user.enums import UserType


def files(request, file_):
    path, file_name = os.path.split(file_)
    if request.user.is_authenticated:
        if path in ["/files/user/picture", "/files/__sized__/user/picture", "user/picture"]:
            if file_[:7] != "/files/":
                file_ = "/files/" + file_
            response = StreamingHttpResponse(open(settings.BASE_DIR + file_, "rb"))
            response["Content-Type"] = ""
            return response
        elif path[:path.rfind("/")] in ["/files/event/resume", "event/resume"]:
            application = get_application_by_resume(resume=file_)
            if request.user.type in [UserType.ORGANISER.value, UserType.VOLUNTERR.value] or application.resume_available and request.user.type in [UserType.SPONSOR.value, UserType.RECRUITER.value] or application.user == request.user:
                if file_[:7] != "/files/":
                    file_ = "/files/" + file_
                response = StreamingHttpResponse(open(settings.BASE_DIR + file_, "rb"))
                response["Content-Type"] = ""
                return response
        else:
            HttpResponseNotFound()
    if path in ["/files/event/picture", "/files/__sized__/event/picture", "event/picture"]:
        if file_[:7] != "/files/":
            file_ = "/files/" + file_
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


@login_required
def dashboard(request):
    events = get_next_events()
    return render(request, "dashboard.html", {"events": events})


def redirect_to(request):
    try:
        return request.headers["Referer"]
    except KeyError:
        return reverse("app_home")
