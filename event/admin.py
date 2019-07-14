from django.contrib import admin

from event.models import Event, ScheduleEvent


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "type",)
    list_display = ("name", "code", "type", "starts_at", "ends_at",)
    list_filter = ("type", "starts_at", "ends_at",)
    ordering = ("starts_at", "ends_at", "name", "code", "type",)


@admin.register(ScheduleEvent)
class ScheduleEventAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "description", "event",)
    list_display = ("name", "event", "starts_at", "ends_at",)
    list_filter = ("starts_at", "ends_at",)
    ordering = ("starts_at", "ends_at", "name", "event",)
