from django.contrib.auth.decorators import user_passes_test, login_required
from django.http import HttpResponseNotFound
from django.shortcuts import render
from django.utils import timezone

from event.enums import DietType, TshirtSize
from event.utils import get_event
from user.utils import is_participant


@login_required
@user_passes_test(is_participant)
def apply(request, code):
    current_data = dict()
    current_page = get_event(code)
    if current_page:
        current_data["event"] = current_page
        current_data["years"] = [(timezone.now().year + year, year == 0) for year in range(-1, 5)]
        current_data["diets"] = [(diet.name.capitalize().replace("_", " "), diet.value) for diet in DietType]
        current_data["tshirts"] = [(tshirt.name.upper(), tshirt.value) for tshirt in TshirtSize]
        if request.method == "POST":
            # TODO: Fill required fields
            required_fields = ["university", "degree", "graduation_year", "description", "projects", "diet", "tshirt"]
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
                resume = request.FILES["resume"]
                resume_available = request.POST["resume_available"]
                diet = request.POST["diet"]
                diet_other = (request.POST["diet_other"] if "diet_other" in request.POST else "")
                tshirt = request.POST["tshirt"]
                hardware = (request.POST["hardware"] if "hardware" in request.POST else "")
                print("FORM SENT")
        return render(request, "apply.html", current_data)
    return HttpResponseNotFound()
