from django.http import HttpResponseRedirect
from django.urls import reverse


def root(request):
    # TODO: Check if organiser, participant, sponsor or media
    return HttpResponseRedirect(reverse("user_login"))
