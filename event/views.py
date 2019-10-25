import math
import datetime

from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.template.loader import get_template
from django.urls import reverse
from django.utils import timezone
from pdf2image import convert_from_bytes

from app.models import FileSubmission
from app.processor import variables_processor
from app.utils import login_verified_required, get_substitutions_templates
from app.views import response
from event.enums import DietType, TshirtSize, ApplicationStatus, SubscriberStatus
from event.models import Application, Subscriber, Invoice, Letter
from event.utils.messages import get_message
from event.utils.utils import (
    get_event,
    get_application,
    get_applications,
    get_application_to_review,
    add_comment,
    get_comments_for_application,
    add_vote,
    get_application_by_id,
    get_ranking,
)
from user.utils import is_participant, is_organiser


@login_verified_required
@user_passes_test(is_participant)
def apply(request, code, context={}):
    current_event = get_event(code=code)
    if current_event:
        context["event"] = current_event
        context["years"] = [
            (current_event.starts_at.year + year, year == 0) for year in range(-1, 6)
        ]
        context["diets"] = [
            (diet.name.capitalize().replace("_", " "), diet.value) for diet in DietType
        ]
        context["tshirts"] = [
            (tshirt.name.upper(), tshirt.value) for tshirt in TshirtSize
        ]
        current_application = get_application(
            event_id=current_event.id, user_id=request.user.id
        )
        context["status"] = "DRAFT"
        if current_application:
            context["application"] = current_application
            context["tshirt_int"] = int(current_application.tshirt)
            if current_application.status in [
                ApplicationStatus.DRAFT.value,
                ApplicationStatus.PENDING.value,
                ApplicationStatus.CANCELLED.value,
                ApplicationStatus.INVITED.value,
                ApplicationStatus.CONFIRMED.value,
                ApplicationStatus.ATTENDED.value,
            ]:
                context["status"] = ApplicationStatus(
                    current_application.status
                ).name.upper()
            else:
                context["status"] = "PENDING"
        if (
            request.method == "POST"
            and not current_application
            or (
                current_application
                and current_application.status == ApplicationStatus.DRAFT.value
            )
        ):
            required_fields = [
                "university",
                "degree",
                "graduation_year",
                "description",
                "projects",
                "diet",
                "tshirt",
            ]
            all_filled = True
            for required_field in required_fields:
                if (
                    required_field not in request.POST
                    or not request.POST[required_field]
                ):
                    all_filled = False
            all_filled &= "resume" in request.FILES if not current_application else True
            if all_filled:
                # TODO: Display messages of error and validate URLs
                # TODO: Restrict resume to PDF
                university = request.POST["university"]
                degree = request.POST["degree"]
                graduation_year = request.POST["graduation_year"]
                description = request.POST["description"]
                projects = request.POST["projects"]
                github = request.POST["github"] if "github" in request.POST else ""
                devpost = request.POST["devpost"] if "devpost" in request.POST else ""
                linkedin = (
                    request.POST["linkedin"] if "linkedin" in request.POST else ""
                )
                website = request.POST["website"] if "website" in request.POST else ""
                resume = request.FILES["resume"] if "resume" in request.FILES else None
                resume_available = (
                    request.POST["resume_available"] == "on"
                    if "resume_available" in request.POST
                    else False
                )
                diet = request.POST["diet"]
                diet_other = (
                    request.POST["diet_other"] if "diet_other" in request.POST else ""
                )
                tshirt = request.POST["tshirt"]
                hardware = (
                    request.POST["hardware"] if "hardware" in request.POST else ""
                )
                status = (
                    ApplicationStatus.PENDING.value
                    if request.POST["submit"] == "apply"
                    else ApplicationStatus.DRAFT.value
                )
                if current_application:
                    application = current_application
                    application.description = description
                    application.projects = projects
                    if resume:
                        application.resume.delete()
                        application.resume = resume
                    application.resume_available = resume_available
                    application.university = university
                    application.degree = degree
                    application.graduation_year = graduation_year
                    application.github = github
                    application.devpost = devpost
                    application.linkedin = linkedin
                    application.website = website
                    application.diet = diet
                    application.diet_other = diet_other
                    application.tshirt = tshirt
                    application.hardware = hardware
                    application.status = status
                else:
                    application = Application(
                        event_id=current_event.id,
                        user_id=request.user.id,
                        description=description,
                        projects=projects,
                        resume=resume,
                        resume_available=resume_available,
                        university=university,
                        degree=degree,
                        graduation_year=graduation_year,
                        github=github,
                        devpost=devpost,
                        linkedin=linkedin,
                        website=website,
                        diet=diet,
                        diet_other=diet_other,
                        tshirt=tshirt,
                        hardware=hardware,
                        status=status,
                    )
                application.save()
                if application.status == ApplicationStatus.DRAFT.value:
                    messages.success(request, "Your application has been saved.")
                    return HttpResponseRedirect("")
                messages.success(request, "Your application has been submitted!")
                return HttpResponseRedirect(reverse("app_dashboard"))
        return render(request, "apply.html", context)
    return HttpResponseNotFound()


