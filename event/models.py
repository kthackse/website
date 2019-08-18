import os
import uuid
from decimal import Decimal
from io import BytesIO
import urllib.request
from urllib.error import URLError

import cairosvg
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from versatileimagefield.fields import VersatileImageField

from event.enums import (
    EventType,
    EventApplicationStatus,
    ApplicationStatus,
    DietType,
    TshirtSize,
    ReimbursementType,
    ReimbursementStatus,
    SubscriberStatus,
    CompanyTier,
    InvoiceStatus,
)
from user.enums import UserType

from djmoney.models.fields import MoneyField


def path_and_rename(instance, filename):
    """
    Stack Overflow
    Django ImageField change file name on upload
    https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
    """
    ext = filename.split(".")[-1]
    # get filename
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        # set filename as random string
        filename = "{}.{}".format(uuid.uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join("event/picture/", filename)


def path_and_rename_background(instance, filename):
    """
    Stack Overflow
    Django ImageField change file name on upload
    https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
    """
    ext = filename.split(".")[-1]
    # get filename
    if instance.pk:
        filename = "{}.{}".format(instance.pk, ext)
    else:
        # set filename as random string
        filename = "{}.{}".format(uuid.uuid4().hex, ext)
    # return the whole path to the file
    return os.path.join("event/background/", filename)


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31, unique=True)
    description = models.TextField(max_length=1000, blank=True, null=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in EventType)
    )
    logo = VersatileImageField("Logo", upload_to=path_and_rename)
    background = models.FileField(
        upload_to=path_and_rename_background, blank=True, null=True
    )
    # TODO: Divide sponsors into categories
    city = models.CharField(max_length=255, default="Stockholm")
    country = models.CharField(max_length=255, default="Sweden")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    hackers = models.IntegerField(default=200)
    published = models.BooleanField(default=False)
    dates_public = models.BooleanField(default=True)
    subscribe_public = models.BooleanField(default=True)
    faq_public = models.BooleanField(default=True)
    organisers_public = models.BooleanField(default=True)
    companies_public = models.BooleanField(default=True)
    application_available = models.DateTimeField()
    application_deadline = models.DateTimeField()
    companies_open = models.BooleanField(default=True)
    custom_home = models.BooleanField(default=False)
    schedule_markdown_url = models.CharField(max_length=255, blank=True, null=True)

    @property
    def application_status(self):
        current_time = timezone.now()
        if current_time < self.application_available:
            return EventApplicationStatus.PENDING
        elif self.application_available <= current_time <= self.application_deadline:
            return EventApplicationStatus.OPEN
        return EventApplicationStatus.CLOSED

    @property
    def application_review_available(self):
        if self.application_status in [
            EventApplicationStatus.PENDING,
            EventApplicationStatus.OPEN,
        ]:
            return True
        current_time = timezone.now()
        return current_time < self.ends_at

    @property
    def schedule(self):
        if self.schedule_markdown_url:
            try:
                return (
                    urllib.request.urlopen(self.schedule_markdown_url)
                    .read()
                    .decode("utf-8")
                )
            except URLError:
                return None
        return None

    def __str__(self):
        return self.name + " " + str(self.starts_at.year)

    def clean(self):
        messages = dict()
        if (
            Event.objects.filter(
                starts_at__lte=self.ends_at, ends_at__gte=self.starts_at
            )
            .exclude(id=self.id)
            .exists()
        ):
            temporal_overlap = "There's another event already taking place for the selected range of dates"
            messages["starts_at"] = temporal_overlap
            messages["ends_at"] = temporal_overlap
        if self.application_deadline > self.ends_at:
            messages[
                "application_deadline"
            ] = "The application deadline can't be after the event has ended"
        if self.application_available > self.application_deadline:
            messages[
                "application_deadline"
            ] = "The application deadline can't be before applications open"
        if messages:
            raise ValidationError(messages)


class CompanyEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("Event", on_delete=models.PROTECT)
    company = models.ForeignKey("user.Company", on_delete=models.PROTECT)
    tier = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in CompanyTier)
    )
    public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company in event"
        verbose_name_plural = "Companies in events"
        # unique_together = ("event", "company",)

    def __str__(self):
        return self.company.name + " (" + self.event.name + ")"


class FAQItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(max_length=2500)
    event = models.ForeignKey("Event", on_delete=models.PROTECT)
    active = models.BooleanField(default=False)
    order = models.IntegerField(default=0)

    class Meta:
        verbose_name = "FAQ item"
        verbose_name_plural = "FAQ items"


def path_and_rename_resume(instance, filename):
    """
    Stack Overflow
    Django ImageField change file name on upload
    https://stackoverflow.com/questions/15140942/django-imagefield-change-file-name-on-upload
    """
    ext = filename.split(".")[-1]
    filename = "{}.{}".format(instance.user.id, ext)
    return os.path.join("event/resume/" + instance.event.code + "/", filename)


