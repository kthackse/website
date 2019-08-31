from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.html import format_html

from app.utils import require_department
from event.enums import InvoiceStatus
from event.models import (
    Event,
    Application,
    Team,
    Vote,
    Comment,
    Reimbursement,
    FAQItem,
    Subscriber,
    CompanyEvent,
    Invoice,
    Message,
)
from event.tasks import send_invoice
from user.enums import DepartmentType


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "type")
    list_display = ("name", "code", "type", "starts_at", "ends_at")
    list_filter = ("type", "starts_at", "ends_at")
    ordering = ("starts_at", "ends_at", "name", "code", "type")


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    search_fields = ("id", "title", "description", "event")
    list_display = ("title", "event", "order")
    list_filter = ("event",)
    ordering = ("order", "title")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    search_fields = (
        "id",
        "user",
        "event",
        "description",
        "projects",
        "city",
        "country",
        "university",
        "degree",
        "team",
    )
    list_display = ("id", "user", "event", "status", "score", "created_at")
    list_filter = ("status", "created_at", "event")
    ordering = ("created_at", "updated_at", "event", "user")


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "creator", "event")
    list_display = ("name", "code", "lemma", "creator", "event")
    list_filter = ("created_at",)
    ordering = ("created_at", "name", "code", "creator")


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    search_fields = ("id", "application", "voted_by")
    list_display = (
        "id",
        "application",
        "voted_by",
        "vote_tech",
        "vote_personal",
        "vote_total",
    )
    list_filter = ("created_at",)
    ordering = ("created_at", "vote_total")


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ("id", "application", "commented_by")
    list_display = ("application", "commented_by", "content")
    list_filter = ("created_at",)
    ordering = ("created_at",)


@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):
    search_fields = ("id", "applications", "reimbursed_by", "comment")
    list_display = ("id", "reimbursed_by", "comment", "type", "status", "expires_at")
    list_filter = ("created_at", "type", "status", "expires_at")
    ordering = ("created_at", "expires_at")


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ("id", "email", "status")
    list_display = ("email", "status", "created_at", "updated_at")
    list_filter = ("status",)
    ordering = ("created_at", "updated_at")


@admin.register(CompanyEvent)
class CompanyEventAdmin(admin.ModelAdmin):
    search_fields = ("id", "event", "company", "tier")
    list_display = ("company", "event", "tier", "public")
    list_filter = ("tier",)
    ordering = ("event", "tier", "company")


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    search_fields = ("id", "company_event", "responisble_event", "responisble_company")
    list_display = (
        "code",
        "company_event",
        "responsible_company",
        "responsible_event",
        "created_at",
        "status",
        "invoice",
        "send",
    )
    ordering = ("-code", "created_at", "updated_at", "company_event")
    readonly_fields = ("invoice", "code", "status", "sent_by")

    def get_urls(self):
        urls = super().get_urls()

        return [
            path(r"<path:id>/send_invoice/", self.send_invoice, name="send_invoice")
        ] + urls

    @require_department([DepartmentType.SPONSORSHIP])
    def send_invoice(self, request, id):
        send_invoice(Invoice.objects.filter(id=id).first(), request=request)
        messages.success(request, "Invoice was successfully sent!")
        return redirect(reverse("admin:event_invoice_changelist"))

    def send(self, invoice):
        if invoice.status == InvoiceStatus.SENT.value:
            return format_html(
                '<span class="readonly">Already sent</span> (<a href="'
                + str(invoice.id)
                + '/send_invoice">resend</a>)'
            )
        return format_html(
            '<a href="'
            + str(invoice.id)
            + '/send_invoice">Send to '
            + invoice.responsible_company.email
            + "</a>"
        )

    send.short_description = "Send invoice"


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    search_fields = ("id", "type", "title", "content")
    list_display = ("title", "event", "type", "recipient", "created_at",)
    list_filter = ("created_at",)
    ordering = ("-created_at",)
