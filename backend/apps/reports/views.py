import secrets

from rest_framework import generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Report, ScheduledReport
from .serializers import (
    ReportCreateSerializer,
    ReportListSerializer,
    ReportSerializer,
    ScheduledReportSerializer,
    ShareReportSerializer,
)


class ReportViewSet(viewsets.ModelViewSet):
    """CRUD for survey reports."""

    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Report.objects.filter(
            created_by=self.request.user
        ).select_related("survey")

    def get_serializer_class(self):
        if self.action == "list":
            return ReportListSerializer
        if self.action == "create":
            return ReportCreateSerializer
        return ReportSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["post"])
    def generate(self, request, pk=None):
        """Trigger report generation."""
        report = self.get_object()
        if report.status == "generating":
            return Response(
                {"detail": "Report is already being generated."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        report.status = Report.Status.GENERATING
        report.save(update_fields=["status"])

        from .tasks import generate_report
        generate_report.delay(str(report.id))

        return Response(
            {"detail": "Report generation started."},
            status=status.HTTP_202_ACCEPTED,
        )

    @action(detail=True, methods=["post"])
    def share(self, request, pk=None):
        """Share or unshare a report via a public link."""
        report = self.get_object()
        serializer = ShareReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.validated_data["is_shared"]:
            if not report.share_token:
                report.share_token = secrets.token_urlsafe(32)
            report.is_shared = True
            password = serializer.validated_data.get("password", "")
            if password:
                from django.contrib.auth.hashers import make_password
                report.share_password = make_password(password)
            report.save(update_fields=[
                "is_shared", "share_token", "share_password"
            ])
            return Response({
                "share_url": f"https://app.surveylab.io/reports/shared/{report.share_token}",
                "share_token": report.share_token,
            })
        else:
            report.is_shared = False
            report.save(update_fields=["is_shared"])
            return Response({"detail": "Report sharing disabled."})

    @action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        """Get download URL for a generated report."""
        report = self.get_object()
        if report.status != "ready" or not report.file:
            return Response(
                {"detail": "Report is not ready for download."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({
            "download_url": request.build_absolute_uri(report.file.url),
            "file_size_bytes": report.file_size_bytes,
        })


class SurveyReportsView(generics.ListAPIView):
    """List all reports for a specific survey."""

    serializer_class = ReportListSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        survey_id = self.kwargs["survey_id"]
        return Report.objects.filter(
            survey_id=survey_id,
            created_by=self.request.user,
        ).select_related("survey")


class ScheduledReportViewSet(viewsets.ModelViewSet):
    """CRUD for scheduled reports."""

    serializer_class = ScheduledReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ScheduledReport.objects.filter(
            created_by=self.request.user
        ).select_related("survey")

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class SharedReportView(APIView):
    """Public endpoint to view a shared report."""

    permission_classes = [permissions.AllowAny]

    def get(self, request, share_token):
        try:
            report = Report.objects.select_related("survey").get(
                share_token=share_token, is_shared=True
            )
        except Report.DoesNotExist:
            return Response(
                {"detail": "Report not found or sharing disabled."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if report.share_password:
            password = request.query_params.get("password", "")
            from django.contrib.auth.hashers import check_password
            if not check_password(password, report.share_password):
                return Response(
                    {"detail": "Invalid password.", "password_required": True},
                    status=status.HTTP_403_FORBIDDEN,
                )

        return Response(ReportSerializer(report).data)
