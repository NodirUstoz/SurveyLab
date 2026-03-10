import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class ResearchPanel(models.Model):
    """A curated group of respondents available for survey distribution."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        related_name="panels",
        verbose_name=_("organization"),
    )
    name = models.CharField(_("panel name"), max_length=255)
    description = models.TextField(_("description"), blank=True, default="")
    is_active = models.BooleanField(_("active"), default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_panels",
        verbose_name=_("created by"),
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("research panel")
        verbose_name_plural = _("research panels")

    def __str__(self):
        return self.name

    @property
    def member_count(self):
        return self.members.count()

    @property
    def active_member_count(self):
        return self.members.filter(is_active=True).count()


class PanelMember(models.Model):
    """A member of a research panel with demographic attributes."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    panel = models.ForeignKey(
        ResearchPanel,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name=_("panel"),
    )
    email = models.EmailField(_("email"))
    first_name = models.CharField(_("first name"), max_length=100, blank=True, default="")
    last_name = models.CharField(_("last name"), max_length=100, blank=True, default="")
    # Demographic attributes
    demographics = models.JSONField(
        _("demographics"), default=dict, blank=True,
        help_text="Flexible demographic data: age, gender, location, etc.",
    )
    tags = models.JSONField(_("tags"), default=list, blank=True)
    is_active = models.BooleanField(_("active"), default=True)
    opt_out = models.BooleanField(_("opted out"), default=False)
    # Participation tracking
    surveys_invited = models.IntegerField(_("surveys invited"), default=0)
    surveys_completed = models.IntegerField(_("surveys completed"), default=0)
    last_invited_at = models.DateTimeField(
        _("last invited at"), null=True, blank=True
    )
    last_responded_at = models.DateTimeField(
        _("last responded at"), null=True, blank=True
    )
    joined_at = models.DateTimeField(_("joined at"), auto_now_add=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        verbose_name = _("panel member")
        verbose_name_plural = _("panel members")
        unique_together = [("panel", "email")]

    def __str__(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email

    @property
    def response_rate(self):
        if self.surveys_invited == 0:
            return 0.0
        return round(self.surveys_completed / self.surveys_invited * 100, 1)
