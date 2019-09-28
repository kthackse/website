import csv
import zipfile
from io import StringIO, BytesIO

from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import (
    HttpResponseRedirect,
    HttpResponseNotFound,
    StreamingHttpResponse,
)
from django.shortcuts import render
from django.urls import reverse
from django.utils import timezone

from app.settings import SIGNUP_DISABLED
from app.utils import login_verified_required
from app.variables import HACKATHON_NAME
from event.utils.utils import get_applications_by_user
from user import forms
from user.enums import SexType, UserType
from user.models import User, UserChange
from user.utils import send_verify


def login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("app_dashboard"))

    if request.method == "POST":
        form = forms.LoginForm(request.POST)
        next_page = request.GET.get("next", "/")
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            user = auth.authenticate(email=email, password=password)
            if user:
                auth.login(request, user)
                if next_page == "/":
                    return HttpResponseRedirect(reverse("app_dashboard"))
                return HttpResponseRedirect(next_page)
            else:
                messages.error(
                    request, "Login failed, the email or password are invalid!"
                )
    else:
        form = forms.LoginForm()

    return render(request, "login.html", {"form": form})


def signup(request):
    if SIGNUP_DISABLED:
        messages.error(request, "The signup page has temporarily been disabled.")
        return HttpResponseRedirect(reverse("app_home"))

    current_data = dict()
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse("app_dashboard"))

    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        # TODO: Fix validation
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]
            name = form.cleaned_data["name"]
            surname = form.cleaned_data["surname"]
            phone = form.cleaned_data["phone"]
            birthday = form.cleaned_data["birthday"]
            sex = form.cleaned_data["sex"]
            city = form.cleaned_data["city"]
            country = form.cleaned_data["country"]

            existing_user = User.objects.filter(email=email).first()
            if existing_user:
                if existing_user.is_active:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Signup failed, an account with this email already exists!",
                    )
                else:
                    messages.add_message(
                        request,
                        messages.ERROR,
                        "Signup failed, a deactivated account with this email still exists, contact us for more information.",
                    )
            else:
                user = User.objects.create_participant(
                    email=email,
                    password=password,
                    name=name,
                    surname=surname,
                    phone=phone,
                    birthday=birthday,
                    sex=sex,
                    city=city,
                    country=country,
                )
                user = auth.authenticate(email=email, password=password)
                send_verify(user)
                auth.login(request, user)
                messages.success(
                    request,
                    "Thank-you for registering, remember to confirm your email!",
                )
                return HttpResponseRedirect(reverse("app_home"))
        else:
            messages.add_message(
                request,
                messages.ERROR,
                "Signup failed, some fields might be wrong or empty!",
            )
    else:
        form = forms.RegisterForm()

    current_data["form"] = form
    current_data["sexes"] = [
        (
            (
                sex.name.capitalize()
                if sex.name.lower() != "none"
                else "Prefer not to say"
            ),
            sex.value,
        )
        for sex in SexType
    ]
    return render(request, "signup.html", current_data)


def logout(request):
    auth.logout(request)
    messages.success(request, "Successfully logged out!")
    return HttpResponseRedirect(reverse("user_login"))


# TODO: Signup test with check for autotype as organiser depending on email


@login_required
def profile(request):
    if request.method == "POST":
        form = forms.ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            try:
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
                    send_verify(request.user)
                    messages.success(
                        request,
                        "The email has been changed, you need to verify it again!",
                    )
                if "picture" in request.FILES:
                    picture = request.FILES["picture"]
                    UserChange(
                        user=request.user,
                        changed_by=request.user,
                        field="picture",
                        value_previous=request.user.picture,
                        value_current=picture,
                    ).save()
                    request.user.picture.delete_sized_images()
                    request.user.picture = picture
                picture_public_participants = form.cleaned_data[
                    "picture_public_participants"
                ]
                if (
                    request.user.picture_public_participants
                    != picture_public_participants
                ):
                    UserChange(
                        user=request.user,
                        changed_by=request.user,
                        field="picture_public_participants",
                        value_previous=request.user.picture_public_participants,
                        value_current=picture_public_participants,
                    ).save()
                    request.user.picture_public_participants = (
                        picture_public_participants
                    )
                picture_public_sponsors_and_recruiters = form.cleaned_data[
                    "picture_public_sponsors_and_recruiters"
                ]
                if (
                    request.user.picture_public_sponsors_and_recruiters
                    != picture_public_sponsors_and_recruiters
                ):
                    UserChange(
                        user=request.user,
                        changed_by=request.user,
                        field="picture_public_sponsors_and_recruiters",
                        value_previous=request.user.picture_public_sponsors_and_recruiters,
                        value_current=picture_public_sponsors_and_recruiters,
                    ).save()
                    request.user.picture_public_sponsors_and_recruiters = (
                        picture_public_sponsors_and_recruiters
                    )
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
                messages.success(request, "Profile updated successfully!")
            except IntegrityError:
                messages.error(request, "The email you entered is already in use!")
        else:
            messages.error(request, "The data you introduced is invalid, please fill in all the fields!")

    user_data = request.user.get_dict()
    form = forms.ProfileForm(user_data)
    if request.user.is_participant:
        user_data["applications"] = get_applications_by_user(request.user.id)
    return render(
        request,
        "profile.html",
        {
            "form": form,
            "user": user_data,
            "picture": request.user.picture.crop["500x500"],
        },
    )


