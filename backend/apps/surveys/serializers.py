from rest_framework import serializers

from .models import (
    BranchingRule,
    Question,
    QuestionOption,
    Survey,
    SurveyPage,
    SurveySettings,
)


class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = [
            "id", "text", "value", "order", "is_other",
            "translations", "quota_limit", "quota_count",
        ]
        read_only_fields = ["id", "quota_count"]


class BranchingRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = BranchingRule
        fields = [
            "id", "survey", "source_question", "operator", "value",
            "action", "target_page", "target_question", "order", "is_active",
        ]
        read_only_fields = ["id"]


class QuestionSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = [
            "id", "page", "question_type", "text", "description",
            "is_required", "order", "translations", "config",
            "matrix_rows", "matrix_columns",
            "rating_min", "rating_max", "rating_min_label", "rating_max_label",
            "min_length", "max_length", "validation_regex",
            "options", "created_at", "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class QuestionCreateUpdateSerializer(serializers.ModelSerializer):
    options = QuestionOptionSerializer(many=True, required=False)

    class Meta:
        model = Question
        fields = [
            "id", "page", "question_type", "text", "description",
            "is_required", "order", "translations", "config",
            "matrix_rows", "matrix_columns",
            "rating_min", "rating_max", "rating_min_label", "rating_max_label",
            "min_length", "max_length", "validation_regex",
            "options",
        ]
        read_only_fields = ["id"]

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])
        question = Question.objects.create(**validated_data)
        for idx, option_data in enumerate(options_data):
            option_data["order"] = option_data.get("order", idx)
            QuestionOption.objects.create(question=question, **option_data)
        return question

    def update(self, instance, validated_data):
        options_data = validated_data.pop("options", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if options_data is not None:
            existing_ids = set()
            for option_data in options_data:
                option_id = option_data.get("id")
                if option_id:
                    opt = QuestionOption.objects.filter(
                        id=option_id, question=instance
                    ).first()
                    if opt:
                        for attr, value in option_data.items():
                            if attr != "id":
                                setattr(opt, attr, value)
                        opt.save()
                        existing_ids.add(str(opt.id))
                        continue
                new_opt = QuestionOption.objects.create(
                    question=instance, **option_data
                )
                existing_ids.add(str(new_opt.id))
            # Remove options not in the update payload
            instance.options.exclude(id__in=existing_ids).delete()

        return instance


class SurveyPageSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyPage
        fields = [
            "id", "survey", "title", "description", "order",
            "is_visible", "questions",
        ]
        read_only_fields = ["id"]


class SurveySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveySettings
        fields = [
            "allow_anonymous", "require_login", "one_response_per_user",
            "show_progress_bar", "shuffle_questions", "allow_back_navigation",
            "show_question_numbers", "max_responses", "quota_rules",
            "theme_color", "logo", "custom_css",
            "notify_on_response", "notification_emails",
        ]


class SurveyListSerializer(serializers.ModelSerializer):
    question_count = serializers.ReadOnlyField()
    response_count = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id", "title", "description", "slug", "status", "category",
            "tags", "default_language", "question_count", "response_count",
            "owner_name", "published_at", "closes_at",
            "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "question_count", "response_count", "owner_name",
            "created_at", "updated_at",
        ]


class SurveyDetailSerializer(serializers.ModelSerializer):
    pages = SurveyPageSerializer(many=True, read_only=True)
    settings = SurveySettingsSerializer(read_only=True)
    branching_rules = BranchingRuleSerializer(many=True, read_only=True)
    question_count = serializers.ReadOnlyField()
    response_count = serializers.ReadOnlyField()
    owner_name = serializers.CharField(source="owner.full_name", read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id", "title", "description", "slug", "status", "category",
            "tags", "default_language", "supported_languages",
            "welcome_message", "thank_you_message",
            "question_count", "response_count", "owner_name",
            "pages", "settings", "branching_rules",
            "published_at", "closes_at", "created_at", "updated_at",
        ]
        read_only_fields = [
            "id", "question_count", "response_count", "owner_name",
            "created_at", "updated_at",
        ]


class SurveyCreateSerializer(serializers.ModelSerializer):
    settings = SurveySettingsSerializer(required=False)

    class Meta:
        model = Survey
        fields = [
            "title", "description", "slug", "category", "tags",
            "default_language", "supported_languages",
            "welcome_message", "thank_you_message", "settings",
        ]

    def create(self, validated_data):
        settings_data = validated_data.pop("settings", {})
        survey = Survey.objects.create(**validated_data)
        SurveySettings.objects.create(survey=survey, **settings_data)
        # Create a default first page
        SurveyPage.objects.create(survey=survey, title="Page 1", order=0)
        return survey


class PublicSurveySerializer(serializers.ModelSerializer):
    """Serializer for the public-facing survey (respondent view)."""

    pages = SurveyPageSerializer(many=True, read_only=True)
    settings = SurveySettingsSerializer(read_only=True)

    class Meta:
        model = Survey
        fields = [
            "id", "title", "description", "default_language",
            "supported_languages", "welcome_message", "thank_you_message",
            "pages", "settings",
        ]
