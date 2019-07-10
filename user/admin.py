from django.contrib import admin
from django.contrib.auth.models import Group

from user.models import User, Department, Company


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    search_fields = ("id", "email", "name", "surname", "type",)
    list_display = ("email", "name", "surname", "type",)
    list_filter = ("type",)
    ordering = ("name", "surname", "email", "type",)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "type",)
    list_display = ("name", "code", "type",)
    list_filter = ("type",)
    ordering = ("name", "code", "type",)


@admin.register(Company)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code")
    list_display = ("name", "code",)
    ordering = ("name", "code",)


admin.site.unregister(Group)
