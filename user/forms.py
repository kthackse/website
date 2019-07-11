from django import forms
from django.contrib.auth.password_validation import (
    password_validators_help_texts,
    validate_password,
)


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
        label="I've read, understand and accept the Terms & Conditions and the Privacy and Cookies Policy"
    )

    field_order = [
        "name",
        "surname",
        "email",
        "password",
        "password2",
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
                "In order to signup you have to accept our Terms & Conditions and"
                " our Privacy and Cookies Policy."
            )
        return cc
