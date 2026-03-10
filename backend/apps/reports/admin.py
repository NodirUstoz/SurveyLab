from django.contrib import admin

from .models import Report, ScheduledReport


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = [
        "title", "survey", "created_by", "report_type",
        "output_format", "status", "is_shared",
        "created_at", "generated_at",
    ]
    list_filter = ["report_type", "output_format", "status", "is_shared"]
    search_fields = ["title", "survey__title", "created_by__email"]
    readonly_fields = [
        "id", "share_token", "file_size_bytes",
        "created_at", "updated_at", "generated_at",
    ]


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    list_display = [
        "survey", "created_by", "report_type", "frequency",
        "is_active", "last_generated_at", "next_scheduled_at",
    ]
    list_filter = ["report_type", "frequency", "is_active"]
    search_fields = ["survey__title", "created_by__email"]
    readonly_fields = [
        "id", "last_generated_at", "next_scheduled_at", "created_at",
    ]
