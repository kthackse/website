from django.http import HttpResponseNotFound
from django.shortcuts import render

from page.utils import get_page


def page(request, category, code):
    current_data = dict()
    current_page = get_page(category, code, user=request.user)
    if current_page:
        current_data["page"] = current_page
        return render(request, "page.html", current_data)
    return HttpResponseNotFound()
