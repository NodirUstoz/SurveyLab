import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Report(models.Model):
    """A generated report for survey results."""

    class ReportType(models.TextChoices):
        SUMMARY = "summary", _("Summary Report")
        DETAILED = "detailed", _("Detailed Report")
        EXECUTIVE = "executive", _("Executive Summary")
        CROSS_TAB = "cross_tab", _("Cross-Tabulation Report")
        TREND = "trend", _("Trend Analysis Report")
        COMPARISON = "comparison", _("Survey Comparison Report")
        CUSTOM = "custom", _("Custom Report")

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        GENERATING = "generating", _("Generating")
        READY = "ready", _("Ready")
        FAILED = "failed", _("Failed")

    class Format(models.TextChoices):
        PDF = "pdf", _("PDF")
        DOCX = "docx", _("Word Document")
        PPTX = "pptx", _("PowerPoint")
        HTML = "html", _("HTML")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("survey"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="reports",
        verbose_name=_("created by"),
    )
    title = models.CharField(_("report title"), max_length=500)
    report_type = models.CharField(
        _("report type"),
        max_length=20,
        choices=ReportType.choices,
        default=ReportType.SUMMARY,
    )
    output_format = models.CharField(
        _("output format"),
        max_length=10,
        choices=Format.choices,
        default=Format.PDF,
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    # Report configuration
    config = models.JSONField(_("report config"), default=dict, blank=True)
    # Sections to include
    include_summary = models.BooleanField(_("include summary"), default=True)
    include_charts = models.BooleanField(_("include charts"), default=True)
    include_individual_responses = models.BooleanField(
        _("include individual responses"), default=False
    )
    include_open_ended = models.BooleanField(
        _("include open-ended responses"), default=True
    )
    include_cross_tabs = models.BooleanField(
        _("include cross-tabulations"), default=False
    )
    # Filters
    date_range_start = models.DateTimeField(
        _("date range start"), null=True, blank=True
    )
    date_range_end = models.DateTimeField(
        _("date range end"), null=True, blank=True
    )
    response_status_filter = models.CharField(
        _("response status filter"), max_length=20, default="all"
    )
    # Generated file
    file = models.FileField(
        _("report file"), upload_to="reports/files/", blank=True, null=True
    )
    file_size_bytes = models.BigIntegerField(
        _("file size (bytes)"), null=True, blank=True
    )
    # Sharing
    is_shared = models.BooleanField(_("shared"), default=False)
    share_token = models.CharField(
        _("share token"), max_length=64, blank=True, default=""
    )
    share_password = models.CharField(
        _("share password"), max_length=128, blank=True, default=""
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    generated_at = models.DateTimeField(
        _("generated at"), null=True, blank=True
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("report")
        verbose_name_plural = _("reports")

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"


class ScheduledReport(models.Model):
    """Scheduled recurring report generation and delivery."""

    class Frequency(models.TextChoices):
        DAILY = "daily", _("Daily")
        WEEKLY = "weekly", _("Weekly")
        BIWEEKLY = "biweekly", _("Bi-Weekly")
        MONTHLY = "monthly", _("Monthly")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.CASCADE,
        related_name="scheduled_reports",
        verbose_name=_("survey"),
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="scheduled_reports",
        verbose_name=_("created by"),
    )
    report_type = models.CharField(
        _("report type"),
        max_length=20,
        choices=Report.ReportType.choices,
        default=Report.ReportType.SUMMARY,
    )
    output_format = models.CharField(
        _("output format"),
        max_length=10,
        choices=Report.Format.choices,
        default=Report.Format.PDF,
    )
    frequency = models.CharField(
        _("frequency"),
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.WEEKLY,
    )
    recipient_emails = models.JSONField(
        _("recipient emails"), default=list, blank=True
    )
    is_active = models.BooleanField(_("active"), default=True)
    last_generated_at = models.DateTimeField(
        _("last generated at"), null=True, blank=True
    )
    next_scheduled_at = models.DateTimeField(
        _("next scheduled at"), null=True, blank=True
    )
    config = models.JSONField(
        _("report config"), default=dict, blank=True
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("scheduled report")
        verbose_name_plural = _("scheduled reports")

    def __str__(self):
        return (
            f"Scheduled {self.get_report_type_display()} for "
            f"{self.survey.title} ({self.get_frequency_display()})"
        )
