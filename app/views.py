import hmac
import json
import os
import subprocess
from _sha1 import sha1
from ipaddress import ip_address, ip_network

import requests
from django.contrib import messages
from django.http import (
    HttpResponseRedirect,
    StreamingHttpResponse,
    HttpResponseNotFound,
)
from django.shortcuts import render
from django.template import TemplateDoesNotExist
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from app import settings
from app.models import FileVerified
from app.settings import GH_KEY, GH_BRANCH
from app.slack import send_deploy_message
from app.utils import login_verified_required
from event.enums import CompanyTier
from event.utils.messages import get_message_by_attachment
from event.utils.utils import (
    get_next_or_past_event,
    get_application_by_resume,
    get_faq_items,
    add_subscriber,
    get_partners_in_event,
    get_sponsors_in_event,
    get_invoice_by_invoice,
    create_team,
    assign_team,
    get_teammates_by_user,
    deassign_team,
    remove_team,
    get_organisers_in_event,
    get_statistics,
    get_messages_for_user,
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
        elif path in ["/files/event/attachment", "event/attachment"]:
            message = get_message_by_attachment(attachment=file_)
            if message and (
                request.user.id == message.recipient_id
                or request.user.email == message.recipient_email
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
        "event/company",
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
        current_data["event_organisers"] = get_organisers_in_event(event_id=event.id)
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
def dashboard(request, context={}):
    if request.method == "POST":
        if request.POST["submit"] == "team-create":
            if "name" in request.POST and request.POST["name"]:
                team = create_team(
                    request.POST["event"], request.user.id, request.POST["name"]
                )
                assign_team(request.POST["event"], request.user.id, team.code)
                messages.success(request, "Your team has been created!")
            else:
                messages.error(request, "You must give a name to the team!")
        elif request.POST["submit"] == "team-join":
            if assign_team(
                request.POST["event"], request.user.id, request.POST["code"]
            ):
                messages.success(request, "You have joined the team!")
            else:
                messages.success(request, "Team is full or doesn't exist!")
        elif request.POST["submit"] == "team-leave":
            deassign_team(request.POST["event"], request.user.id)
            messages.success(request, "You have left the team!")
        elif request.POST["submit"] == "team-remove":
            remove_team(request.POST["event"], request.user.id, request.POST["team"])
            messages.success(request, "The team has been removed!")

    context["teammates"] = get_teammates_by_user(request.user.id)
    context["statistics"] = get_statistics()
    context["alerts"] = get_messages_for_user(request.user.id)
    return render(request, "dashboard.html", context)


def verify(request, context={}):
    if request.method == "POST":
        ip = get_client_ip(request)
        if FileVerified.objects.filter(ip=ip, verified_at__gte=(timezone.now()-timezone.timedelta(hours=1))).count() >= 10:
            messages.error(request, "You have verified or attempted to verify 10 documents in the last hour, please wait some time before trying again.")
        else:
            if "control" in request.POST and "verification" in request.POST:
                verication_control = request.POST["control"].replace(" ", "")
                verification_code = request.POST["verification"].replace(" ", "")
                if len(verication_control) == 8 and len(verification_code) == 32:
                    file_verified = FileVerified(ip=ip, verification_control=verication_control, verification_code=verification_code)
                    file_verified.save()
                    if file_verified.file:
                        return render(request, "verify.html", context)
                    else:
                        messages.error(request, "The data control and verification numbers do not correspond to any valid document.")
                else:
                    messages.error(request, "The data control and verification numbers are not valid.")
            else:
                messages.error(request, "The data control and verification numbers do not correspond to any valid document.")
    return render(request, "verify.html", context)


def get_client_ip(request):
    """
    Stack Overflow
    How do I get user IP address in django?
    https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def redirect_to(request):
    try:
        return request.headers["Referer"]
    except KeyError:
        return reverse("app_home")


@require_POST
@csrf_exempt
def deploy(request):
    forwarded_for = u"{}".format(request.META.get("HTTP_X_FORWARDED_FOR"))
    client_ip_address = ip_address(forwarded_for)
    whitelist = requests.get("https://api.github.com/meta").json()["hooks"]

    for valid_ip in whitelist:
        if client_ip_address in ip_network(valid_ip):
            break
    else:
        return response(request, code=500)

    header_signature = request.META.get("HTTP_X_HUB_SIGNATURE")
    if header_signature is None:
        return response(request, code=500)

    sha_name, signature = header_signature.split("=")
    if sha_name != "sha1":
        return response(request, code=501)

    mac = hmac.new(force_bytes(GH_KEY), msg=force_bytes(request.body), digestmod=sha1)
    if not hmac.compare_digest(force_bytes(mac.hexdigest()), force_bytes(signature)):
        return response(request, code=500)

    event = request.META.get("HTTP_X_GITHUB_EVENT")
    if event == "push":
        data = json.loads(request.body.decode("utf-8"))
        # Deploy if push to the current branch
        if data["ref"] == "refs/heads/" + GH_BRANCH:
            try:
                subprocess.call(
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "../deploy.sh"
                    )
                )
                send_deploy_message(data, succedded=True)
            except OSError:
                send_deploy_message(data, succedded=False)
            return response(request, code=200)
    return response(request, code=204)


def response(request, *args, code: int, message: str = None, **kwargs):
    response_result = render(request, "response.html", dict(code=code, message=message))
    response_result.status_code = code
    return response_result


def response_400(request, *args, **kwargs):
    return response(request, *args, code=404, *kwargs)


def response_403(request, *args, **kwargs):
    return response(request, *args, code=404, *kwargs)


def response_404(request, *args, **kwargs):
    return response(request, *args, code=404, *kwargs)


def response_500(request, *args, **kwargs):
    return response(request, *args, code=404, *kwargs)
