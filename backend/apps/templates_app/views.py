from django.db.models import Avg, Q
from django.utils.text import slugify
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.surveys.models import (
    Question,
    QuestionOption,
    Survey,
    SurveyPage,
    SurveySettings,
)
from .models import SurveyTemplate, TemplateRating
from .serializers import (
    CreateFromTemplateSerializer,
    SurveyTemplateListSerializer,
    SurveyTemplateSerializer,
    TemplateRatingSerializer,
)


class SurveyTemplateViewSet(viewsets.ModelViewSet):
    """Browse and manage survey templates."""

    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filterset_fields = ["category", "is_featured"]
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["use_count", "average_rating", "created_at", "title"]

    def get_queryset(self):
        qs = SurveyTemplate.objects.all()
        if self.action == "list":
            if self.request.user.is_authenticated and self.request.user.organization:
                qs = qs.filter(
                    Q(is_public=True)
                    | Q(organization=self.request.user.organization)
                )
            else:
                qs = qs.filter(is_public=True)
        return qs

    def get_serializer_class(self):
        if self.action == "list":
            return SurveyTemplateListSerializer
        return SurveyTemplateSerializer

    def perform_create(self, serializer):
        # Count questions in template_data
        template_data = serializer.validated_data.get("template_data", {})
        question_count = 0
        for page in template_data.get("pages", []):
            question_count += len(page.get("questions", []))

        serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization,
            question_count=question_count,
        )

    @action(detail=True, methods=["post"], url_path="create-survey")
    def create_survey(self, request, pk=None):
        """Create a new survey from this template."""
        template = self.get_object()
        serializer = CreateFromTemplateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        template_data = template.template_data

        # Create the survey
        slug = slugify(data["title"])
        base_slug = slug
        counter = 1
        while Survey.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        survey = Survey.objects.create(
            title=data["title"],
            description=data.get("description", template.description),
            slug=slug,
            owner=request.user,
            organization=request.user.organization,
            category=template.category,
        )

        # Apply settings from template
        settings_data = template_data.get("settings", {})
        SurveySettings.objects.create(survey=survey, **settings_data)

        # Create pages and questions from template
        for page_idx, page_data in enumerate(template_data.get("pages", [])):
            page = SurveyPage.objects.create(
                survey=survey,
                title=page_data.get("title", f"Page {page_idx + 1}"),
                description=page_data.get("description", ""),
                order=page_idx,
            )

            for q_idx, q_data in enumerate(page_data.get("questions", [])):
                question = Question.objects.create(
                    page=page,
                    question_type=q_data.get("question_type", "multiple_choice"),
                    text=q_data.get("text", ""),
                    description=q_data.get("description", ""),
                    is_required=q_data.get("is_required", False),
                    order=q_idx,
                    config=q_data.get("config", {}),
                    matrix_rows=q_data.get("matrix_rows", []),
                    matrix_columns=q_data.get("matrix_columns", []),
                    rating_min=q_data.get("rating_min", 1),
                    rating_max=q_data.get("rating_max", 5),
                    rating_min_label=q_data.get("rating_min_label", ""),
                    rating_max_label=q_data.get("rating_max_label", ""),
                )

                for opt_idx, opt_data in enumerate(q_data.get("options", [])):
                    QuestionOption.objects.create(
                        question=question,
                        text=opt_data.get("text", ""),
                        value=opt_data.get("value", ""),
                        order=opt_idx,
                        is_other=opt_data.get("is_other", False),
                    )

        # Increment use count
        template.use_count += 1
        template.save(update_fields=["use_count"])

        from apps.surveys.serializers import SurveyDetailSerializer
        return Response(
            SurveyDetailSerializer(survey).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"])
    def rate(self, request, pk=None):
        """Rate a template."""
        template = self.get_object()
        serializer = TemplateRatingSerializer(data={
            **request.data,
            "template": template.id,
        })
        serializer.is_valid(raise_exception=True)

        rating, created = TemplateRating.objects.update_or_create(
            template=template,
            user=request.user,
            defaults={
                "score": serializer.validated_data["score"],
                "comment": serializer.validated_data.get("comment", ""),
            },
        )

        # Update average rating
        avg = template.ratings.aggregate(avg=Avg("score"))["avg"] or 0
        template.average_rating = round(avg, 2)
        template.save(update_fields=["average_rating"])

        return Response(
            TemplateRatingSerializer(rating).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )
