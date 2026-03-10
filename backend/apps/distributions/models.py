import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class DistributionChannel(models.Model):
    """A channel through which a survey is distributed (link, email, embed, etc.)."""

    class ChannelType(models.TextChoices):
        WEB_LINK = "web_link", _("Web Link")
        EMAIL = "email", _("Email Campaign")
        EMBED = "embed", _("Website Embed")
        QR_CODE = "qr_code", _("QR Code")
        SOCIAL = "social", _("Social Media")
        API = "api", _("API Integration")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.CASCADE,
        related_name="distribution_channels",
        verbose_name=_("survey"),
    )
    channel_type = models.CharField(
        _("channel type"),
        max_length=20,
        choices=ChannelType.choices,
        default=ChannelType.WEB_LINK,
    )
    name = models.CharField(_("channel name"), max_length=255)
    is_active = models.BooleanField(_("active"), default=True)
    # Tracking
    unique_token = models.CharField(
        _("unique token"), max_length=64, unique=True, db_index=True
    )
    click_count = models.IntegerField(_("click count"), default=0)
    response_count = models.IntegerField(_("response count"), default=0)
    # Configuration
    config = models.JSONField(_("channel config"), default=dict, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("distribution channel")
        verbose_name_plural = _("distribution channels")

    def __str__(self):
        return f"{self.name} ({self.get_channel_type_display()})"

    @property
    def conversion_rate(self):
        if self.click_count == 0:
            return 0.0
        return round(self.response_count / self.click_count * 100, 1)


class EmailCampaign(models.Model):
    """Email distribution campaign for sending survey invitations."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        SCHEDULED = "scheduled", _("Scheduled")
        SENDING = "sending", _("Sending")
        SENT = "sent", _("Sent")
        FAILED = "failed", _("Failed")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.ForeignKey(
        DistributionChannel,
        on_delete=models.CASCADE,
        related_name="email_campaigns",
        verbose_name=_("channel"),
    )
    subject = models.CharField(_("email subject"), max_length=500)
    body_html = models.TextField(_("email body (HTML)"))
    body_text = models.TextField(_("email body (text)"), blank=True, default="")
    from_name = models.CharField(
        _("from name"), max_length=255, default="SurveyLab"
    )
    from_email = models.EmailField(_("from email"), blank=True, default="")
    reply_to = models.EmailField(_("reply-to"), blank=True, default="")
    recipient_list = models.JSONField(
        _("recipient emails"), default=list, blank=True
    )
    status = models.CharField(
        _("status"),
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
    )
    scheduled_at = models.DateTimeField(_("scheduled at"), null=True, blank=True)
    sent_at = models.DateTimeField(_("sent at"), null=True, blank=True)
    total_sent = models.IntegerField(_("total sent"), default=0)
    total_opened = models.IntegerField(_("total opened"), default=0)
    total_clicked = models.IntegerField(_("total clicked"), default=0)
    total_bounced = models.IntegerField(_("total bounced"), default=0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("email campaign")
        verbose_name_plural = _("email campaigns")

    def __str__(self):
        return f"Campaign: {self.subject[:60]}"

    @property
    def open_rate(self):
        if self.total_sent == 0:
            return 0.0
        return round(self.total_opened / self.total_sent * 100, 1)


class EmbedConfiguration(models.Model):
    """Configuration for embedding a survey on a website."""

    class EmbedType(models.TextChoices):
        INLINE = "inline", _("Inline")
        POPUP = "popup", _("Popup / Modal")
        SLIDE_IN = "slide_in", _("Slide-in Panel")
        FULL_PAGE = "full_page", _("Full Page")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    channel = models.OneToOneField(
        DistributionChannel,
        on_delete=models.CASCADE,
        related_name="embed_config",
        verbose_name=_("channel"),
    )
    embed_type = models.CharField(
        _("embed type"),
        max_length=20,
        choices=EmbedType.choices,
        default=EmbedType.INLINE,
    )
    width = models.CharField(_("width"), max_length=20, default="100%")
    height = models.CharField(_("height"), max_length=20, default="600px")
    allowed_domains = models.JSONField(
        _("allowed domains"), default=list, blank=True
    )
    trigger_delay_seconds = models.IntegerField(
        _("trigger delay (seconds)"), default=0
    )
    trigger_scroll_percent = models.IntegerField(
        _("trigger scroll percent"), default=0
    )
    show_close_button = models.BooleanField(_("show close button"), default=True)
    custom_css = models.TextField(_("custom CSS"), blank=True, default="")

    class Meta:
        verbose_name = _("embed configuration")
        verbose_name_plural = _("embed configurations")

    def __str__(self):
        return f"Embed config for {self.channel.name}"

    def generate_embed_code(self):
        """Generate the HTML/JS embed snippet."""
        token = self.channel.unique_token
        if self.embed_type == self.EmbedType.INLINE:
            return (
                f'<div id="surveylab-embed-{token}"></div>\n'
                f'<script src="https://cdn.surveylab.io/embed.js" '
                f'data-token="{token}" data-type="inline" '
                f'data-width="{self.width}" data-height="{self.height}">'
                f"</script>"
            )
        elif self.embed_type == self.EmbedType.POPUP:
            return (
                f'<script src="https://cdn.surveylab.io/embed.js" '
                f'data-token="{token}" data-type="popup" '
                f'data-delay="{self.trigger_delay_seconds}">'
                f"</script>"
            )
        return f'<script src="https://cdn.surveylab.io/embed.js" data-token="{token}"></script>'
