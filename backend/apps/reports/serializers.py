from rest_framework import serializers

from .models import Report, ScheduledReport


class ReportSerializer(serializers.ModelSerializer):
    survey_title = serializers.CharField(source="survey.title", read_only=True)
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )

    class Meta:
        model = Report
        fields = [
            "id", "survey", "survey_title", "created_by", "created_by_name",
            "title", "report_type", "output_format", "status",
            "config", "include_summary", "include_charts",
            "include_individual_responses", "include_open_ended",
            "include_cross_tabs",
            "date_range_start", "date_range_end", "response_status_filter",
            "file", "file_size_bytes",
            "is_shared", "share_token",
            "created_at", "updated_at", "generated_at",
        ]
        read_only_fields = [
            "id", "created_by", "status", "file", "file_size_bytes",
            "share_token", "created_at", "updated_at", "generated_at",
        ]


class ReportCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = [
            "survey", "title", "report_type", "output_format",
            "config", "include_summary", "include_charts",
            "include_individual_responses", "include_open_ended",
            "include_cross_tabs",
            "date_range_start", "date_range_end", "response_status_filter",
        ]

    def validate_survey(self, value):
        user = self.context["request"].user
        if value.owner != user:
            raise serializers.ValidationError("You do not own this survey.")
        return value


class ReportListSerializer(serializers.ModelSerializer):
    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = Report
        fields = [
            "id", "survey", "survey_title", "title",
            "report_type", "output_format", "status",
            "file_size_bytes", "is_shared",
            "created_at", "generated_at",
        ]
        read_only_fields = ["id", "created_at", "generated_at"]


class ScheduledReportSerializer(serializers.ModelSerializer):
    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = ScheduledReport
        fields = [
            "id", "survey", "survey_title", "created_by",
            "report_type", "output_format", "frequency",
            "recipient_emails", "is_active",
            "last_generated_at", "next_scheduled_at",
            "config", "created_at",
        ]
        read_only_fields = [
            "id", "created_by", "last_generated_at",
            "next_scheduled_at", "created_at",
        ]


class ShareReportSerializer(serializers.Serializer):
    """Serializer for sharing/unsharing a report."""

    is_shared = serializers.BooleanField()
    password = serializers.CharField(
        required=False, allow_blank=True, default=""
    )
