import os

from django.contrib import messages
from django.http import (
    HttpResponseRedirect,
    StreamingHttpResponse,
    HttpResponseNotFound,
    HttpResponse,
)
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

from app import settings
from app.utils import login_verified_required
from event.enums import CompanyTier
from event.utils import (
    get_next_or_past_event,
    get_next_events,
    get_application_by_resume,
    get_faq_items,
    add_subscriber,
    get_partners_in_event,
    get_sponsors_in_event,
    get_invoice_by_invoice,
)
from user.enums import UserType
from user.utils import get_user_by_picture, get_organisers


def files(request, file_):
    path, file_name = os.path.split(file_)
    if request.user.is_authenticated:
        if path in ["user/picture", "__sized__/user/picture"]:
            user = get_user_by_picture(picture=file_name)
            if file_name in ["profile.png", "profile-crop-c0-5__0-5-500x500.png"] or (
                user
                and (
                    request.user.type
                    in [
                        UserType.ORGANISER.value,
                        UserType.VOLUNTEER.value,
                        UserType.MENTOR.value,
                    ]
                    or user.picture_public_participants
                    and request.user.type == UserType.PARTICIPANT.value
                    or user.picture_public_sponsors_and_recruiters
                    and request.user.type
                    in [UserType.SPONSOR.value, UserType.RECRUITER.value]
                    or user == request.user
                )
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
        elif path in ["/files/invoice", "invoice"]:
            invoice = get_invoice_by_invoice(invoice=file_)
            if invoice and (
                request.user.is_sponsorship
                or request.user.company == invoice.company_event.company
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
        "event/background",
        "user/company",
    ]:
        if file_[:7] != "/files/":
            file_ = "/files/" + file_
        response = StreamingHttpResponse(open(settings.BASE_DIR + file_, "rb"))
        response["Content-Type"] = ""
        return response
    else:
        HttpResponseNotFound()
    return HttpResponseRedirect("%s?next=%s" % (reverse("user_login"), request.path))


def home(request):
    current_data = dict()
    event = get_next_or_past_event()
    if request.method == "POST" and "email" in request.POST:
        email = request.POST["email"]
        if not email:
            messages.add_message(
                request, messages.ERROR, "You need to enter a valid email!"
            )
        else:
            current_data["subscriber"] = add_subscriber(
                email=email, event=event, request=request
            )
    if event:
        current_data["event"] = event
        current_data["faq"] = get_faq_items(event_id=event.id)
        current_data["organisers"] = get_organisers(event_id=event.id)
        sponsors = get_sponsors_in_event(event_id=event.id)
        if sponsors:
            sponsors_dict = dict()
            for tier in CompanyTier:
                sponsors_dict[tier.name.lower()] = sponsors.filter(tier=tier.value)
            current_data["sponsors"] = sponsors_dict
        current_data["partners"] = get_partners_in_event(event_id=event.id)
        current_data["background_video"] = event.background.name[-4:] == ".mp4"
        current_data["background_image"] = event.background.name[-4:] in [
            ".png",
            ".jpg",
            ".jpeg",
            ".gif",
            ".svg",
        ]
        if event.custom_home:
            try:
                return render(
                    request, "custom/" + event.code + "/index.html", current_data
                )
            except TemplateDoesNotExist:
                pass
    return render(request, "home.html", current_data)


@login_verified_required
def dashboard(request):
    events = get_next_events()
    return render(request, "dashboard.html", {"events": events})


def redirect_to(request):
    try:
        return request.headers["Referer"]
    except KeyError:
        return reverse("app_home")


@csrf_exempt
def deploy(request):
    return HttpResponse("pong")