class Application(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("event.Event", on_delete=models.PROTECT)
    user = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, related_name="event_user"
    )
    invited_by = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="invited_by",
    )
    contacted_by = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="contacted_by",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in ApplicationStatus),
        default=ApplicationStatus.DRAFT.value,
    )

    # Application details
    description = models.TextField(max_length=1000)
    projects = models.TextField(max_length=1000)

    # Reimbursement
    money_needed = MoneyField(
        max_digits=7, decimal_places=2, default_currency="SEK", blank=True, null=True
    )

    # Resume
    resume = models.FileField(upload_to=path_and_rename_resume)
    resume_available = models.BooleanField(default=False)

    # University
    university = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    graduation_year = models.PositiveIntegerField(default=timezone.now().year)

    # URLs
    github = models.URLField(blank=True, null=True)
    devpost = models.URLField(blank=True, null=True)
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # Swag
    diet = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in DietType), default=DietType.REGULAR.value
    )
    diet_other = models.CharField(max_length=255, blank=True, null=True)
    tshirt = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in TshirtSize), default=TshirtSize.L.value
    )
    hardware = models.TextField(max_length=1000, null=True, blank=True)

    # Team
    team = models.ForeignKey("Team", on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        unique_together = ("event", "user")

    @property
    def status_str(self):
        return ApplicationStatus(self.status).name.upper()

    def is_invited(self):
        return self.invited_by is not None

    def is_contacted(self):
        return self.contacted_by is not None

    def is_firsttimer(self):
        return (
            Application.objects.filter(
                user=self.user, status=ApplicationStatus.CONFIRMED.value
            )
            is None
        )

    def is_reimbursementneeded(self):
        return self.money_needed.amount > Decimal(0.0)

    def clean(self):
        messages = dict()
        if self.user.type != UserType.PARTICIPANT.value:
            messages["user"] = "The user needs to be a participant"
        if self.team and self.team.event != self.event:
            messages["team"] = "The team needs to be from the same edition"
        if messages:
            raise ValidationError(messages)


class Team(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("event.Event", on_delete=models.PROTECT)
    creator = models.ForeignKey("user.User", on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=31)
    lemma = models.CharField(max_length=127, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (("event", "creator"), ("event", "code"))


def valid_vote(vote):
    return 0 <= vote <= 10


class Vote(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey("Application", on_delete=models.PROTECT)
    voted_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    # Vote result
    vote_tech = models.IntegerField(validators=[valid_vote])
    vote_personal = models.SmallIntegerField(validators=[valid_vote])
    vote_total = models.FloatField()

    class Meta:
        unique_together = ("application", "voted_by")

    def clean(self):
        messages = dict()
        if not self.voted_by.is_organiser():
            messages["user"] = "A user must be an organiser in order to vote"
        if messages:
            raise ValidationError(messages)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey("Application", on_delete=models.PROTECT)
    commented_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)

    def clean(self):
        messages = dict()
        if not self.commented_by.is_organiser():
            messages["user"] = "A user must be an organiser in order to make a comment"
        if messages:
            raise ValidationError(messages)


class Reimbursement(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    applications = models.ManyToManyField("Application")
    reimbursed_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    # Money
    money_assigned = MoneyField(
        max_digits=7, decimal_places=2, default_currency="SEK", blank=True, null=True
    )
    comment = models.TextField(max_length=1000)

    # Details
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in ReimbursementType)
    )
    receipt = models.FileField(null=True, blank=True, upload_to="receipt")
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in ReimbursementStatus)
    )
    expires_at = models.DateTimeField()

    # TODO: Check only one reimbursement per application


