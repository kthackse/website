from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from event.enums import DietType, TshirtSize, ApplicationStatus
from event.models import Application
from event.utils import get_event, get_application
from user.utils import is_participant


@login_required
@user_passes_test(is_participant)
def apply(request, code):
    current_data = dict()
    current_event = get_event(code)
    if current_event:
        current_data["event"] = current_event
        current_data["years"] = [
            (timezone.now().year + year, year == 0) for year in range(-1, 5)
        ]
        current_data["diets"] = [
            (diet.name.capitalize().replace("_", " "), diet.value) for diet in DietType
        ]
        current_data["tshirts"] = [
            (tshirt.name.upper(), tshirt.value) for tshirt in TshirtSize
        ]
        current_application = get_application(
            event_id=current_event.id, user_id=request.user.id
        )
        if current_application:
            current_data["application"] = current_application
        if (
            request.method == "POST"
            and not current_application
            or current_application.status == ApplicationStatus.SAVED.value
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
                if required_field not in request.POST:
                    all_filled = False
            all_filled &= "resume" in request.FILES
            if all_filled:
                university = request.POST["university"]
                degree = request.POST["degree"]
                graduation_year = request.POST["graduation_year"]
                description = request.POST["description"]
                projects = request.POST["projects"]
                github = (
                    request.POST["github"] if "github" in request.POST else ""
                )
                devpost = (
                    request.POST["devpost"] if "devpost" in request.POST else ""
                )
                linkedin = (
                    request.POST["linkedin"] if "linkedin" in request.POST else ""
                )
                website = (
                    request.POST["website"] if "website" in request.POST else ""
                )
                resume = request.FILES["resume"]
                resume_available = (
                    request.POST["resume_available"] if "resume_available" in request.POST else False
                )
                diet = request.POST["diet"]
                diet_other = (
                    request.POST["diet_other"] if "diet_other" in request.POST else ""
                )
                tshirt = request.POST["tshirt"]
                hardware = (
                    request.POST["hardware"] if "hardware" in request.POST else ""
                )
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
                )
                application.save()
        return render(request, "apply.html", current_data)
    return HttpResponseNotFound()
