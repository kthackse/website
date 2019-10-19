from django.contrib import admin

from app.models import File, FileVerified


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(File)
class FileAdmin(ReadOnlyAdmin):
    search_fields = ("id", "type", "status", "verification_control", "verification_code")
    list_display = ("id", "type", "status", "verification_control", "verification_code", "created_at", "updated_at")
    list_filter = ("type", "status", "created_at", "updated_at")
    ordering = ("-created_at",)


@admin.register(FileVerified)
class FileVerifiedAdmin(ReadOnlyAdmin):
    search_fields = ("id", "ip", "status", "verification_control", "verification_code")
    list_display = ("id", "status", "verification_control", "verification_code", "verified_at")
    list_filter = ("status", "verified_at")
    ordering = ("-verified_at",)
