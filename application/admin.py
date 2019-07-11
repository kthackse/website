from django.contrib import admin

from application.models import Application, Team, Vote, Comment, Reimbursement


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    search_fields = ("id", "user", "description", "projects", "city", "country", "university", "degree", "team",)
    list_display = ("user", "status", "created_at",)
    list_filter = ("status", "created_at",)
    ordering = ("created_at", "updated_at", "user",)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    search_fields = ("id", "name", "code", "creator", "event",)
    list_display = ("name", "code", "lemma", "creator", "event",)
    list_filter = ("created_at",)
    ordering = ("created_at", "name", "code", "creator",)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    search_fields = ("id", "application", "voted_by",)
    list_display = ("application", "voted_by", "vote_tech", "vote_personal", "vote_total",)
    list_filter = ("created_at",)
    ordering = ("created_at", "vote_total",)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    search_fields = ("id", "application", "commented_by",)
    list_display = ("application", "commented_by", "content",)
    list_filter = ("created_at",)
    ordering = ("created_at",)


@admin.register(Reimbursement)
class ReimbursementAdmin(admin.ModelAdmin):
    search_fields = ("id", "applications", "reimbursed_by", "comment",)
    list_display = ("id", "reimbursed_by", "comment", "type", "status", "expires_at",)
    list_filter = ("created_at", "type", "status", "expires_at",)
    ordering = ("created_at", "expires_at",)
