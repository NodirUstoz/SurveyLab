"""Service for creating and dispatching notifications."""
import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Notification, NotificationPreference

logger = logging.getLogger(__name__)


class NotificationService:
    """Centralized service for creating notifications."""

    @staticmethod
    def create_notification(
        recipient,
        notification_type,
        title,
        message,
        priority="normal",
        action_url="",
        related_survey=None,
        metadata=None,
    ):
        """Create an in-app notification and optionally send an email."""
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            priority=priority,
            title=title,
            message=message,
            action_url=action_url,
            related_survey=related_survey,
            metadata=metadata or {},
        )

        # Check if email notification should be sent
        try:
            prefs = NotificationPreference.objects.get(user=recipient)
        except NotificationPreference.DoesNotExist:
            prefs = None

        should_email = NotificationService._should_send_email(
            notification_type, prefs, recipient
        )

        if should_email:
            NotificationService._send_email_notification(
                recipient, title, message
            )

        return notification

    @staticmethod
    def _should_send_email(notification_type, prefs, user):
        """Determine if an email should be sent based on preferences."""
        if not user.email_notifications:
            return False

        if prefs is None:
            return True

        type_pref_map = {
            "response_received": prefs.email_on_response,
            "quota_reached": prefs.email_on_quota,
            "survey_closed": prefs.email_on_survey_close,
        }

        return type_pref_map.get(notification_type, True)

    @staticmethod
    def _send_email_notification(recipient, title, message):
        """Send an email notification."""
        try:
            send_mail(
                subject=f"SurveyLab: {title}",
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient.email],
                fail_silently=True,
            )
        except Exception as exc:
            logger.error(
                f"Failed to send email notification to {recipient.email}: {exc}"
            )

    @staticmethod
    def notify_response_received(survey, response):
        """Create notification when a new survey response is received."""
        NotificationService.create_notification(
            recipient=survey.owner,
            notification_type=Notification.NotificationType.RESPONSE_RECEIVED,
            title=f"New response for '{survey.title}'",
            message=(
                f"A new response has been submitted for your survey "
                f"'{survey.title}'. Total responses: {survey.response_count}."
            ),
            action_url=f"/surveys/{survey.id}/responses/{response.id}",
            related_survey=survey,
            metadata={
                "response_id": str(response.id),
                "response_status": response.status,
            },
        )

    @staticmethod
    def notify_quota_reached(survey):
        """Create notification when a survey reaches its response quota."""
        NotificationService.create_notification(
            recipient=survey.owner,
            notification_type=Notification.NotificationType.QUOTA_REACHED,
            title=f"Quota reached for '{survey.title}'",
            message=(
                f"Your survey '{survey.title}' has reached its maximum "
                f"number of responses and will no longer accept new submissions."
            ),
            priority="high",
            action_url=f"/surveys/{survey.id}/settings",
            related_survey=survey,
        )

    @staticmethod
    def notify_export_ready(user, survey, export_url):
        """Create notification when a data export is ready for download."""
        NotificationService.create_notification(
            recipient=user,
            notification_type=Notification.NotificationType.EXPORT_READY,
            title=f"Export ready for '{survey.title}'",
            message=(
                f"Your data export for survey '{survey.title}' is ready "
                f"for download."
            ),
            action_url=export_url,
            related_survey=survey,
        )
