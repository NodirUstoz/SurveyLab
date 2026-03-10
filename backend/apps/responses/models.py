import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ResponseSession(models.Model):
    """
    Tracks an in-progress survey session, enabling partial saves
    and resumption of incomplete responses.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name=_("survey"),
    )
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_sessions",
        verbose_name=_("respondent"),
    )
    session_key = models.CharField(
        _("session key"), max_length=255, unique=True, db_index=True
    )
    current_page = models.IntegerField(_("current page index"), default=0)
    partial_data = models.JSONField(_("partial data"), default=dict, blank=True)
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True, default="")
    language = models.CharField(_("response language"), max_length=10, default="en")
    started_at = models.DateTimeField(_("started at"), auto_now_add=True)
    last_activity = models.DateTimeField(_("last activity"), auto_now=True)
    is_completed = models.BooleanField(_("completed"), default=False)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = _("response session")
        verbose_name_plural = _("response sessions")

    def __str__(self):
        return f"Session {self.session_key} for {self.survey.title}"


class SurveyResponse(models.Model):
    """A complete submitted response to a survey."""

    class Status(models.TextChoices):
        COMPLETE = "complete", _("Complete")
        PARTIAL = "partial", _("Partial")
        DISQUALIFIED = "disqualified", _("Disqualified")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.CASCADE,
        related_name="responses",
        verbose_name=_("survey"),
    )
    session = models.OneToOneField(
        ResponseSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="response",
        verbose_name=_("session"),
    )
    respondent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="survey_responses",
        verbose_name=_("respondent"),
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.COMPLETE,
    )
    ip_address = models.GenericIPAddressField(_("IP address"), null=True, blank=True)
    user_agent = models.TextField(_("user agent"), blank=True, default="")
    language = models.CharField(_("response language"), max_length=10, default="en")
    duration_seconds = models.IntegerField(
        _("duration (seconds)"), null=True, blank=True
    )
    metadata = models.JSONField(_("metadata"), default=dict, blank=True)
    submitted_at = models.DateTimeField(_("submitted at"), auto_now_add=True)

    class Meta:
        ordering = ["-submitted_at"]
        verbose_name = _("survey response")
        verbose_name_plural = _("survey responses")

    def __str__(self):
        return f"Response {self.id} for {self.survey.title}"


class Answer(models.Model):
    """An individual answer to a question within a response."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("response"),
    )
    question = models.ForeignKey(
        "surveys.Question",
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name=_("question"),
    )
    # Flexible storage: use the appropriate field based on question type
    text_value = models.TextField(_("text value"), blank=True, default="")
    numeric_value = models.FloatField(_("numeric value"), null=True, blank=True)
    selected_options = models.ManyToManyField(
        "surveys.QuestionOption",
        blank=True,
        related_name="answers",
        verbose_name=_("selected options"),
    )
    # For matrix questions: {"row_label": "column_value", ...}
    matrix_values = models.JSONField(
        _("matrix values"), default=dict, blank=True
    )
    # For file uploads
    file_upload = models.FileField(
        _("file upload"), upload_to="responses/files/", blank=True, null=True
    )
    # For ranking questions: ordered list of option IDs
    ranking_values = models.JSONField(
        _("ranking values"), default=list, blank=True
    )
    answered_at = models.DateTimeField(_("answered at"), auto_now_add=True)

    class Meta:
        ordering = ["answered_at"]
        verbose_name = _("answer")
        verbose_name_plural = _("answers")
        unique_together = [("response", "question")]

    def __str__(self):
        return f"Answer to Q({self.question_id}) in R({self.response_id})"

    @property
    def display_value(self):
        """Return a human-readable representation of the answer."""
        if self.numeric_value is not None:
            return str(self.numeric_value)
        if self.text_value:
            return self.text_value
        if self.matrix_values:
            return str(self.matrix_values)
        selected = self.selected_options.all()
        if selected.exists():
            return ", ".join(opt.text for opt in selected)
        if self.ranking_values:
            return str(self.ranking_values)
        return ""
