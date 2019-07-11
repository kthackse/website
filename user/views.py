from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from user import forms
from user.models import User


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("app_root"))

    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        next_page = request.GET.get("next", "/")
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


def signup(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("app_root"))

    if request.method == 'POST':
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            surname = form.cleaned_data['surname']

            if User.objects.filter(email=email).first() is not None:
                # messages.error(request, 'An account with this email already exists')
                pass
            else:
                user = User.objects.create_user(email=email, password=password, name=name, surname=surname)
                user = auth.authenticate(email=email, password=password)
                auth.login(request, user)
                return HttpResponseRedirect(reverse('app_root'))
    else:
        form = forms.RegisterForm()

    return render(request, 'signup.html', {'form': form})


def logout(request):
    auth.logout(request)
    # messages.success(request, 'Successfully logged out!')
    return HttpResponseRedirect(reverse('user_login'))


@login_required
def profile(request):
    return render(request, 'profile.html')
