import uuid

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Survey(models.Model):
    """Core survey model containing pages, questions, and settings."""

    class Status(models.TextChoices):
        DRAFT = "draft", _("Draft")
        PUBLISHED = "published", _("Published")
        CLOSED = "closed", _("Closed")
        ARCHIVED = "archived", _("Archived")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(_("title"), max_length=500)
    description = models.TextField(_("description"), blank=True, default="")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="surveys",
        verbose_name=_("owner"),
    )
    organization = models.ForeignKey(
        "accounts.Organization",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="surveys",
        verbose_name=_("organization"),
    )
    status = models.CharField(
        _("status"), max_length=20, choices=Status.choices, default=Status.DRAFT
    )
    slug = models.SlugField(_("slug"), max_length=255, unique=True)
    category = models.CharField(_("category"), max_length=100, blank=True, default="")
    tags = models.JSONField(_("tags"), default=list, blank=True)
    default_language = models.CharField(
        _("default language"), max_length=10, default="en"
    )
    supported_languages = models.JSONField(
        _("supported languages"), default=list, blank=True
    )
    welcome_message = models.TextField(_("welcome message"), blank=True, default="")
    thank_you_message = models.TextField(
        _("thank you message"),
        blank=True,
        default="Thank you for completing this survey!",
    )
    published_at = models.DateTimeField(_("published at"), null=True, blank=True)
    closes_at = models.DateTimeField(_("closes at"), null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = _("survey")
        verbose_name_plural = _("surveys")

    def __str__(self):
        return self.title

    @property
    def question_count(self):
        return Question.objects.filter(page__survey=self).count()

    @property
    def response_count(self):
        return self.responses.count()


class SurveySettings(models.Model):
    """Per-survey configuration for behavior, quotas, and display."""

    survey = models.OneToOneField(
        Survey,
        on_delete=models.CASCADE,
        related_name="settings",
        verbose_name=_("survey"),
    )
    allow_anonymous = models.BooleanField(_("allow anonymous responses"), default=True)
    require_login = models.BooleanField(_("require login"), default=False)
    one_response_per_user = models.BooleanField(
        _("one response per user"), default=False
    )
    show_progress_bar = models.BooleanField(_("show progress bar"), default=True)
    shuffle_questions = models.BooleanField(_("shuffle questions"), default=False)
    allow_back_navigation = models.BooleanField(
        _("allow back navigation"), default=True
    )
    show_question_numbers = models.BooleanField(
        _("show question numbers"), default=True
    )
    # Quotas
    max_responses = models.IntegerField(_("max responses"), null=True, blank=True)
    quota_rules = models.JSONField(_("quota rules"), default=list, blank=True)
    # Appearance
    theme_color = models.CharField(
        _("theme color"), max_length=7, default="#4F46E5"
    )
    logo = models.ImageField(
        _("survey logo"), upload_to="surveys/logos/", blank=True, null=True
    )
    custom_css = models.TextField(_("custom CSS"), blank=True, default="")
    # Notifications
    notify_on_response = models.BooleanField(
        _("notify on response"), default=False
    )
    notification_emails = models.JSONField(
        _("notification emails"), default=list, blank=True
    )

    class Meta:
        verbose_name = _("survey settings")
        verbose_name_plural = _("survey settings")

    def __str__(self):
        return f"Settings for {self.survey.title}"

    def check_quota(self):
        """Return True if the survey can still accept responses."""
        if self.max_responses is None:
            return True
        return self.survey.response_count < self.max_responses


class SurveyPage(models.Model):
    """A page within a survey. Surveys can have multiple pages."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="pages",
        verbose_name=_("survey"),
    )
    title = models.CharField(_("page title"), max_length=500, blank=True, default="")
    description = models.TextField(
        _("page description"), blank=True, default=""
    )
    order = models.PositiveIntegerField(_("order"), default=0)
    is_visible = models.BooleanField(_("visible"), default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("survey page")
        verbose_name_plural = _("survey pages")
        unique_together = [("survey", "order")]

    def __str__(self):
        return f"{self.survey.title} - Page {self.order + 1}"


class Question(models.Model):
    """A question within a survey page."""

    class QuestionType(models.TextChoices):
        MULTIPLE_CHOICE = "multiple_choice", _("Multiple Choice")
        CHECKBOX = "checkbox", _("Checkbox (Multi-Select)")
        RATING = "rating", _("Rating Scale")
        MATRIX = "matrix", _("Matrix / Grid")
        OPEN_ENDED = "open_ended", _("Open-Ended Text")
        NPS = "nps", _("Net Promoter Score")
        DROPDOWN = "dropdown", _("Dropdown")
        DATE = "date", _("Date")
        FILE_UPLOAD = "file_upload", _("File Upload")
        RANKING = "ranking", _("Ranking")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    page = models.ForeignKey(
        SurveyPage,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name=_("page"),
    )
    question_type = models.CharField(
        _("question type"),
        max_length=30,
        choices=QuestionType.choices,
        default=QuestionType.MULTIPLE_CHOICE,
    )
    text = models.TextField(_("question text"))
    description = models.TextField(
        _("question description"), blank=True, default=""
    )
    is_required = models.BooleanField(_("required"), default=False)
    order = models.PositiveIntegerField(_("order"), default=0)
    # Translations stored as JSON: {"es": "...", "fr": "..."}
    translations = models.JSONField(
        _("translations"), default=dict, blank=True
    )
    # Type-specific configuration
    config = models.JSONField(_("configuration"), default=dict, blank=True)
    # Matrix questions: row and column labels
    matrix_rows = models.JSONField(_("matrix rows"), default=list, blank=True)
    matrix_columns = models.JSONField(
        _("matrix columns"), default=list, blank=True
    )
    # Rating config
    rating_min = models.IntegerField(_("rating min"), default=1)
    rating_max = models.IntegerField(_("rating max"), default=5)
    rating_min_label = models.CharField(
        _("min label"), max_length=100, blank=True, default=""
    )
    rating_max_label = models.CharField(
        _("max label"), max_length=100, blank=True, default=""
    )
    # Validation
    min_length = models.IntegerField(_("min length"), null=True, blank=True)
    max_length = models.IntegerField(_("max length"), null=True, blank=True)
    validation_regex = models.CharField(
        _("validation regex"), max_length=500, blank=True, default=""
    )
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("question")
        verbose_name_plural = _("questions")

    def __str__(self):
        return f"[{self.get_question_type_display()}] {self.text[:80]}"

    def get_text_for_language(self, language="en"):
        if language == "en" or language not in self.translations:
            return self.text
        return self.translations.get(language, self.text)


class QuestionOption(models.Model):
    """An option for multiple-choice, checkbox, dropdown, or ranking questions."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
        verbose_name=_("question"),
    )
    text = models.CharField(_("option text"), max_length=500)
    value = models.CharField(_("option value"), max_length=255, blank=True, default="")
    order = models.PositiveIntegerField(_("order"), default=0)
    is_other = models.BooleanField(
        _("is 'Other' option"), default=False
    )
    translations = models.JSONField(
        _("translations"), default=dict, blank=True
    )
    # Quota tracking per option
    quota_limit = models.IntegerField(_("quota limit"), null=True, blank=True)
    quota_count = models.IntegerField(_("quota count"), default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = _("question option")
        verbose_name_plural = _("question options")

    def __str__(self):
        return self.text

    def get_text_for_language(self, language="en"):
        if language == "en" or language not in self.translations:
            return self.text
        return self.translations.get(language, self.text)

    @property
    def is_quota_full(self):
        if self.quota_limit is None:
            return False
        return self.quota_count >= self.quota_limit


class BranchingRule(models.Model):
    """Conditional branching logic: if question X has answer Y, go to page/question Z."""

    class Action(models.TextChoices):
        SKIP_TO_PAGE = "skip_to_page", _("Skip to Page")
        SKIP_TO_QUESTION = "skip_to_question", _("Skip to Question")
        HIDE_QUESTION = "hide_question", _("Hide Question")
        END_SURVEY = "end_survey", _("End Survey")
        DISQUALIFY = "disqualify", _("Disqualify")

    class Operator(models.TextChoices):
        EQUALS = "equals", _("Equals")
        NOT_EQUALS = "not_equals", _("Does Not Equal")
        CONTAINS = "contains", _("Contains")
        GREATER_THAN = "greater_than", _("Greater Than")
        LESS_THAN = "less_than", _("Less Than")
        IS_ANSWERED = "is_answered", _("Is Answered")
        IS_NOT_ANSWERED = "is_not_answered", _("Is Not Answered")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    survey = models.ForeignKey(
        Survey,
        on_delete=models.CASCADE,
        related_name="branching_rules",
        verbose_name=_("survey"),
    )
    source_question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="branching_rules_as_source",
        verbose_name=_("source question"),
    )
    operator = models.CharField(
        _("operator"), max_length=20, choices=Operator.choices
    )
    value = models.CharField(
        _("comparison value"), max_length=500, blank=True, default=""
    )
    action = models.CharField(
        _("action"), max_length=20, choices=Action.choices
    )
    target_page = models.ForeignKey(
        SurveyPage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="branching_rules_as_target",
        verbose_name=_("target page"),
    )
    target_question = models.ForeignKey(
        Question,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="branching_rules_as_target",
        verbose_name=_("target question"),
    )
    order = models.PositiveIntegerField(_("evaluation order"), default=0)
    is_active = models.BooleanField(_("active"), default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = _("branching rule")
        verbose_name_plural = _("branching rules")

    def __str__(self):
        return (
            f"If Q({self.source_question_id}) {self.operator} '{self.value}' "
            f"-> {self.action}"
        )

    def evaluate(self, answer_value):
        """Evaluate the rule against a given answer value. Returns True if the rule matches."""
        if self.operator == self.Operator.EQUALS:
            return str(answer_value) == self.value
        elif self.operator == self.Operator.NOT_EQUALS:
            return str(answer_value) != self.value
        elif self.operator == self.Operator.CONTAINS:
            return self.value in str(answer_value)
        elif self.operator == self.Operator.GREATER_THAN:
            try:
                return float(answer_value) > float(self.value)
            except (ValueError, TypeError):
                return False
        elif self.operator == self.Operator.LESS_THAN:
            try:
                return float(answer_value) < float(self.value)
            except (ValueError, TypeError):
                return False
        elif self.operator == self.Operator.IS_ANSWERED:
            return bool(answer_value)
        elif self.operator == self.Operator.IS_NOT_ANSWERED:
            return not bool(answer_value)
        return False
