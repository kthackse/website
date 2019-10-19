import os
import uuid
from decimal import Decimal
import urllib.request
from urllib.error import URLError

import html2text
import weasyprint
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import models, transaction
from django.template.loader import get_template
from django.utils import timezone
from versatileimagefield.fields import VersatileImageField

from app.enums import FileType, FileStatus
from app.models import File, get_new_verification
from app.utils import markdown_to_text, get_substitutions_templates
from app.variables import HACKATHON_VOTE_PERSONAL, HACKATHON_VOTE_TECHNICAL
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
    MessageType,
    LetterStatus,
    LetterType,
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
    logo_white = VersatileImageField(
        "White logo", upload_to=path_and_rename, blank=True, null=True
    )
    logo_clean = VersatileImageField(
        "Clean logo", upload_to=path_and_rename, blank=True, null=True
    )
    logo_white_clean = VersatileImageField(
        "Clean white logo", upload_to=path_and_rename, blank=True, null=True
    )
    background = models.FileField(
        upload_to=path_and_rename_background, blank=True, null=True
    )
    # TODO: Divide sponsors into categories
    city = models.CharField(max_length=255, default="Stockholm")
    country = models.CharField(max_length=255, default="Sweden")
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    coding_starts_at = models.DateTimeField(blank=True, null=True)
    coding_ends_at = models.DateTimeField(blank=True, null=True)
    hackers = models.IntegerField(default=200)
    published = models.BooleanField(default=False)
    dates_public = models.BooleanField(default=True)
    subscribe_public = models.BooleanField(default=True)
    faq_public = models.BooleanField(default=True)
    organisers_public = models.BooleanField(default=True)
    companies_public = models.BooleanField(default=True)
    application_available = models.DateTimeField()
    application_deadline = models.DateTimeField()
    organisers_open = models.BooleanField(default=False)
    volunteers_open = models.BooleanField(default=False)
    mentors_open = models.BooleanField(default=False)
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

    @property
    def duration(self):
        if self.coding_starts_at and self.coding_ends_at:
            return self.coding_ends_at - self.coding_starts_at
        return self.ends_at - self.starts_at

    @property
    def hacking_starts_at(self):
        if self.coding_starts_at:
            return self.coding_starts_at
        return self.starts_at

    @property
    def hacking_ends_at(self):
        if self.coding_ends_at:
            return self.coding_ends_at
        return self.ends_at

    @property
    def logo_home(self):
        return self.logo

    @property
    def logo_white_home(self):
        if self.logo_white:
            return self.logo_white
        return self.logo

    @property
    def logo_header(self):
        if self.logo_clean:
            return self.logo_clean
        return self.logo_home

    @property
    def logo_white_header(self):
        if self.logo_white_clean:
            return self.logo_white_clean
        return self.logo_white_home

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
        if (
            self.coding_starts_at
            and not self.starts_at <= self.coding_starts_at <= self.ends_at
        ):
            messages[
                "coding_starts_at"
            ] = "The end time for coding needs to be within the times of the event"
        if (
            self.coding_ends_at
            and not self.starts_at <= self.coding_ends_at <= self.ends_at
        ):
            messages[
                "coding_ends_at"
            ] = "The start time for coding needs to be within the times of the event"
        if messages:
            raise ValidationError(messages)


def path_and_rename_company(instance, filename):
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
    return os.path.join("event/company/", filename)


class CompanyEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey("Event", on_delete=models.PROTECT)
    company = models.ForeignKey("user.Company", on_delete=models.PROTECT)
    current_logo = VersatileImageField(
        "Image", upload_to=path_and_rename_company, blank=True, null=True
    )
    tier = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in CompanyTier)
    )
    public = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Company in event"
        verbose_name_plural = "Companies in events"
        # unique_together = ("event", "company",)

    @property
    def logo(self):
        if self.current_logo:
            return self.current_logo
        return self.company.logo

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
    note = models.CharField(max_length=255, blank=True, null=True)

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
    team = models.ForeignKey("Team", on_delete=models.SET_NULL, null=True, blank=True)

    # Score
    score = models.FloatField(default=0.0)

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

    def cancel(self):
        self.team = None
        self.status = ApplicationStatus.CANCELLED.value
        self.save()

    def set_score(self, score):
        self.score = score
        self.save()

    def __str__(self):
        return str(self.user) + " (" + str(self.event) + ")"

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

    def __str__(self):
        return self.name + " (" + str(self.event) + ")"

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
    vote_tech = models.SmallIntegerField(validators=[valid_vote], null=True, blank=True)
    vote_personal = models.SmallIntegerField(
        validators=[valid_vote], null=True, blank=True
    )
    vote_total = models.FloatField(null=True, blank=True)

    # Skipped?
    skipped = models.BooleanField(default=False)

    class Meta:
        unique_together = ("application", "voted_by")

    def clean(self):
        messages = dict()
        if not self.voted_by.is_organiser:
            messages["user"] = "A user must be an organiser in order to vote"
        if not self.skipped and (not self.vote_tech or not self.vote_personal):
            messages["skipped"] = "A non skip vote must have a score"
        if messages:
            raise ValidationError(messages)

    def delete(self, *args, **kwargs):
        if not self.skipped:
            with transaction.atomic():
                votes = (
                    Vote.objects.filter(application_id=self.application_id)
                    .exclude(id=self.id)
                    .values_list("vote_total", flat=True)
                )
                if not votes:
                    votes = [0]
                self.application.set_score((sum(votes) / len(votes)))
        return super().delete(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.skipped:
            self.vote_total = (
                HACKATHON_VOTE_PERSONAL * self.vote_personal
                + HACKATHON_VOTE_TECHNICAL * self.vote_tech
            ) / (HACKATHON_VOTE_PERSONAL + HACKATHON_VOTE_TECHNICAL)
            with transaction.atomic():
                votes = (
                    Vote.objects.filter(application_id=self.application_id)
                    .exclude(id=self.id)
                    .count()
                )
                score = (self.application.score * votes + self.vote_total) / (votes + 1)
                self.application.set_score(score)
        return super().save(*args, **kwargs)


class Comment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    application = models.ForeignKey("Application", on_delete=models.PROTECT)
    commented_by = models.ForeignKey("user.User", on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    content = models.TextField(max_length=1000)

    def clean(self):
        messages = dict()
        if not self.commented_by.is_organiser:
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


class Letter(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=31)
    application = models.ForeignKey("Application", on_delete=models.CASCADE)
    responsible = models.ForeignKey("user.User", on_delete=models.PROTECT)
    type = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in LetterType), default=LetterType.VISA.value
    )
    letter = models.FileField(null=True, blank=True, upload_to="letter")
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in LetterStatus),
        default=LetterStatus.DRAFT.value,
    )
    sent_by = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        related_name="letter_sent_by",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # TODO: Create letter file
    def get_letter_file(self):
        template = get_template("file/letter.html")
        html = template.render(
            context=dict(letter=self, **get_substitutions_templates())
        )
        return weasyprint.HTML(string=html).write_pdf()

    def mark_as_signed(self, request=None):
        self.status = LetterStatus.SIGNED.value
        self.save()

    def mark_as_sent(self, request=None):
        self.status = LetterStatus.SENT.value
        if request:
            self.sent_by = request.user
        self.save()

    def clean(self):
        messages = dict()
        if not self.responsible.can_sign:
            messages["responsible"] = "The letter responsible must be able to sign"
        if messages:
            raise ValidationError(messages)

    def save(self, *args, **kwargs):
        self.clean()
        if not self.code:
            if (
                not Letter.objects.filter(created_at__year=timezone.now().year)
                .exclude(id=self.id)
                .exists()
            ):
                self.code = str(timezone.now().year) + "-" + f"{10:04d}"
            else:
                self.code = (
                    str(timezone.now().year)
                    + "-"
                    + f"{int(Letter.objects.filter(created_at__year=timezone.now().year).order_by('-created_at').first().code[-4:])+1:04d}"
                )
        self.letter = ContentFile(self.get_letter_file(), name=self.code + ".pdf")
        return super().save(*args, **kwargs)


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
    invoice = models.ForeignKey("app.File", on_delete=models.PROTECT)
    status = models.PositiveSmallIntegerField(
        choices=((s.value, s.name) for s in InvoiceStatus),
        default=InvoiceStatus.DRAFT.value,
    )
    sent_by = models.ForeignKey(
        "user.User",
        on_delete=models.PROTECT,
        related_name="invoice_seny_by",
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_invoice_file(self, verification_control=None, verification_code=None):
        template = get_template("file/invoice.html")
        html = template.render(
            context=dict(invoice=self, **get_substitutions_templates(), verification_control=verification_control, verification_code=verification_code)
        )
        return weasyprint.HTML(string=html).write_pdf()

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
        if self.invoice:
            self.invoice.status = FileStatus.DEPRECATED
            self.invoice.save()
        verification_control, verification_code, verification_until = get_new_verification(self.id)
        invoice = File(
            file=ContentFile(
                self.get_invoice_file(verification_control=verification_control, verification_code=verification_code),
                name=self.company_event.event.code + "_" + self.code + ".pdf",
            ),
            type=FileType.INVOICE,
            status=FileStatus.VALID,
            verification_control=verification_control,
            verification_code=verification_code,
            verification_until=verification_until
        )
        invoice.save()
        self.invoice = invoice
        return super().save(*args, **kwargs)


def path_and_rename_attachment(instance, filename):
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
    return os.path.join("event/attachment/", filename)


class Message(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    event = models.ForeignKey(
        "event.Event", on_delete=models.PROTECT, blank=True, null=True
    )
    recipient = models.ForeignKey(
        "user.User", on_delete=models.CASCADE, blank=True, null=True
    )
    recipient_email = models.EmailField(max_length=255, blank=True, null=True)
    type = models.PositiveSmallIntegerField(
        choices=((t.value, t.name) for t in MessageType),
        default=MessageType.GENERIC.value,
    )
    title = models.CharField(max_length=255)
    content = models.TextField()
    attachment = models.ForeignKey("app.File", on_delete=models.PROTECT, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def content_short(self):
        short = self.content[:50].rstrip(" ")
        if short[-3:] != "...":
            short += "..."
        return short

    @property
    def content_short_plain(self):
        short = markdown_to_text(html2text.html2text(self.content))[:100].rstrip(" ")
        if short[-3:] != "...":
            short += "..."
        return short

    def clean(self):
        messages = dict()
        if not self.recipient and not self.recipient_email:
            messages["recipient"] = "A recipient or email's recipient must be provided"
        if messages:
            raise ValidationError(messages)
