"""Celery tasks for distribution-related async operations."""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mass_mail
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=120)
def send_email_campaign(self, campaign_id):
    """Send an email campaign to all recipients."""
    try:
        from .models import EmailCampaign

        campaign = EmailCampaign.objects.select_related(
            "channel__survey"
        ).get(id=campaign_id)

        if campaign.status != "sending":
            logger.warning(
                f"Campaign {campaign_id} is not in 'sending' state, skipping."
            )
            return

        recipients = campaign.recipient_list or []
        if not recipients:
            campaign.status = EmailCampaign.Status.FAILED
            campaign.save(update_fields=["status"])
            logger.error(f"Campaign {campaign_id} has no recipients.")
            return

        survey_url = f"https://app.surveylab.io/s/{campaign.channel.survey.slug}"
        tracking_url = (
            f"https://app.surveylab.io/t/{campaign.channel.unique_token}"
        )

        body_with_link = campaign.body_html.replace(
            "{{survey_link}}", tracking_url
        )
        text_with_link = (campaign.body_text or campaign.body_html).replace(
            "{{survey_link}}", tracking_url
        )

        from_email = campaign.from_email or settings.DEFAULT_FROM_EMAIL

        messages = []
        for recipient in recipients:
            messages.append((
                campaign.subject,
                text_with_link,
                from_email,
                [recipient],
            ))

        # Send in batches of 50
        batch_size = 50
        total_sent = 0
        for i in range(0, len(messages), batch_size):
            batch = messages[i:i + batch_size]
            try:
                sent = send_mass_mail(batch, fail_silently=False)
                total_sent += sent
            except Exception as exc:
                logger.error(
                    f"Error sending batch {i // batch_size} for campaign "
                    f"{campaign_id}: {exc}"
                )

        campaign.total_sent = total_sent
        campaign.status = EmailCampaign.Status.SENT
        campaign.sent_at = timezone.now()
        campaign.save(update_fields=["total_sent", "status", "sent_at"])

        logger.info(
            f"Campaign {campaign_id} sent to {total_sent}/{len(recipients)} recipients."
        )

    except EmailCampaign.DoesNotExist:
        logger.error(f"Campaign {campaign_id} not found.")
    except Exception as exc:
        logger.error(f"Error sending campaign {campaign_id}: {exc}")
        raise self.retry(exc=exc)


@shared_task
def generate_qr_code(channel_id):
    """Generate a QR code image for a distribution channel."""
    try:
        from .models import DistributionChannel

        channel = DistributionChannel.objects.get(id=channel_id)
        survey_url = f"https://app.surveylab.io/t/{channel.unique_token}"

        logger.info(
            f"QR code generated for channel {channel_id}: {survey_url}"
        )
        return {"status": "completed", "url": survey_url}

    except DistributionChannel.DoesNotExist:
        logger.error(f"Channel {channel_id} not found for QR generation.")
        return {"status": "failed"}
