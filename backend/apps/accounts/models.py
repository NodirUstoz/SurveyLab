import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class Organization(models.Model):
    """Multi-tenant organization for grouping users and surveys."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(_("organization name"), max_length=255)
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    logo = models.ImageField(
        _("logo"), upload_to="organizations/logos/", blank=True, null=True
    )
    website = models.URLField(_("website"), blank=True, default="")
    plan = models.CharField(
        _("plan"),
        max_length=20,
        choices=[
            ("free", "Free"),
            ("starter", "Starter"),
            ("professional", "Professional"),
            ("enterprise", "Enterprise"),
        ],
        default="free",
    )
    max_surveys = models.IntegerField(_("max surveys"), default=10)
    max_responses_per_survey = models.IntegerField(
        _("max responses per survey"), default=100
    )
    is_active = models.BooleanField(_("active"), default=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name = _("organization")
        verbose_name_plural = _("organizations")

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Custom user model with organization support."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(_("email address"), unique=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        verbose_name=_("organization"),
    )
    role = models.CharField(
        _("role"),
        max_length=20,
        choices=[
            ("owner", "Owner"),
            ("admin", "Admin"),
            ("editor", "Editor"),
            ("viewer", "Viewer"),
        ],
        default="editor",
    )
    avatar = models.ImageField(
        _("avatar"), upload_to="users/avatars/", blank=True, null=True
    )
    phone = models.CharField(_("phone number"), max_length=20, blank=True, default="")
    preferred_language = models.CharField(
        _("preferred language"), max_length=10, default="en"
    )
    timezone = models.CharField(_("timezone"), max_length=50, default="UTC")
    email_notifications = models.BooleanField(
        _("email notifications"), default=True
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self):
        return self.email

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email