class Subscriber(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(max_length=255, unique=True)
    events = models.ManyToManyField("Event")
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in SubscriberStatus),
        default=SubscriberStatus.PENDING.value,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Invoice(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=31)
    code_invoice_company = models.CharField(max_length=31, blank=True, null=True)
    company_event = models.ForeignKey("CompanyEvent", on_delete=models.PROTECT)
    responsible_event = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, related_name="responisble_event"
    )
    responsible_company = models.ForeignKey(
        "user.User", on_delete=models.PROTECT, related_name="responisble_company"
    )
    description = models.CharField(max_length=255, blank=True, null=True)
    amount = MoneyField(max_digits=7, decimal_places=2, default_currency="SEK")
    vat = models.PositiveIntegerField(default=0)
    date_due = models.DateField(blank=True)
    invoice = models.FileField(null=True, blank=True, upload_to="invoice")
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in InvoiceStatus),
        default=InvoiceStatus.DRAFT.value,
    )
    sent_by = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        related_name="sent_by",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def create_invoice(self, item: str = None):
        if self.vat > 0:
            invoice_svg = open("app/templates/file/invoice/base_with_vat.svg").read()
        else:
            invoice_svg = open("app/templates/file/invoice/base.svg").read()
        invoice_svg = invoice_svg.replace(
            "{{event_name}}",
            self.company_event.event.name.upper()
            + " "
            + str(self.company_event.event.starts_at.year),
        )
        invoice_svg = invoice_svg.replace(
            "{{event_location}}",
            self.company_event.event.city.upper()
            + ", "
            + self.company_event.event.country.upper(),
        )
        invoice_svg = invoice_svg.replace(
            "{{company_name}}", self.company_event.company.name.upper()
        )
        invoice_svg = invoice_svg.replace(
            "{{date_today}}", str(timezone.now().strftime("%B %d, %Y")).upper()
        )
        invoice_svg = invoice_svg.replace(
            "{{company_organisation_name}}", self.company_event.company.org_name.upper()
        )
        invoice_svg = invoice_svg.replace(
            "{{company_address_1}}",
            (
                self.company_event.company.address_1
                if self.company_event.company.address_1
                else "Address: UNKNOWN"
            ),
        )
        invoice_svg = invoice_svg.replace(
            "{{company_address_2}}",
            (
                self.company_event.company.address_2
                if self.company_event.company.address_2
                else self.company_event.event.city
            ),
        )
        invoice_svg = invoice_svg.replace(
            "{{company_organisation_number}}",
            (
                self.company_event.company.organisation_number
                if self.company_event.company.organisation_number
                else "UNKNOWN"
            ),
        )
        invoice_svg = invoice_svg.replace("{{invoice_reference}}", self.code)
        invoice_svg = invoice_svg.replace(
            "{{invoice_created}}", timezone.now().strftime("%Y-%m-%d %H:%M")
        )
        invoice_svg = invoice_svg.replace(
            "{{invoice_due}}", self.date_due.strftime("%Y-%m-%d")
        )
        if self.code_invoice_company:
            invoice_svg = invoice_svg.replace(
                "{{company_invoice_reference}}",
                "Company reference: " + self.code_invoice_company,
            )
        else:
            invoice_svg = invoice_svg.replace("{{company_invoice_reference}}", "")
        if self.description:
            invoice_svg = invoice_svg.replace("{{invoice_item}}", self.description)
        else:
            invoice_svg = invoice_svg.replace(
                "{{invoice_item}}",
                (
                    item
                    if item
                    else self.company_event.event.name
                    + " "
                    + str(self.company_event.event.starts_at.year)
                    + " "
                    + CompanyTier(self.company_event.tier).name.capitalize()
                    + " Sponsorship"
                ),
            )
        invoice_svg = invoice_svg.replace(
            "{{invoice_amount}}",
            "{:,.2f}".format(self.amount.amount)
            .replace(",", ";")
            .replace(".", ",")
            .replace(";", ".")
            + " "
            + str(self.amount.currency),
        )
        if self.vat > 0:
            invoice_svg = invoice_svg.replace(
                "{{invoice_vat}}", str(self.vat) + "% VAT"
            )
            vat_amount = (float(self.amount.amount) * float(self.vat)) / 100.0
            invoice_svg = invoice_svg.replace(
                "{{invoice_vat_amount}}",
                "{:,.2f}".format(vat_amount)
                .replace(",", ";")
                .replace(".", ",")
                .replace(";", ".")
                + " "
                + str(self.amount.currency),
            )
            invoice_svg = invoice_svg.replace(
                "{{invoice_total}}",
                "{:,.2f}".format(self.amount.amount + Decimal(vat_amount))
                .replace(",", ";")
                .replace(".", ",")
                .replace(";", ".")
                + " "
                + str(self.amount.currency),
            )
        else:
            invoice_svg = invoice_svg.replace(
                "{{invoice_total}}",
                "{:,.2f}".format(self.amount.amount)
                .replace(",", ";")
                .replace(".", ",")
                .replace(";", ".")
                + " "
                + str(self.amount.currency),
            )
        invoice_svg = invoice_svg.replace(
            "{{event_responsible_name}}", str(self.responsible_event)
        )
        invoice_svg = invoice_svg.replace(
            "{{event_responsible_phone}}", str(self.responsible_event.phone)
        )
        invoice_svg = invoice_svg.replace(
            "{{event_responsible_email}}", str(self.responsible_event.email)
        )
        return ContentFile(
            BytesIO((cairosvg.svg2pdf(bytestring=invoice_svg))).getvalue(),
            name=self.company_event.event.code + "_" + self.code + ".pdf",
        )

    def mark_as_sent(self, request=None):
        self.status = InvoiceStatus.SENT.value
        if request:
            self.sent_by = request.user
        self.save()

    def clean(self):
        messages = dict()
        if not self.responsible_event.is_organiser:
            messages["responsible_event"] = "An event responsible must be an organiser"
        if not self.responsible_company.is_sponsor:
            messages["responsible_company"] = "A company responsible must be a sponsor"
        if messages:
            raise ValidationError(messages)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.code:
            if (
                not Invoice.objects.filter(created_at__year=timezone.now().year)
                .exclude(id=self.id)
                .exists()
            ):
                self.code = str(timezone.now().year) + "-" + f"{10:04d}"
            else:
                self.code = (
                    str(timezone.now().year)
                    + "-"
                    + f"{int(Invoice.objects.filter(created_at__year=timezone.now().year).order_by('-created_at').first().code[-4:])+1:04d}"
                )
        if not self.date_due:
            time_now = timezone.now()
            time_month = time_now.month + 2
            self.date_due = timezone.datetime(
                day=time_now.day,
                month=time_month,
                year=(time_now.year if time_month <= 12 else time_now.year + 1),
            ).date()
        self.invoice = self.create_invoice()
        return super().save(*args, **kwargs)
