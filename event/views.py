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
            # TODO: Handle form
            print("FORM SENT")
        return render(request, "apply.html", current_data)
    return HttpResponseNotFound()
