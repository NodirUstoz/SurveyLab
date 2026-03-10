import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _


class SurveyAnalytics(models.Model):
    """Aggregated analytics snapshot for a survey."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.OneToOneField(
        "surveys.Survey",
        on_delete=models.CASCADE,
        related_name="analytics",
        verbose_name=_("survey"),
    )
    total_responses = models.IntegerField(_("total responses"), default=0)
    complete_responses = models.IntegerField(_("complete responses"), default=0)
    partial_responses = models.IntegerField(_("partial responses"), default=0)
    disqualified_responses = models.IntegerField(
        _("disqualified responses"), default=0
    )
    completion_rate = models.FloatField(_("completion rate"), default=0.0)
    average_duration_seconds = models.FloatField(
        _("average duration (seconds)"), default=0.0
    )
    median_duration_seconds = models.FloatField(
        _("median duration (seconds)"), default=0.0
    )
    total_views = models.IntegerField(_("total views"), default=0)
    unique_visitors = models.IntegerField(_("unique visitors"), default=0)
    drop_off_rates = models.JSONField(
        _("drop-off rates by page"), default=dict, blank=True
    )
    response_trend = models.JSONField(
        _("daily response counts"), default=list, blank=True
    )
    language_distribution = models.JSONField(
        _("language distribution"), default=dict, blank=True
    )
    device_distribution = models.JSONField(
        _("device distribution"), default=dict, blank=True
    )
    last_response_at = models.DateTimeField(
        _("last response at"), null=True, blank=True
    )
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("survey analytics")
        verbose_name_plural = _("survey analytics")

    def __str__(self):
        return f"Analytics for {self.survey.title}"


class QuestionAnalytics(models.Model):
    """Per-question analytics with distribution breakdowns."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey_analytics = models.ForeignKey(
        SurveyAnalytics,
        on_delete=models.CASCADE,
        related_name="question_analytics",
        verbose_name=_("survey analytics"),
    )
    question = models.OneToOneField(
        "surveys.Question",
        on_delete=models.CASCADE,
        related_name="analytics",
        verbose_name=_("question"),
    )
    total_answers = models.IntegerField(_("total answers"), default=0)
    skip_count = models.IntegerField(_("times skipped"), default=0)
    answer_rate = models.FloatField(_("answer rate"), default=0.0)
    # For choice-based questions: {"option_id": count, ...}
    option_distribution = models.JSONField(
        _("option distribution"), default=dict, blank=True
    )
    # For numeric/rating questions
    numeric_average = models.FloatField(_("average"), null=True, blank=True)
    numeric_median = models.FloatField(_("median"), null=True, blank=True)
    numeric_std_dev = models.FloatField(
        _("standard deviation"), null=True, blank=True
    )
    numeric_min = models.FloatField(_("minimum"), null=True, blank=True)
    numeric_max = models.FloatField(_("maximum"), null=True, blank=True)
    # NPS-specific
    nps_score = models.FloatField(_("NPS score"), null=True, blank=True)
    nps_promoters = models.IntegerField(_("promoters"), default=0)
    nps_passives = models.IntegerField(_("passives"), default=0)
    nps_detractors = models.IntegerField(_("detractors"), default=0)
    # For text questions: word frequency, sentiment
    word_cloud_data = models.JSONField(
        _("word cloud data"), default=dict, blank=True
    )
    average_text_length = models.FloatField(
        _("average text length"), null=True, blank=True
    )
    # For matrix questions: row-by-column aggregation
    matrix_aggregation = models.JSONField(
        _("matrix aggregation"), default=dict, blank=True
    )
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        verbose_name = _("question analytics")
        verbose_name_plural = _("question analytics")

    def __str__(self):
        return f"Analytics for Q: {self.question.text[:60]}"


class CrossTabulation(models.Model):
    """Stores cross-tabulation analysis between two questions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        "surveys.Survey",
        on_delete=models.CASCADE,
        related_name="cross_tabulations",
        verbose_name=_("survey"),
    )
    question_a = models.ForeignKey(
        "surveys.Question",
        on_delete=models.CASCADE,
        related_name="cross_tabs_as_a",
        verbose_name=_("question A"),
    )
    question_b = models.ForeignKey(
        "surveys.Question",
        on_delete=models.CASCADE,
        related_name="cross_tabs_as_b",
        verbose_name=_("question B"),
    )
    # Matrix of counts: {"optA1": {"optB1": 5, "optB2": 3}, ...}
    contingency_table = models.JSONField(
        _("contingency table"), default=dict, blank=True
    )
    chi_square_statistic = models.FloatField(
        _("chi-square statistic"), null=True, blank=True
    )
    p_value = models.FloatField(_("p-value"), null=True, blank=True)
    cramers_v = models.FloatField(_("Cramer's V"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)

    class Meta:
        verbose_name = _("cross tabulation")
        verbose_name_plural = _("cross tabulations")
        unique_together = [("survey", "question_a", "question_b")]

    def __str__(self):
        return (
            f"CrossTab: {self.question_a.text[:30]} x {self.question_b.text[:30]}"
        )