@login_verified_required
@user_passes_test(is_organiser)
def applications(request, code, context={}):
    # letter = Letter.objects.all().first()
    # response = HttpResponse(content_type='application/pdf')
    # response.write(letter.get_letter_file())
    # return response
    # template = get_template("file/letter/underage.html")
    # html = template.render(
    #     context=dict(
    #         letter=Letter.objects.first(),
    #         **variables_processor(request),
    #         verification_control="11468239",
    #         verification_code="B74709D2DAE84CB380B005390615A454"
    #     )
    # )
    # return HttpResponse(html)
    current_event = get_event(code=code, application_status=None)
    if current_event:
        context["event"] = current_event
        context["applications"] = get_applications(event_id=current_event.id)
        return render(request, "applications.html", context)
    return HttpResponseNotFound()


@login_verified_required
@user_passes_test(is_organiser)
def applications_review(request, code, context={}):
    current_event = get_event(code=code)
    if current_event:
        if request.method == "POST":
            if request.POST["submit"] == "comment":
                if request.POST["comment"]:
                    add_comment(
                        request.POST["application"],
                        request.user.id,
                        request.POST["comment"],
                    )
                    messages.success(
                        request,
                        "Your comment has been added successfully to the application.",
                    )
                else:
                    messages.error(request, "The comment cannot be empty!")
            elif request.POST["submit"] == "vote":
                if (
                    "vote-personal" not in request.POST
                    or request.POST["vote-personal"] == "-1"
                    or "vote-technical" not in request.POST
                    or request.POST["vote-technical"] == "-1"
                ):
                    messages.error(
                        request, "You need to vote both personal and technical skills!"
                    )
                else:
                    add_vote(
                        request.POST["application"],
                        request.user.id,
                        int(request.POST["vote-personal"]),
                        int(request.POST["vote-technical"]),
                    )
        context["event"] = current_event
        application = get_application_to_review(
            event_id=current_event.id, user_id=request.user.id
        )
        context["application"] = application
        if application:
            context["comments"] = get_comments_for_application(
                application_id=application.id
            )
        context["review"] = True
        return render(request, "application_review.html", context)
    return HttpResponseNotFound()


@login_verified_required
@user_passes_test(is_organiser)
def applications_other(request, code, id, context={}):
    current_event = get_event(code=code)
    if current_event:
        if request.method == "POST":
            if request.POST["submit"] == "comment":
                if request.POST["comment"]:
                    add_comment(id, request.user.id, request.POST["comment"])
                    messages.success(
                        request,
                        "Your comment has been added successfully to the application.",
                    )
                else:
                    messages.error(request, "The comment cannot be empty!")
        current_application = get_application_by_id(application_id=id)
        if current_application:
            context["event"] = current_event
            context["application"] = current_application
            context["comments"] = get_comments_for_application(
                application_id=current_application.id
            )
            return render(request, "application_review.html", context)
    return HttpResponseNotFound()


def subscribe(request, id):
    subscriber = Subscriber.objects.filter(
        id=id,
        status__in=[
            SubscriberStatus.PENDING.value,
            SubscriberStatus.UNSUBSCRIBED.value,
        ],
    ).first()
    if subscriber:
        subscriber.status = SubscriberStatus.SUBSCRIBED.value
        subscriber.save()
        messages.add_message(request, messages.INFO, "Your email has been verified!")
    else:
        subscriber = Subscriber.objects.filter(
            id=id, status=SubscriberStatus.SUBSCRIBED.value
        ).first()
        if subscriber:
            messages.add_message(
                request, messages.INFO, "Your email has already been verified before!"
            )
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "We are sorry, but we couldn't verify your email!",
            )
    return HttpResponseRedirect(reverse("app_home"))


def unsubscribe(request, id):
    subscriber = Subscriber.objects.filter(
        id=id, status=SubscriberStatus.SUBSCRIBED.value
    ).first()
    if subscriber:
        subscriber.status = SubscriberStatus.UNSUBSCRIBED.value
        subscriber.save()
        messages.add_message(request, messages.INFO, "You have been unsubscribed!")
    else:
        messages.add_message(
            request, messages.ERROR, "We are sorry, but we couldn't verify your email!"
        )
    return HttpResponseRedirect(reverse("app_home"))