@login_verified_required
def profile_other(request, id):
    user = User.objects.filter(id=id).first()
    if user and request.user.type in [
        UserType.PARTICIPANT.value,
        UserType.ORGANISER.value,
        UserType.VOLUNTEER.value,
        UserType.MENTOR.value,
        UserType.SPONSOR.value,
        UserType.RECRUITER.value,
    ]:
        extra_info = (
            request.user.type
            in [
                UserType.ORGANISER.value,
                UserType.VOLUNTEER.value,
                UserType.MENTOR.value,
            ]
            or user.picture_public_participants
            and request.user.type == UserType.PARTICIPANT.value
            or user.picture_public_sponsors_and_recruiters
            and request.user.type in [UserType.SPONSOR.value, UserType.RECRUITER.value]
        )
        user_data = user.get_dict()
        form = forms.ProfileForm(user_data)
        return render(
            request,
            "profile.html",
            {
                "form": form,
                "user": user_data,
                "picture": user.picture.crop["500x500"],
                "other": True,
                "extra_info": extra_info,
                "type_str": UserType(user.type).name.capitalize(),
                "underage": user.is_underage,
            },
        )
    return HttpResponseNotFound()


@login_required
def verify(request):
    if request.user.email_verified:
        return HttpResponseRedirect(reverse("app_dashboard"))
    return render(request, "verify.html")


@login_required
def verify_key(request, verification_key):
    if request.user.email_verified:
        return HttpResponseRedirect(reverse("app_dashboard"))
    request.user.verify(verify_key=verification_key)
    if request.user.email_verified:
        messages.success(request, "Thank-you, your email has been verified!")
    else:
        messages.error(
            request, "We couldn't verify your email as the verification key expired."
        )
    return HttpResponseRedirect(reverse("user_verify"))


@login_required
def send_verification(request):
    send_verify(request.user)
    messages.success(request, "The email verification has been sent again!")
    return HttpResponseRedirect(reverse("user_verify"))


@login_verified_required
def download_personal_data(request):
    with StringIO() as csvfile:
        csvwriter = csv.writer(
            csvfile, delimiter=";", quotechar="|", quoting=csv.QUOTE_MINIMAL
        )
        csvwriter.writerow(["ID", request.user.id])
        csvwriter.writerow(["First name", request.user.name])
        csvwriter.writerow(["Last name", request.user.surname])
        csvwriter.writerow(["Email", request.user.email])
        csvwriter.writerow(["Email verified", request.user.email_verified])
        csvwriter.writerow(["Last login", request.user.last_login])
        csvwriter.writerow(["Type", UserType(request.user.type).name.upper()])
        if request.user.is_organiser or request.user.is_volunteer:
            csvwriter.writerow(
                [
                    "Departments",
                    ", ".join([str(d) for d in request.user.departments.all()]),
                ]
            )
        if request.user.is_sponsor or request.user.is_recruiter:
            csvwriter.writerow(["Company", request.user.company])
        csvwriter.writerow(
            ["Events", ", ".join([str(e) for e in request.user.events.all()])]
        )
        csvwriter.writerow(
            ["Picture public to participants", request.user.picture_public_participants]
        )
        csvwriter.writerow(
            [
                "Picture public to sponsors and recruiters",
                request.user.picture_public_sponsors_and_recruiters,
            ]
        )
        csvwriter.writerow(["Sex", SexType(request.user.sex).name.upper()])
        csvwriter.writerow(["Birthday", request.user.birthday])
        csvwriter.writerow(["Phone", request.user.phone])
        csvwriter.writerow(["City", request.user.city])
        csvwriter.writerow(["Country", request.user.country])

        mf = BytesIO()
        zf = zipfile.ZipFile(mf, mode="w", compression=zipfile.ZIP_DEFLATED)
        zf.writestr("profile.csv", csvfile.getvalue())
        zf.writestr("profile.png", request.user.picture.read())
        zf.close()

        # TODO: Fix wrong formatted zip
        response = StreamingHttpResponse(mf.getvalue(), "rb")
        response["Content-Type"] = "application/zip"
        response["Content-Disposition"] = (
            'attachment; filename="'
            + HACKATHON_NAME.lower()
            + "_personaldata_"
            + str(request.user.id)
            + "_"
            + str(int(timezone.now().timestamp()))
            + '.zip"'
        )

        return response


@login_verified_required
def deactivate(request):
    request.user.mark_as_inactive()
    messages.success(
        request, "Your account has been deactivated, we are sorry to hear that."
    )
    auth.logout(request)
    return HttpResponseRedirect(reverse("app_home"))
