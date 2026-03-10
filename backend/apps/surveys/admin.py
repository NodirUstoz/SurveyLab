from django.contrib import admin

from .models import (
    BranchingRule,
    Question,
    QuestionOption,
    Survey,
    SurveyPage,
    SurveySettings,
)


class SurveySettingsInline(admin.StackedInline):
    model = SurveySettings
    can_delete = False


class SurveyPageInline(admin.TabularInline):
    model = SurveyPage
    extra = 0
    ordering = ["order"]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = [
        "title", "owner", "status", "category",
        "question_count", "response_count",
        "published_at", "created_at",
    ]
    list_filter = ["status", "category", "default_language"]
    search_fields = ["title", "description", "slug"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["id", "created_at", "updated_at"]
    inlines = [SurveySettingsInline, SurveyPageInline]


class QuestionOptionInline(admin.TabularInline):
    model = QuestionOption
    extra = 0
    ordering = ["order"]


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = [
        "text_short", "question_type", "page", "is_required", "order",
    ]
    list_filter = ["question_type", "is_required"]
    search_fields = ["text"]
    inlines = [QuestionOptionInline]

    @admin.display(description="Question")
    def text_short(self, obj):
        return obj.text[:80]


@admin.register(SurveyPage)
class SurveyPageAdmin(admin.ModelAdmin):
    list_display = ["survey", "title", "order", "is_visible"]
    list_filter = ["is_visible"]


@admin.register(BranchingRule)
class BranchingRuleAdmin(admin.ModelAdmin):
    list_display = [
        "survey", "source_question", "operator", "value",
        "action", "is_active", "order",
    ]
    list_filter = ["action", "operator", "is_active"]
