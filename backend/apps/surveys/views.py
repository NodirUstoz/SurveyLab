from django.utils.text import slugify
from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import (
    BranchingRule,
    Question,
    QuestionOption,
    Survey,
    SurveyPage,
    SurveySettings,
)
from .serializers import (
    BranchingRuleSerializer,
    PublicSurveySerializer,
    QuestionCreateUpdateSerializer,
    QuestionOptionSerializer,
    QuestionSerializer,
    SurveyCreateSerializer,
    SurveyDetailSerializer,
    SurveyListSerializer,
    SurveyPageSerializer,
    SurveySettingsSerializer,
)
from .services import SurveyService


class SurveyViewSet(viewsets.ModelViewSet):
    """CRUD operations for surveys owned by the authenticated user."""

    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "category"]
    search_fields = ["title", "description", "tags"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        return Survey.objects.filter(
            owner=self.request.user
        ).select_related("settings", "owner").prefetch_related("pages__questions__options")

    def get_serializer_class(self):
        if self.action == "list":
            return SurveyListSerializer
        if self.action == "create":
            return SurveyCreateSerializer
        return SurveyDetailSerializer

    def perform_create(self, serializer):
        title = serializer.validated_data.get("title", "")
        slug = serializer.validated_data.get("slug") or slugify(title)
        # Ensure unique slug
        base_slug = slug
        counter = 1
        while Survey.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        serializer.save(
            owner=self.request.user,
            organization=self.request.user.organization,
            slug=slug,
        )

    @action(detail=True, methods=["post"])
    def publish(self, request, pk=None):
        survey = self.get_object()
        success, errors = SurveyService.publish_survey(survey)
        if success:
            return Response(
                SurveyDetailSerializer(survey).data, status=status.HTTP_200_OK
            )
        return Response({"errors": errors}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        survey = self.get_object()
        SurveyService.close_survey(survey)
        return Response(SurveyDetailSerializer(survey).data)

    @action(detail=True, methods=["post"])
    def duplicate(self, request, pk=None):
        survey = self.get_object()
        new_survey = SurveyService.duplicate_survey(survey, new_owner=request.user)
        return Response(
            SurveyDetailSerializer(new_survey).data,
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["post"], url_path="reorder-pages")
    def reorder_pages(self, request, pk=None):
        survey = self.get_object()
        page_order = request.data.get("page_order", [])
        SurveyService.reorder_pages(survey, page_order)
        return Response({"detail": "Pages reordered."})

    @action(detail=True, methods=["get", "put", "patch"])
    def settings(self, request, pk=None):
        survey = self.get_object()
        try:
            settings_obj = survey.settings
        except SurveySettings.DoesNotExist:
            settings_obj = SurveySettings.objects.create(survey=survey)

        if request.method == "GET":
            return Response(SurveySettingsSerializer(settings_obj).data)

        serializer = SurveySettingsSerializer(
            settings_obj, data=request.data, partial=(request.method == "PATCH")
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class SurveyPageViewSet(viewsets.ModelViewSet):
    """CRUD for survey pages."""

    serializer_class = SurveyPageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SurveyPage.objects.filter(
            survey__owner=self.request.user,
            survey_id=self.kwargs.get("survey_pk"),
        ).prefetch_related("questions__options")

    def perform_create(self, serializer):
        survey = Survey.objects.get(
            pk=self.kwargs["survey_pk"], owner=self.request.user
        )
        max_order = survey.pages.count()
        serializer.save(survey=survey, order=max_order)

    @action(detail=True, methods=["post"], url_path="reorder-questions")
    def reorder_questions(self, request, survey_pk=None, pk=None):
        page = self.get_object()
        question_order = request.data.get("question_order", [])
        SurveyService.reorder_questions(page, question_order)
        return Response({"detail": "Questions reordered."})


class QuestionViewSet(viewsets.ModelViewSet):
    """CRUD for questions within a survey page."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Question.objects.filter(
            page__survey__owner=self.request.user,
            page_id=self.kwargs.get("page_pk"),
        ).prefetch_related("options")

    def get_serializer_class(self):
        if self.action in ("create", "update", "partial_update"):
            return QuestionCreateUpdateSerializer
        return QuestionSerializer

    def perform_create(self, serializer):
        page = SurveyPage.objects.get(
            pk=self.kwargs["page_pk"],
            survey__owner=self.request.user,
        )
        max_order = page.questions.count()
        serializer.save(page=page, order=max_order)


class QuestionOptionViewSet(viewsets.ModelViewSet):
    """CRUD for question options."""

    serializer_class = QuestionOptionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return QuestionOption.objects.filter(
            question__page__survey__owner=self.request.user,
            question_id=self.kwargs.get("question_pk"),
        )

    def perform_create(self, serializer):
        question = Question.objects.get(
            pk=self.kwargs["question_pk"],
            page__survey__owner=self.request.user,
        )
        max_order = question.options.count()
        serializer.save(question=question, order=max_order)


class BranchingRuleViewSet(viewsets.ModelViewSet):
    """CRUD for branching rules within a survey."""

    serializer_class = BranchingRuleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return BranchingRule.objects.filter(
            survey__owner=self.request.user,
            survey_id=self.kwargs.get("survey_pk"),
        )

    def perform_create(self, serializer):
        survey = Survey.objects.get(
            pk=self.kwargs["survey_pk"], owner=self.request.user
        )
        serializer.save(survey=survey)


class PublicSurveyView(generics.RetrieveAPIView):
    """Public endpoint for respondents to load a survey by slug."""

    serializer_class = PublicSurveySerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    def get_queryset(self):
        return Survey.objects.filter(
            status=Survey.Status.PUBLISHED
        ).select_related("settings").prefetch_related(
            "pages__questions__options"
        )
