from django.contrib import admin

from .models import PanelMember, ResearchPanel


class PanelMemberInline(admin.TabularInline):
    model = PanelMember
    extra = 0
    readonly_fields = [
        "surveys_invited", "surveys_completed",
        "last_invited_at", "last_responded_at", "joined_at",
    ]
    fields = [
        "email", "first_name", "last_name",
        "is_active", "opt_out", "surveys_invited",
        "surveys_completed",
    ]


@admin.register(ResearchPanel)
class ResearchPanelAdmin(admin.ModelAdmin):
    list_display = [
        "name", "organization", "member_count",
        "active_member_count", "is_active", "created_at",
    ]
    list_filter = ["is_active", "organization"]
    search_fields = ["name", "description"]
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [PanelMemberInline]


@admin.register(PanelMember)
class PanelMemberAdmin(admin.ModelAdmin):
    list_display = [
        "email", "first_name", "last_name", "panel",
        "is_active", "opt_out", "surveys_completed",
        "response_rate", "joined_at",
    ]
    list_filter = ["is_active", "opt_out", "panel"]
    search_fields = ["email", "first_name", "last_name"]
    readonly_fields = [
        "id", "surveys_invited", "surveys_completed",
        "last_invited_at", "last_responded_at", "joined_at",
    ]
