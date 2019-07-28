from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponseNotFound, HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone

from event.enums import DietType, TshirtSize, ApplicationStatus
from event.models import Application
from event.utils import get_event, get_application, get_applications
from user.utils import is_participant, is_organiser


@login_required
@user_passes_test(is_participant)
def apply(request, code):
    current_data = dict()
    current_event = get_event(code=code)
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
        current_data["status"] = "DRAFT"
        if current_application:
            current_data["application"] = current_application
            current_data["tshirt_int"] = int(current_application.tshirt)
            if current_application.status in [ApplicationStatus.DRAFT.value, ApplicationStatus.PENDING.value, ApplicationStatus.CANCELLED.value, ApplicationStatus.INVITED.value, ApplicationStatus.CONFIRMED.value, ApplicationStatus.ATTENDED.value]:
                current_data["status"] = ApplicationStatus(current_application.status).name.upper()
            else:
                current_data["status"] = "PENDING"
        if (
            request.method == "POST"
            and not current_application
            or (current_application and current_application.status == ApplicationStatus.DRAFT.value)
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
                if required_field not in request.POST or not request.POST[required_field]:
                    all_filled = False
            all_filled &= "resume" in request.FILES if not current_application else True
            if all_filled:
                # TODO: Display messages of error and validate URLs
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
                return HttpResponseRedirect("")
        return render(request, "apply.html", current_data)
    return HttpResponseNotFound()


@login_required
@user_passes_test(is_organiser)
def applications(request, code):
    current_data = dict()
    current_event = get_event(code=code)
    if current_event:
        current_data["event"] = current_event
        current_data["applications"] = get_applications(event_id=current_event.id)
        return render(request, "applications.html", current_data)
    return HttpResponseNotFound()
