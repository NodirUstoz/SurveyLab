import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    """In-app notification for a user."""

    class NotificationType(models.TextChoices):
        RESPONSE_RECEIVED = "response_received", _("New Response Received")
        SURVEY_PUBLISHED = "survey_published", _("Survey Published")
        SURVEY_CLOSED = "survey_closed", _("Survey Closed")
        QUOTA_REACHED = "quota_reached", _("Response Quota Reached")
        EXPORT_READY = "export_ready", _("Export Ready")
        CAMPAIGN_SENT = "campaign_sent", _("Campaign Sent")
        TEAM_INVITE = "team_invite", _("Team Invitation")
        SYSTEM = "system", _("System Notification")

    class Priority(models.TextChoices):
        LOW = "low", _("Low")
        NORMAL = "normal", _("Normal")
        HIGH = "high", _("High")
        URGENT = "urgent", _("Urgent")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("recipient"),
    )
    notification_type = models.CharField(
        _("type"),
        max_length=30,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
    )
    priority = models.CharField(
        _("priority"),
        max_length=10,
        choices=Priority.choices,
        default=Priority.NORMAL,
    )
    title = models.CharField(_("title"), max_length=500)
    message = models.TextField(_("message"))
    # Optional link to related resource
    action_url = models.URLField(_("action URL"), blank=True, default="")
    # Reference to related objects
    related_survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="notifications",
        verbose_name=_("related survey"),
    )
    metadata = models.JSONField(_("metadata"), default=dict, blank=True)
    is_read = models.BooleanField(_("read"), default=False)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("notification")
        verbose_name_plural = _("notifications")
        indexes = [
            models.Index(
                fields=["recipient", "is_read", "-created_at"],
                name="idx_notif_recipient_unread",
            ),
        ]

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title[:60]}"


class NotificationPreference(models.Model):
    """Per-user notification delivery preferences."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notification_preferences",
        verbose_name=_("user"),
    )
    email_on_response = models.BooleanField(
        _("email on new response"), default=True
    )
    email_on_quota = models.BooleanField(
        _("email on quota reached"), default=True
    )
    email_on_survey_close = models.BooleanField(
        _("email when survey closes"), default=True
    )
    email_digest = models.CharField(
        _("email digest frequency"),
        max_length=20,
        choices=[
            ("none", "None"),
            ("daily", "Daily"),
            ("weekly", "Weekly"),
        ],
        default="daily",
    )
    in_app_enabled = models.BooleanField(
        _("in-app notifications"), default=True
    )
    quiet_hours_start = models.TimeField(
        _("quiet hours start"), null=True, blank=True
    )
    quiet_hours_end = models.TimeField(
        _("quiet hours end"), null=True, blank=True
    )

    class Meta:
        verbose_name = _("notification preference")
        verbose_name_plural = _("notification preferences")

    def __str__(self):
        return f"Notification prefs for {self.user.email}"
