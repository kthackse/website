from django.contrib import admin

from event.models import Event, ScheduleEvent, Application, Team, Vote, Comment, Reimbursement, FAQItem, Subscriber, \
    CompanyEvent


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


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    search_fields = ("id", "title", "description", "event",)
    list_display = ("title", "event", "order",)
    list_filter = ("event",)
    ordering = ("order", "title",)


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


@admin.register(Subscriber)
class SubscriberAdmin(admin.ModelAdmin):
    search_fields = ("id", "email", "status",)
    list_display = ("email", "status", "created_at", "updated_at",)
    list_filter = ("status",)
    ordering = ("created_at", "updated_at",)


@admin.register(CompanyEvent)
class CompanyEventAdmin(admin.ModelAdmin):
    search_fields = ("id", "event", "company", "tier",)
    list_display = ("event", "company", "tier",)
    list_filter = ("tier",)
    ordering = ("event", "tier", "company",)
