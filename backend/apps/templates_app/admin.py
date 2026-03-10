from django.contrib import admin

from .models import SurveyTemplate, TemplateRating


class TemplateRatingInline(admin.TabularInline):
    model = TemplateRating
    extra = 0
    readonly_fields = ["user", "score", "comment", "created_at"]


@admin.register(SurveyTemplate)
class SurveyTemplateAdmin(admin.ModelAdmin):
    list_display = [
        "title", "category", "question_count",
        "use_count", "average_rating", "is_public",
        "is_featured", "created_at",
    ]
    list_filter = ["category", "is_public", "is_featured"]
    search_fields = ["title", "description"]
    readonly_fields = ["id", "use_count", "average_rating", "created_at", "updated_at"]
    inlines = [TemplateRatingInline]
