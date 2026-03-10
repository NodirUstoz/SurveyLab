import csv
import io
import logging
import uuid

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.surveys.models import Question, QuestionOption, Survey, SurveySettings
from apps.surveys.services import SurveyService
from .models import Answer, ResponseSession, SurveyResponse
from .serializers import (
    ExportRequestSerializer,
    ResponseSessionSerializer,
    SavePartialResponseSerializer,
    SubmitResponseSerializer,
    SurveyResponseListSerializer,
    SurveyResponseSerializer,
)
from .tasks import process_response_analytics, send_response_notification

logger = logging.getLogger(__name__)


class SubmitResponseView(APIView):
    """
    Submit a complete survey response.
    Open to anonymous users when survey allows it.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SubmitResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            survey = Survey.objects.select_related("settings").get(
                id=data["survey_id"], status=Survey.Status.PUBLISHED
            )
        except Survey.DoesNotExist:
            return Response(
                {"detail": "Survey not found or not published."},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Check survey closure
        if survey.closes_at and survey.closes_at < timezone.now():
            return Response(
                {"detail": "This survey has closed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check quotas
        try:
            settings_obj = survey.settings
            if not settings_obj.check_quota():
                return Response(
                    {"detail": "This survey has reached its response limit."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except SurveySettings.DoesNotExist:
            pass

        # Check one-response-per-user
        if hasattr(survey, "settings") and survey.settings.one_response_per_user:
            if request.user.is_authenticated:
                if SurveyResponse.objects.filter(
                    survey=survey, respondent=request.user
                ).exists():
                    return Response(
                        {"detail": "You have already responded to this survey."},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

        # Validate required questions
        required_questions = Question.objects.filter(
            page__survey=survey, is_required=True
        ).values_list("id", flat=True)
        answered_ids = {
            a["question_id"] for a in data["answers"]
        }
        missing = set(str(q) for q in required_questions) - set(str(a) for a in answered_ids)
        if missing:
            return Response(
                {"detail": "Required questions not answered.", "missing": list(missing)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Determine respondent
        respondent = request.user if request.user.is_authenticated else None
        ip_address = self._get_client_ip(request)

        # Create response
        survey_response = SurveyResponse.objects.create(
            survey=survey,
            respondent=respondent,
            status=SurveyResponse.Status.COMPLETE,
            ip_address=ip_address,
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            language=data.get("language", "en"),
            duration_seconds=data.get("duration_seconds"),
            metadata=data.get("metadata", {}),
        )

        # Link session if exists
        session_key = data.get("session_key")
        if session_key:
            ResponseSession.objects.filter(session_key=session_key).update(
                is_completed=True
            )
            session = ResponseSession.objects.filter(session_key=session_key).first()
            if session:
                survey_response.session = session
                survey_response.save(update_fields=["session"])

        # Save answers
        for answer_data in data["answers"]:
            answer = Answer.objects.create(
                response=survey_response,
                question_id=answer_data["question_id"],
                text_value=answer_data.get("text_value", ""),
                numeric_value=answer_data.get("numeric_value"),
                matrix_values=answer_data.get("matrix_values", {}),
                ranking_values=answer_data.get("ranking_values", []),
            )
            # Set selected options for choice-based questions
            selected_ids = answer_data.get("selected_option_ids", [])
            if selected_ids:
                options = QuestionOption.objects.filter(id__in=selected_ids)
                answer.selected_options.set(options)
                # Update quota counts
                for opt in options:
                    if opt.quota_limit is not None:
                        QuestionOption.objects.filter(id=opt.id).update(
                            quota_count=models.F("quota_count") + 1
                        )

        # Trigger async analytics and notifications
        process_response_analytics.delay(str(survey_response.id))
        try:
            if survey.settings.notify_on_response:
                send_response_notification.delay(str(survey_response.id))
        except SurveySettings.DoesNotExist:
            pass

        return Response(
            {
                "detail": "Response submitted successfully.",
                "response_id": str(survey_response.id),
            },
            status=status.HTTP_201_CREATED,
        )

    def _get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class SavePartialResponseView(APIView):
    """Save partial response data for resumption later."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = SavePartialResponseSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            survey = Survey.objects.get(
                id=data["survey_id"], status=Survey.Status.PUBLISHED
            )
        except Survey.DoesNotExist:
            return Response(
                {"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND
            )

        session, created = ResponseSession.objects.update_or_create(
            session_key=data["session_key"],
            defaults={
                "survey": survey,
                "respondent": request.user if request.user.is_authenticated else None,
                "current_page": data.get("current_page", 0),
                "partial_data": {
                    "answers": [
                        {
                            "question_id": str(a["question_id"]),
                            "text_value": a.get("text_value", ""),
                            "numeric_value": a.get("numeric_value"),
                            "selected_option_ids": [str(i) for i in a.get("selected_option_ids", [])],
                            "matrix_values": a.get("matrix_values", {}),
                            "ranking_values": [str(i) for i in a.get("ranking_values", [])],
                        }
                        for a in data.get("answers", [])
                    ]
                },
                "ip_address": request.META.get("REMOTE_ADDR"),
                "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                "language": data.get("language", "en"),
            },
        )

        return Response(
            ResponseSessionSerializer(session).data,
            status=status.HTTP_200_OK if not created else status.HTTP_201_CREATED,
        )


class ResumeSessionView(generics.RetrieveAPIView):
    """Resume a partial response session by session key."""

    serializer_class = ResponseSessionSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "session_key"

    def get_queryset(self):
        return ResponseSession.objects.filter(is_completed=False)


class SurveyResponseListView(generics.ListAPIView):
    """List all responses for a survey owned by the authenticated user."""

    serializer_class = SurveyResponseListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["status", "language"]
    ordering_fields = ["submitted_at", "duration_seconds"]

    def get_queryset(self):
        survey_id = self.kwargs["survey_id"]
        return SurveyResponse.objects.filter(
            survey_id=survey_id,
            survey__owner=self.request.user,
        ).prefetch_related("answers")


class SurveyResponseDetailView(generics.RetrieveDestroyAPIView):
    """Retrieve or delete a single survey response."""

    serializer_class = SurveyResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return SurveyResponse.objects.filter(
            survey__owner=self.request.user
        ).prefetch_related("answers__selected_options", "answers__question")


class ExportResponsesView(APIView):
    """Export survey responses in CSV, XLSX, or PDF format."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, survey_id):
        serializer = ExportRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        try:
            survey = Survey.objects.get(id=survey_id, owner=request.user)
        except Survey.DoesNotExist:
            return Response(
                {"detail": "Survey not found."}, status=status.HTTP_404_NOT_FOUND
            )

        responses = SurveyResponse.objects.filter(survey=survey)

        if data.get("status_filter") and data["status_filter"] != "all":
            responses = responses.filter(status=data["status_filter"])
        if data.get("date_from"):
            responses = responses.filter(submitted_at__gte=data["date_from"])
        if data.get("date_to"):
            responses = responses.filter(submitted_at__lte=data["date_to"])

        responses = responses.prefetch_related(
            "answers__question", "answers__selected_options"
        )

        questions = Question.objects.filter(
            page__survey=survey
        ).order_by("page__order", "order")

        export_format = data.get("format", "csv")

        if export_format == "csv":
            return self._export_csv(survey, responses, questions)
        elif export_format == "xlsx":
            return self._export_xlsx(survey, responses, questions)
        else:
            return Response(
                {"detail": f"Format '{export_format}' export is available via async task."},
                status=status.HTTP_200_OK,
            )

    def _export_csv(self, survey, responses, questions):
        output = io.StringIO()
        writer = csv.writer(output)

        # Header row
        header = ["Response ID", "Status", "Language", "Duration (s)", "Submitted At"]
        for q in questions:
            header.append(q.text[:50])
        writer.writerow(header)

        # Data rows
        for resp in responses:
            row = [
                str(resp.id),
                resp.status,
                resp.language,
                resp.duration_seconds or "",
                resp.submitted_at.isoformat(),
            ]
            answer_map = {
                str(a.question_id): a for a in resp.answers.all()
            }
            for q in questions:
                answer = answer_map.get(str(q.id))
                row.append(answer.display_value if answer else "")
            writer.writerow(row)

        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="{survey.slug}-responses.csv"'
        )
        return response

    def _export_xlsx(self, survey, responses, questions):
        from openpyxl import Workbook

        wb = Workbook()
        ws = wb.active
        ws.title = "Responses"

        header = ["Response ID", "Status", "Language", "Duration (s)", "Submitted At"]
        for q in questions:
            header.append(q.text[:50])
        ws.append(header)

        for resp in responses:
            row = [
                str(resp.id),
                resp.status,
                resp.language,
                resp.duration_seconds or "",
                resp.submitted_at.isoformat(),
            ]
            answer_map = {
                str(a.question_id): a for a in resp.answers.all()
            }
            for q in questions:
                answer = answer_map.get(str(q.id))
                row.append(answer.display_value if answer else "")
            ws.append(row)

        output = io.BytesIO()
        wb.save(output)
        output.seek(0)

        response = HttpResponse(
            output.getvalue(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = (
            f'attachment; filename="{survey.slug}-responses.xlsx"'
        )
        return response
