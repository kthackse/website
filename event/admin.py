from django.contrib import admin

from event.models import Event


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "type")
    list_display = ("name", "code", "type")
    list_filter = ("type",)
    ordering = ("name", "code", "type")
