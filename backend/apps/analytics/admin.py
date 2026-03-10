from django.contrib import admin

from .models import CrossTabulation, QuestionAnalytics, SurveyAnalytics


class QuestionAnalyticsInline(admin.TabularInline):
    model = QuestionAnalytics
    extra = 0
    readonly_fields = [
        "question", "total_answers", "skip_count", "answer_rate",
        "numeric_average", "numeric_median", "nps_score", "updated_at",
    ]
    fields = [
        "question", "total_answers", "skip_count", "answer_rate",
        "numeric_average", "nps_score",
    ]


@admin.register(SurveyAnalytics)
class SurveyAnalyticsAdmin(admin.ModelAdmin):
    list_display = [
        "survey", "total_responses", "complete_responses",
        "completion_rate", "average_duration_seconds",
        "last_response_at", "updated_at",
    ]
    list_filter = ["updated_at"]
    search_fields = ["survey__title"]
    readonly_fields = [
        "id", "total_responses", "complete_responses", "partial_responses",
        "disqualified_responses", "completion_rate",
        "average_duration_seconds", "median_duration_seconds",
        "total_views", "unique_visitors", "drop_off_rates",
        "response_trend", "language_distribution", "device_distribution",
        "last_response_at", "updated_at",
    ]
    inlines = [QuestionAnalyticsInline]


@admin.register(CrossTabulation)
class CrossTabulationAdmin(admin.ModelAdmin):
    list_display = [
        "survey", "question_a", "question_b",
        "chi_square_statistic", "cramers_v", "created_at",
    ]
    list_filter = ["created_at"]
    search_fields = ["survey__title"]
    readonly_fields = [
        "id", "contingency_table", "chi_square_statistic",
        "p_value", "cramers_v", "created_at",
    ]
