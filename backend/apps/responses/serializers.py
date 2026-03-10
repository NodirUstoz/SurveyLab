from rest_framework import serializers

from apps.surveys.models import Question, QuestionOption
from .models import Answer, ResponseSession, SurveyResponse


class AnswerSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(
        source="question.text", read_only=True
    )
    question_type = serializers.CharField(
        source="question.question_type", read_only=True
    )
    selected_option_ids = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=QuestionOption.objects.all(),
        source="selected_options",
        required=False,
    )
    display_value = serializers.ReadOnlyField()

    class Meta:
        model = Answer
        fields = [
            "id", "question", "question_text", "question_type",
            "text_value", "numeric_value", "selected_option_ids",
            "matrix_values", "file_upload", "ranking_values",
            "display_value", "answered_at",
        ]
        read_only_fields = ["id", "answered_at"]


class AnswerSubmitSerializer(serializers.Serializer):
    """Serializer for a single answer in a submission payload."""

    question_id = serializers.UUIDField()
    text_value = serializers.CharField(required=False, allow_blank=True, default="")
    numeric_value = serializers.FloatField(required=False, allow_null=True, default=None)
    selected_option_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    matrix_values = serializers.DictField(required=False, default=dict)
    ranking_values = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )


class SurveyResponseSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyResponse
        fields = [
            "id", "survey", "respondent", "status", "language",
            "duration_seconds", "metadata", "answers", "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]


class SurveyResponseListSerializer(serializers.ModelSerializer):
    answer_count = serializers.SerializerMethodField()

    class Meta:
        model = SurveyResponse
        fields = [
            "id", "survey", "status", "language",
            "duration_seconds", "answer_count", "submitted_at",
        ]
        read_only_fields = ["id", "submitted_at"]

    def get_answer_count(self, obj):
        return obj.answers.count()


class SubmitResponseSerializer(serializers.Serializer):
    """Top-level serializer for submitting a complete survey response."""

    survey_id = serializers.UUIDField()
    session_key = serializers.CharField(required=False, allow_blank=True, default="")
    language = serializers.CharField(required=False, default="en")
    answers = AnswerSubmitSerializer(many=True)
    duration_seconds = serializers.IntegerField(required=False, allow_null=True)
    metadata = serializers.DictField(required=False, default=dict)


class ResponseSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResponseSession
        fields = [
            "id", "survey", "session_key", "current_page",
            "partial_data", "language", "started_at",
            "last_activity", "is_completed",
        ]
        read_only_fields = ["id", "started_at", "last_activity"]


class SavePartialResponseSerializer(serializers.Serializer):
    """Serializer for saving partial (in-progress) response data."""

    survey_id = serializers.UUIDField()
    session_key = serializers.CharField()
    current_page = serializers.IntegerField(default=0)
    answers = AnswerSubmitSerializer(many=True, required=False, default=list)
    language = serializers.CharField(required=False, default="en")


class ExportRequestSerializer(serializers.Serializer):
    """Serializer for requesting a data export."""

    format = serializers.ChoiceField(choices=["csv", "xlsx", "pdf"], default="csv")
    date_from = serializers.DateTimeField(required=False, allow_null=True)
    date_to = serializers.DateTimeField(required=False, allow_null=True)
    status_filter = serializers.ChoiceField(
        choices=["all", "complete", "partial", "disqualified"],
        default="all",
    )
