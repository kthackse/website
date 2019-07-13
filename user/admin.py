from django.contrib import admin
from django.contrib.auth.models import Group

from user.models import User, Department, Company, UserChange


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("id", "email", "name", "surname", "type")
    list_display = ("email", "name", "surname", "type")
    list_filter = ("type",)
    ordering = ("name", "surname", "email", "type")


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "type")
    list_display = ("name", "code", "type")
    list_filter = ("type",)
    ordering = ("name", "code", "type")


@admin.register(Company)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code")
    list_display = ("name", "code")
    ordering = ("name", "code")


@admin.register(UserChange)
class UserChangeAdmin(admin.ModelAdmin):
    search_fields = ("id", "user", "changed_by", "field", "value_previous", "value_current")
    list_display = ("id", "user", "changed_by", "field", "value_previous", "value_current", "created_at",)
    list_filter = ("field",)
    ordering = ("-created_at", "user", "changed_by", "field",)


admin.site.unregister(Group)
