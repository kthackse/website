from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse

from app.views import redirect_to
from user import forms
from user.models import User, UserChange


def login(request):
    page_redirect = redirect_to(request)
    if request.user.is_authenticated:
        return HttpResponseRedirect(page_redirect)

    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        next_page = request.GET.get("next", "/")
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = auth.authenticate(email=email, password=password)
            if user and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(next_page)
            else:
                form.add_error(
                    None, "The email or password are invalid, please try again"
                )
    else:
        form = forms.LoginForm()

    return render(request, "login.html", {"form": form})


def signup(request):
    page_redirect = redirect_to(request)
    if request.user.is_authenticated:
        return HttpResponseRedirect(page_redirect)

    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            name = form.cleaned_data["name"]
            surname = form.cleaned_data["surname"]

            if User.objects.filter(email=email).first() is not None:
                # messages.error(request, 'An account with this email already exists')
                pass
            else:
                user = User.objects.create_user(
                    email=email, password=password, name=name, surname=surname
                )
                user = auth.authenticate(email=email, password=password)
                auth.login(request, user)
                return HttpResponseRedirect(page_redirect)
    else:
        form = forms.RegisterForm()

    return render(request, "signup.html", {"form": form})


def logout(request):
    auth.logout(request)
    # messages.success(request, 'Successfully logged out!')
    return HttpResponseRedirect(reverse("app_home"))


@login_required
def profile(request):
    if request.method == "POST":
        form = forms.ProfileForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data["name"]
            if request.user.name != name:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="name",
                    value_previous=request.user.name,
                    value_current=name,
                ).save()
                request.user.name = name
            surname = form.cleaned_data["surname"]
            if request.user.surname != surname:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="surname",
                    value_previous=request.user.surname,
                    value_current=surname,
                ).save()
                request.user.surname = surname
            email = form.cleaned_data["email"]
            if request.user.email != email:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="email",
                    value_previous=request.user.email,
                    value_current=email,
                ).save()
                request.user.email_verified = False
                request.user.email = email
                # TODO: Send confirmation email and set message of that on webpage
            # TODO: Fix picture update
            # TODO: Remove old pictures with .delete_all_created_images()
            picture = form.cleaned_data["picture"]
            if picture:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="picture",
                    value_previous=request.user.picture,
                    value_current=picture,
                ).save()
                request.user.picture = picture
            picture_public_participants = form.cleaned_data["picture_public_participants"]
            if request.user.picture_public_participants != picture_public_participants:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="picture_public_participants",
                    value_previous=request.user.picture_public_participants,
                    value_current=picture_public_participants,
                ).save()
                request.user.picture_public_participants = picture_public_participants
            picture_public_sponsors_and_recruiters = form.cleaned_data["picture_public_sponsors_and_recruiters"]
            if request.user.picture_public_sponsors_and_recruiters != picture_public_sponsors_and_recruiters:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="picture_public_sponsors_and_recruiters",
                    value_previous=request.user.picture_public_sponsors_and_recruiters,
                    value_current=picture_public_sponsors_and_recruiters,
                ).save()
                request.user.picture_public_sponsors_and_recruiters = picture_public_sponsors_and_recruiters
            phone = form.cleaned_data["phone"]
            if request.user.phone != phone:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="phone",
                    value_previous=request.user.phone,
                    value_current=phone,
                ).save()
                request.user.phone = phone
            city = form.cleaned_data["city"]
            if request.user.city != city:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="city",
                    value_previous=request.user.city,
                    value_current=city,
                ).save()
                request.user.city = city
            country = form.cleaned_data["country"]
            if request.user.country != country:
                UserChange(
                    user=request.user,
                    changed_by=request.user,
                    field="country",
                    value_previous=request.user.country,
                    value_current=country,
                ).save()
                request.user.country = country
            request.user.save()

    user_data = request.user.get_dict()
    form = forms.ProfileForm(user_data)
    return render(
        request, "profile.html", {"form": form, "picture": request.user.picture.crop['500x500']}
    )
