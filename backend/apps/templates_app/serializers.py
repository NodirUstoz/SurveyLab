from django.db.models import Avg
from rest_framework import serializers

from .models import SurveyTemplate, TemplateRating


class TemplateRatingSerializer(serializers.ModelSerializer):
    user_email = serializers.CharField(source="user.email", read_only=True)

    class Meta:
        model = TemplateRating
        fields = ["id", "template", "user", "user_email", "score", "comment", "created_at"]
        read_only_fields = ["id", "user", "created_at"]


class SurveyTemplateSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(
        source="created_by.full_name", read_only=True
    )
    rating_count = serializers.SerializerMethodField()

    class Meta:
        model = SurveyTemplate
        fields = [
            "id", "title", "description", "category", "tags",
            "thumbnail", "template_data",
            "estimated_minutes", "question_count",
            "is_public", "is_featured",
            "created_by", "created_by_name", "organization",
            "use_count", "average_rating", "rating_count",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "use_count", "average_rating",
            "created_by", "created_at", "updated_at",
        ]

    def get_rating_count(self, obj):
        return obj.ratings.count()


class SurveyTemplateListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for template browsing."""

    class Meta:
        model = SurveyTemplate
        fields = [
            "id", "title", "description", "category", "tags",
            "thumbnail", "estimated_minutes", "question_count",
            "is_featured", "use_count", "average_rating",
        ]


class CreateFromTemplateSerializer(serializers.Serializer):
    """Serializer for creating a new survey from a template."""

    template_id = serializers.UUIDField()
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(required=False, allow_blank=True, default="")
