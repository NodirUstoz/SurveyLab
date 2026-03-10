from rest_framework import serializers

from .models import CrossTabulation, QuestionAnalytics, SurveyAnalytics


class QuestionAnalyticsSerializer(serializers.ModelSerializer):
    question_text = serializers.CharField(
        source="question.text", read_only=True
    )
    question_type = serializers.CharField(
        source="question.question_type", read_only=True
    )

    class Meta:
        model = QuestionAnalytics
        fields = [
            "id", "question", "question_text", "question_type",
            "total_answers", "skip_count", "answer_rate",
            "option_distribution",
            "numeric_average", "numeric_median", "numeric_std_dev",
            "numeric_min", "numeric_max",
            "nps_score", "nps_promoters", "nps_passives", "nps_detractors",
            "word_cloud_data", "average_text_length",
            "matrix_aggregation", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class SurveyAnalyticsSerializer(serializers.ModelSerializer):
    question_analytics = QuestionAnalyticsSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyAnalytics
        fields = [
            "id", "survey", "total_responses", "complete_responses",
            "partial_responses", "disqualified_responses",
            "completion_rate", "average_duration_seconds",
            "median_duration_seconds", "total_views", "unique_visitors",
            "drop_off_rates", "response_trend",
            "language_distribution", "device_distribution",
            "last_response_at", "question_analytics", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class SurveyAnalyticsSummarySerializer(serializers.ModelSerializer):
    """Lightweight serializer for dashboard summaries."""

    survey_title = serializers.CharField(source="survey.title", read_only=True)

    class Meta:
        model = SurveyAnalytics
        fields = [
            "id", "survey", "survey_title", "total_responses",
            "complete_responses", "completion_rate",
            "average_duration_seconds", "last_response_at", "updated_at",
        ]
        read_only_fields = ["id", "updated_at"]


class CrossTabulationSerializer(serializers.ModelSerializer):
    question_a_text = serializers.CharField(
        source="question_a.text", read_only=True
    )
    question_b_text = serializers.CharField(
        source="question_b.text", read_only=True
    )

    class Meta:
        model = CrossTabulation
        fields = [
            "id", "survey", "question_a", "question_a_text",
            "question_b", "question_b_text",
            "contingency_table", "chi_square_statistic",
            "p_value", "cramers_v", "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class CrossTabulationRequestSerializer(serializers.Serializer):
    """Serializer for requesting a new cross-tabulation analysis."""

    question_a_id = serializers.UUIDField()
    question_b_id = serializers.UUIDField()

    def validate(self, attrs):
        if attrs["question_a_id"] == attrs["question_b_id"]:
            raise serializers.ValidationError(
                "Cross-tabulation requires two different questions."
            )
        return attrs
