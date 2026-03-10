from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.surveys.models import Question, Survey
from .models import CrossTabulation, SurveyAnalytics
from .serializers import (
    CrossTabulationRequestSerializer,
    CrossTabulationSerializer,
    SurveyAnalyticsSerializer,
    SurveyAnalyticsSummarySerializer,
)
from .services import AnalyticsService


class SurveyAnalyticsView(generics.RetrieveAPIView):
    """Retrieve full analytics for a specific survey."""

    serializer_class = SurveyAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        survey_id = self.kwargs["survey_id"]
        survey = Survey.objects.get(id=survey_id, owner=self.request.user)
        analytics, created = SurveyAnalytics.objects.get_or_create(survey=survey)
        if created:
            AnalyticsService._update_survey_level_stats(analytics, survey)
            AnalyticsService._update_question_stats(analytics, survey)
        return analytics


class SurveyAnalyticsRefreshView(APIView):
    """Force a full analytics recomputation for a survey."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, survey_id):
        try:
            survey = Survey.objects.get(id=survey_id, owner=request.user)
        except Survey.DoesNotExist:
            return Response(
                {"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND
            )

        analytics, _ = SurveyAnalytics.objects.get_or_create(survey=survey)
        AnalyticsService._update_survey_level_stats(analytics, survey)
        AnalyticsService._update_question_stats(analytics, survey)

        return Response(
            SurveyAnalyticsSerializer(analytics).data, status=status.HTTP_200_OK
        )


class DashboardAnalyticsView(generics.ListAPIView):
    """Dashboard view: summary analytics for all surveys owned by user."""

    serializer_class = SurveyAnalyticsSummarySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SurveyAnalytics.objects.filter(
            survey__owner=self.request.user
        ).select_related("survey").order_by("-updated_at")


class CrossTabulationView(APIView):
    """Compute or retrieve cross-tabulation between two questions."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, survey_id):
        """List existing cross-tabulations for a survey."""
        cross_tabs = CrossTabulation.objects.filter(
            survey_id=survey_id, survey__owner=request.user
        ).select_related("question_a", "question_b")

        return Response(
            CrossTabulationSerializer(cross_tabs, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, survey_id):
        """Create a new cross-tabulation analysis."""
        serializer = CrossTabulationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            survey = Survey.objects.get(id=survey_id, owner=request.user)
        except Survey.DoesNotExist:
            return Response(
                {"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            question_a = Question.objects.get(
                id=serializer.validated_data["question_a_id"],
                page__survey=survey,
            )
            question_b = Question.objects.get(
                id=serializer.validated_data["question_b_id"],
                page__survey=survey,
            )
        except Question.DoesNotExist:
            return Response(
                {"detail": "One or both questions not found in this survey."},
                status=status.HTTP_404_NOT_FOUND,
            )

        cross_tab = AnalyticsService.compute_cross_tabulation(
            survey, question_a, question_b
        )

        return Response(
            CrossTabulationSerializer(cross_tab).data,
            status=status.HTTP_201_CREATED,
        )
