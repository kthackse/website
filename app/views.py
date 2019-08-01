import os

from django.contrib.auth.decorators import login_required
from django.http import (
    HttpResponseRedirect,
    StreamingHttpResponse,
    HttpResponseNotFound,
)
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.urls import reverse

from app import settings
from event.utils import (
    get_next_or_past_event,
    get_next_events,
    get_application_by_resume,
)
from user.enums import UserType
from user.utils import get_user_by_picture


def files(request, file_):
    path, file_name = os.path.split(file_)
    if request.user.is_authenticated:
        if path in [
            "user/picture",
            "__sized__/user/picture",
        ]:
            user = get_user_by_picture(picture=file_name)
            if file_name in ["profile.png", "profile-crop-c0-5__0-5-500x500.png"] or (user and (
                    request.user.type
                    in [UserType.ORGANISER.value, UserType.VOLUNTEER.value, UserType.MENTOR.value]
                    or user.picture_public_participants
                    and request.user.type == UserType.PARTICIPANT.value
                    or user.picture_public_sponsors_and_recruiters
                    and request.user.type
                    in [UserType.SPONSOR.value, UserType.RECRUITER.value]
                    or user == request.user)
            ):
                if file_[:7] != "/files/":
                    file_ = "/files/" + file_
                response = StreamingHttpResponse(open(settings.BASE_DIR + file_, "rb"))
                response["Content-Type"] = ""
                return response
        elif path[: path.rfind("/")] in ["/files/event/resume", "event/resume"]:
            application = get_application_by_resume(resume=file_)
            if application and (
                request.user.type
                in [UserType.ORGANISER.value, UserType.VOLUNTEER.value]
                or application.resume_available
                and request.user.type
                in [UserType.SPONSOR.value, UserType.RECRUITER.value]
                or application.user == request.user
            ):
                if file_[:7] != "/files/":
                    file_ = "/files/" + file_
                response = StreamingHttpResponse(open(settings.BASE_DIR + file_, "rb"))
                response["Content-Type"] = ""
                return response
        else:
            HttpResponseNotFound()
    if path in [
        "event/picture",
        "__sized__/event/picture",
        "event/picture",
        "event/background",
    ]:
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
        current_data["background_video"] = (event.background.name[-4:] == ".mp4")
        current_data["background_image"] = (event.background.name[-4:] in [".png", ".jpg", ".jpeg", ".gif", ".svg"])
        if event.custom_home:
            try:
                return render(request, "custom/" + event.code + "/index.html", current_data)
            except TemplateDoesNotExist:
                pass
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
