from django.contrib import admin

from .models import Answer, ResponseSession, SurveyResponse


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = [
        "question", "text_value", "numeric_value",
        "matrix_values", "ranking_values", "display_value",
        "answered_at",
    ]
    fields = [
        "question", "text_value", "numeric_value", "display_value",
    ]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = [
        "id_short", "survey", "respondent", "status",
        "language", "duration_seconds", "submitted_at",
    ]
    list_filter = ["status", "language", "submitted_at"]
    search_fields = [
        "survey__title", "respondent__email", "ip_address",
    ]
    readonly_fields = [
        "id", "ip_address", "user_agent", "metadata", "submitted_at",
    ]
    inlines = [AnswerInline]

    @admin.display(description="Response ID")
    def id_short(self, obj):
        return str(obj.id)[:8]


@admin.register(ResponseSession)
class ResponseSessionAdmin(admin.ModelAdmin):
    list_display = [
        "session_key_short", "survey", "respondent",
        "current_page", "is_completed",
        "started_at", "last_activity",
    ]
    list_filter = ["is_completed", "language"]
    search_fields = ["session_key", "survey__title"]
    readonly_fields = [
        "id", "session_key", "partial_data",
        "ip_address", "user_agent",
        "started_at", "last_activity",
    ]

    @admin.display(description="Session Key")
    def session_key_short(self, obj):
        return obj.session_key[:16] + "..."


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = [
        "id_short", "response", "question_short",
        "display_value_short", "answered_at",
    ]
    search_fields = ["response__survey__title", "question__text"]
    readonly_fields = ["id", "answered_at"]

    @admin.display(description="ID")
    def id_short(self, obj):
        return str(obj.id)[:8]

    @admin.display(description="Question")
    def question_short(self, obj):
        return obj.question.text[:50]

    @admin.display(description="Answer")
    def display_value_short(self, obj):
        val = obj.display_value
        return val[:80] if val else ""
