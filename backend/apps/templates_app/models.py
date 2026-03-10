import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class SurveyTemplate(models.Model):
    """Pre-built survey templates that can be used to create new surveys."""

    class Category(models.TextChoices):
        CUSTOMER_SATISFACTION = "customer_satisfaction", _("Customer Satisfaction")
        EMPLOYEE_ENGAGEMENT = "employee_engagement", _("Employee Engagement")
        MARKET_RESEARCH = "market_research", _("Market Research")
        ACADEMIC = "academic", _("Academic Research")
        EVENT_FEEDBACK = "event_feedback", _("Event Feedback")
        PRODUCT_FEEDBACK = "product_feedback", _("Product Feedback")
        HEALTHCARE = "healthcare", _("Healthcare")
        EDUCATION = "education", _("Education")
        HR = "hr", _("Human Resources")
        OTHER = "other", _("Other")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("template title"), max_length=500)
    description = models.TextField(_("description"))
    category = models.CharField(
        _("category"),
        max_length=30,
        choices=Category.choices,
        default=Category.OTHER,
    )
    tags = models.JSONField(_("tags"), default=list, blank=True)
    thumbnail = models.ImageField(
        _("thumbnail"),
        upload_to="templates/thumbnails/",
        blank=True,
        null=True,
    )
    # The full template definition as JSON
    template_data = models.JSONField(
        _("template data"),
        default=dict,
        help_text="Complete survey structure: pages, questions, options, settings.",
    )
    # Estimated time to complete
    estimated_minutes = models.IntegerField(
        _("estimated minutes"), default=5
    )
    question_count = models.IntegerField(_("question count"), default=0)
    # Visibility
    is_public = models.BooleanField(_("public"), default=True)
    is_featured = models.BooleanField(_("featured"), default=False)
    # Ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_templates",
        verbose_name=_("created by"),
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="templates",
        verbose_name=_("organization"),
    )
    # Usage tracking
    use_count = models.IntegerField(_("times used"), default=0)
    average_rating = models.FloatField(_("average rating"), default=0.0)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["-is_featured", "-use_count", "title"]
        verbose_name = _("survey template")
        verbose_name_plural = _("survey templates")

    def __str__(self):
        return f"{self.title} ({self.get_category_display()})"


class TemplateRating(models.Model):
    """User rating for a survey template."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(
        SurveyTemplate,
        on_delete=models.CASCADE,
        related_name="ratings",
        verbose_name=_("template"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="template_ratings",
        verbose_name=_("user"),
    )
    score = models.IntegerField(
        _("score"),
        choices=[(i, str(i)) for i in range(1, 6)],
    )
    comment = models.TextField(_("comment"), blank=True, default="")
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("template rating")
        verbose_name_plural = _("template ratings")
        unique_together = [("template", "user")]

    def __str__(self):
        return f"{self.user.email} rated {self.template.title}: {self.score}/5"
