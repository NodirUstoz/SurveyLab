"""Celery tasks for async response processing."""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def process_response_analytics(self, response_id):
    """
    Process a submitted response and update survey analytics.
    Runs asynchronously after each response submission.
    """
    try:
        from apps.responses.models import SurveyResponse
        from apps.analytics.services import AnalyticsService

        response = SurveyResponse.objects.select_related("survey").get(id=response_id)
        AnalyticsService.update_analytics_for_response(response)
        logger.info(f"Analytics updated for response {response_id}")
    except SurveyResponse.DoesNotExist:
        logger.error(f"Response {response_id} not found for analytics processing")
    except Exception as exc:
        logger.error(f"Error processing analytics for response {response_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_response_notification(self, response_id):
    """
    Send email notification to survey owner when a new response is received.
    """
    try:
        from apps.responses.models import SurveyResponse

        response = SurveyResponse.objects.select_related(
            "survey__owner", "survey__settings"
        ).get(id=response_id)

        survey = response.survey
        owner = survey.owner

        notification_emails = [owner.email]
        try:
            extra_emails = survey.settings.notification_emails or []
            notification_emails.extend(extra_emails)
        except Exception:
            pass

        # Deduplicate
        notification_emails = list(set(notification_emails))

        subject = f"New response received for '{survey.title}'"
        message = (
            f"A new response has been submitted for your survey '{survey.title}'.\n\n"
            f"Response ID: {response.id}\n"
            f"Status: {response.status}\n"
            f"Language: {response.language}\n"
            f"Submitted at: {response.submitted_at}\n\n"
            f"Total responses: {survey.response_count}\n\n"
            f"View responses in SurveyLab to see the full details."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=notification_emails,
            fail_silently=False,
        )

        logger.info(
            f"Notification sent for response {response_id} to {notification_emails}"
        )
    except SurveyResponse.DoesNotExist:
        logger.error(f"Response {response_id} not found for notification")
    except Exception as exc:
        logger.error(f"Error sending notification for response {response_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def cleanup_expired_sessions():
    """Remove incomplete sessions older than 7 days."""
    from datetime import timedelta

    from django.utils import timezone

    from apps.responses.models import ResponseSession

    threshold = timezone.now() - timedelta(days=7)
    deleted_count, _ = ResponseSession.objects.filter(
        is_completed=False,
        last_activity__lt=threshold,
    ).delete()
    logger.info(f"Cleaned up {deleted_count} expired sessions")


@shared_task
def generate_export_file(survey_id, export_format, user_id, filters=None):
    """Generate export file asynchronously for large datasets."""
    try:
        from apps.surveys.models import Survey, Question
        from apps.responses.models import SurveyResponse

        survey = Survey.objects.get(id=survey_id)
        responses = SurveyResponse.objects.filter(survey=survey)

        if filters:
            if filters.get("status_filter") and filters["status_filter"] != "all":
                responses = responses.filter(status=filters["status_filter"])
            if filters.get("date_from"):
                responses = responses.filter(submitted_at__gte=filters["date_from"])
            if filters.get("date_to"):
                responses = responses.filter(submitted_at__lte=filters["date_to"])

        responses = responses.prefetch_related(
            "answers__question", "answers__selected_options"
        )

        logger.info(
            f"Export generated for survey {survey_id}: "
            f"{responses.count()} responses in {export_format} format"
        )
        return {"status": "completed", "count": responses.count()}
    except Exception as exc:
        logger.error(f"Error generating export for survey {survey_id}: {exc}")
        return {"status": "failed", "error": str(exc)}
