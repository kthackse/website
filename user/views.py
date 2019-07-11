from django.contrib import auth
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from user import forms


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("root"))

    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        next_page = request.GET("next", "/")
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = auth.authenticate(email=email, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(next_page)
            else:
                form.add_error(None, "The email or password are invalid, please try again")
    else:
        form = forms.LoginForm()

    return render(request, "login.html", {"form": form})
