import os

from django.http import (
    HttpResponseRedirect,
    StreamingHttpResponse,
    HttpResponseNotFound,
)
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from user.enums import UserType
from user.models import User


def files(request, file_):
    path, file_name = os.path.split(file_)
    path_splitted = path.split("/")
    downloadable_path = None
    if request.user.is_authenticated:
        if len(path_splitted) > 0 and path_splitted[0] == "user":
            if len(path_splitted) > 1 and path_splitted[1] == "picture":
                user = get_object_or_404(User, picture=file_)
                if (
                    not user.picture_public_participants
                    and request.user.type == UserType.PARTICIPANT.value
                ):
                    HttpResponseNotFound()
                if (
                    not user.picture_public_sponsors_and_recruiters
                    and request.user.type
                    in [UserType.SPONSOR.value, UserType.RECRUITER.value]
                ):
                    HttpResponseNotFound()
                downloadable_path = user.picture.path
        if downloadable_path:
            response = StreamingHttpResponse(open(downloadable_path, "rb"))
            response["Content-Type"] = ""
            return response
        else:
            HttpResponseNotFound()
    return HttpResponseRedirect(reverse("user_login"))


def home(request):
    return render(request, "home.html")


def redirect_to(request):
    try:
        return request.headers["Referer"]
    except KeyError:
        return reverse("app_home")
