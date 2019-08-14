from django.contrib import admin

from job.models import Application, Offer


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "created_by", "company")
    list_display = ("name", "code", "created_by", "company", "created_at")
    list_filter = ("type", "status", "created_at")
    ordering = ("created_at", "updated_at")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    search_fields = ("id", "offer", "user", "status")
    list_display = ("user", "offer", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    ordering = ("created_at",)
