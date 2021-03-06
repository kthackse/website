from django import forms
from django.contrib.auth.password_validation import validate_password
from django.utils.safestring import mark_safe

from user.enums import SexType


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=255)
    password = forms.CharField(
        widget=forms.PasswordInput, label="Password", max_length=255
    )


class RegisterForm(LoginForm):
    name = forms.CharField(label="First name", max_length=225)
    surname = forms.CharField(label="Last name", max_length=225)
    password2 = forms.CharField(
        widget=forms.PasswordInput, label="Repeat password", max_length=100
    )
    terms = forms.BooleanField(
        label=mark_safe(
            'I\'ve read, understand and accept the <a href="../../page/legal/terms-and-conditions" target="_blank">'
            'Terms & Conditions</a> and the <a href="../../page/legal/privacy-and-cookies" target="_blank">'
            "Privacy and Cookies Policy</a>"
        )
    )
    phone = forms.CharField(label="Phone", max_length=225)
    birthday = forms.DateField(label="Birthday")
    sex = forms.ChoiceField(label="Sex", choices=((t.value, t.name) for t in SexType))
    city = forms.CharField(label="City", max_length=225)
    country = forms.CharField(label="Country", max_length=225)

    field_order = [
        "name",
        "surname",
        "email",
        "password",
        "password2",
        "phone",
        "birthday",
        "sex",
        "city",
        "country",
        "terms",
    ]

    def clean_password2(self):
        # Check that the two password entries match
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")
        if password and password2 and password != password2:
            raise forms.ValidationError("Passwords don't match")
        validate_password(password)
        return password2

    def clean_terms(self):
        cc = self.cleaned_data.get("terms", False)
        if not cc:
            raise forms.ValidationError(
                'In order to signup you have to accept our <a href="../../page/legal/terms-and-conditions"'
                ' target="_blank">Terms & Conditions</a> and the <a href="../../page/legal/privacy-and-cookies"'
                ' target="_blank">Privacy and Cookies Policy</a>.'
            )
        return cc


class ProfileForm(forms.Form):
    name = forms.CharField(label="First name", max_length=225)
    surname = forms.CharField(label="Last name", max_length=225)
    email = forms.EmailField(label="Email", max_length=255)
    picture = forms.FileField(label="Picture", required=False)
    picture_public_participants = forms.BooleanField(
        label="Display picture to other participants", required=False
    )
    picture_public_sponsors_and_recruiters = forms.BooleanField(
        label="Display picture to sponsors and recruiters", required=False
    )
    phone = forms.CharField(label="Phone", max_length=255)
    city = forms.CharField(label="City", max_length=255)
    country = forms.CharField(label="Country", max_length=255)