def live(request, code, context={}):
    current_event = get_event(code=code, application_status=None)
    if current_event:
        context["event"] = current_event
        if current_event.schedule:
            current_line = 0
            schedule = list()
            current_day = None
            current_starts_at = None
            current_ends_at = None
            current_title = None
            for schedule_line in current_event.schedule.replace("\r", "").split("\n"):
                if schedule_line:
                    try:
                        current_day = datetime.datetime.strptime(
                            schedule_line[1:].lstrip(), "%Y-%m-%d"
                        )
                    except ValueError:
                        pass
                    try:
                        if not current_starts_at:
                            current_starts_at = datetime.datetime.strptime(
                                schedule_line, "%H:%M"
                            )
                        else:
                            current_ends_at = datetime.datetime.strptime(
                                schedule_line, "%H:%M"
                            )
                    except ValueError:
                        pass
                    if schedule_line[:2] == "##":
                        current_title = schedule_line[2:].lstrip()
                    elif schedule_line[0] == ">":
                        current_description = schedule_line[1:].lstrip()
                        if current_title and current_starts_at:
                            schedule_item = dict(
                                name=current_title,
                                description=current_description,
                                starts_at=timezone.datetime(
                                    day=current_day.day,
                                    month=current_day.month,
                                    year=current_day.year,
                                    hour=current_starts_at.hour,
                                    minute=current_starts_at.minute,
                                    tzinfo=None,
                                ),
                            )
                            if current_ends_at:
                                schedule_item["ends_at"] = timezone.datetime(
                                    day=current_day.day,
                                    month=current_day.month,
                                    year=current_day.year,
                                    hour=current_ends_at.hour,
                                    minute=current_ends_at.minute,
                                    tzinfo=None,
                                )
                            list.append(schedule, schedule_item)
                            current_title = None
                            current_starts_at = None
                            current_ends_at = None
                        else:
                            return response(
                                request,
                                code=500,
                                message="The schedule file for the event is wrongly formatted on line "
                                + str(current_line)
                                + ".",
                            )
                    current_line += 1
        else:
            return response(request, code=404)
        starts_at = current_event.starts_at.replace(minute=0, second=0).replace(
            tzinfo=None
        )
        ends_at = current_event.ends_at
        if ends_at.minute > 0 or ends_at.second > 0:
            ends_at += timezone.timedelta(hours=1)
        ends_at = ends_at.replace(minute=0, second=0).replace(tzinfo=None)
        hours = [
            (
                # TODO: Fix timezone
                starts_at + timezone.timedelta(hours=h + 2),
                starts_at + timezone.timedelta(hours=h + 3),
            )
            for h in range(math.ceil((ends_at - starts_at).total_seconds() / 3600.0))
        ]
        context["schedule"] = [
            dict(
                time_from=hour[0].replace(tzinfo=None),
                time_to=hour[1].replace(tzinfo=None),
                schedule=[
                    schedule_item
                    for schedule_item in schedule
                    if hour[0]
                    # TODO: Fix timezone
                    <= schedule_item["starts_at"] < hour[1]
                ],
            )
            for hour in hours
        ]
        days = []
        for hour in hours:
            if hour[0].date() not in [d.date() for d in days]:
                list.append(days, hour[0].replace(tzinfo=None))
        context["days"] = days
        # TODO: Fix timezone
        now = timezone.now()
        if now > current_event.ends_at:
            now = current_event.ends_at
        context["now"] = now
        context["now_tz"] = now.replace(tzinfo=None) + timezone.timedelta(hours=2)
        return render(request, "live.html", context)
    return response(request, code=404)


@login_verified_required
@user_passes_test(is_participant)
def apply_remove(request, code, context={}):
    context["popup"] = dict(
        title="Remove your application",
        message="Are you sure you want to do that? After removing it, you won't be able to apply again! "
        "If you just want to modify something, let us know at contact@kthack.com and we'll help you out.",
        actions=[
            dict(
                name="Remove",
                url=reverse("event_applyremoveconfirm", kwargs=dict(code=code)),
            )
        ],
    )
    return apply(request, code, context=context)


@login_verified_required
@user_passes_test(is_participant)
def apply_remove_confirm(request, code, context={}):
    current_event = get_event(code=code)
    if current_event:
        current_application = get_application(
            event_id=current_event.id, user_id=request.user.id
        )
        if current_application:
            current_application.cancel()
            messages.success(request, "Your application has been cancelled.")
    return HttpResponseRedirect(reverse("app_dashboard"))


@login_verified_required
def message(request, id, context={}):
    message = get_message(message_id=id)
    if message:
        context["message"] = message
        return render(request, "message.html", context)
    return HttpResponseRedirect(reverse("app_dashboard"))


@login_verified_required
@user_passes_test(is_organiser)
def applications_ranking(request, code, context={}):
    current_event = get_event(code=code)
    if current_event:
        context["ranking"] = get_ranking(code)
        return render(request, "application_ranking.html", context)
    return HttpResponseNotFound()
