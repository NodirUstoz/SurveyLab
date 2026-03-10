"""Business logic services for the surveys app."""
import logging
from datetime import datetime

from django.db import transaction
from django.utils import timezone

from .models import (
    BranchingRule,
    Question,
    QuestionOption,
    Survey,
    SurveyPage,
    SurveySettings,
)

logger = logging.getLogger(__name__)


class SurveyService:
    """Encapsulates survey business logic."""

    @staticmethod
    @transaction.atomic
    def duplicate_survey(survey, new_owner=None):
        """Create a complete copy of a survey, including pages, questions, and options."""
        original_id = survey.id
        owner = new_owner or survey.owner

        # Duplicate survey
        survey.pk = None
        survey.title = f"{survey.title} (Copy)"
        survey.slug = f"{survey.slug}-copy-{timezone.now().strftime('%Y%m%d%H%M%S')}"
        survey.status = Survey.Status.DRAFT
        survey.owner = owner
        survey.published_at = None
        survey.save()

        # Duplicate settings
        try:
            original_survey = Survey.objects.get(pk=original_id)
            original_settings = original_survey.settings
            original_settings.pk = None
            original_settings.survey = survey
            original_settings.save()
        except (Survey.DoesNotExist, SurveySettings.DoesNotExist):
            SurveySettings.objects.create(survey=survey)

        # Duplicate pages, questions, and options
        original_pages = SurveyPage.objects.filter(
            survey_id=original_id
        ).prefetch_related("questions__options")

        page_id_map = {}
        question_id_map = {}

        for page in original_pages:
            old_page_id = page.pk
            page.pk = None
            page.survey = survey
            page.save()
            page_id_map[old_page_id] = page.pk

            for question in Question.objects.filter(page_id=old_page_id):
                old_question_id = question.pk
                options = list(question.options.all())
                question.pk = None
                question.page = page
                question.save()
                question_id_map[old_question_id] = question.pk

                for option in options:
                    option.pk = None
                    option.question = question
                    option.quota_count = 0
                    option.save()

        # Duplicate branching rules with updated references
        original_rules = BranchingRule.objects.filter(survey_id=original_id)
        for rule in original_rules:
            rule.pk = None
            rule.survey = survey
            if rule.source_question_id in question_id_map:
                rule.source_question_id = question_id_map[rule.source_question_id]
            if rule.target_question_id and rule.target_question_id in question_id_map:
                rule.target_question_id = question_id_map[rule.target_question_id]
            if rule.target_page_id and rule.target_page_id in page_id_map:
                rule.target_page_id = page_id_map[rule.target_page_id]
            rule.save()

        logger.info(f"Survey {original_id} duplicated as {survey.id}")
        return survey

    @staticmethod
    def publish_survey(survey):
        """Validate and publish a survey."""
        errors = SurveyService.validate_survey(survey)
        if errors:
            return False, errors

        survey.status = Survey.Status.PUBLISHED
        survey.published_at = timezone.now()
        survey.save(update_fields=["status", "published_at", "updated_at"])
        logger.info(f"Survey {survey.id} published")
        return True, []

    @staticmethod
    def close_survey(survey):
        """Close a published survey."""
        survey.status = Survey.Status.CLOSED
        survey.save(update_fields=["status", "updated_at"])
        logger.info(f"Survey {survey.id} closed")
        return True

    @staticmethod
    def validate_survey(survey):
        """Validate a survey is ready for publishing."""
        errors = []
        pages = survey.pages.prefetch_related("questions__options").all()

        if not pages.exists():
            errors.append("Survey must have at least one page.")
            return errors

        total_questions = 0
        for page in pages:
            questions = page.questions.all()
            total_questions += questions.count()
            for question in questions:
                if not question.text.strip():
                    errors.append(
                        f"Question on page '{page.title}' has empty text."
                    )
                if question.question_type in (
                    Question.QuestionType.MULTIPLE_CHOICE,
                    Question.QuestionType.CHECKBOX,
                    Question.QuestionType.DROPDOWN,
                    Question.QuestionType.RANKING,
                ):
                    if question.options.count() < 2:
                        errors.append(
                            f"Question '{question.text[:50]}' needs at least 2 options."
                        )
                if question.question_type == Question.QuestionType.MATRIX:
                    if not question.matrix_rows or not question.matrix_columns:
                        errors.append(
                            f"Matrix question '{question.text[:50]}' needs rows and columns."
                        )

        if total_questions == 0:
            errors.append("Survey must have at least one question.")

        return errors

    @staticmethod
    def evaluate_branching(survey, answers):
        """
        Evaluate branching rules based on collected answers.
        Returns a list of actions to take.
        """
        actions = []
        rules = survey.branching_rules.filter(is_active=True).order_by("order")

        for rule in rules:
            source_question_id = str(rule.source_question_id)
            answer_value = answers.get(source_question_id)

            if rule.evaluate(answer_value):
                actions.append({
                    "action": rule.action,
                    "target_page": str(rule.target_page_id) if rule.target_page_id else None,
                    "target_question": str(rule.target_question_id) if rule.target_question_id else None,
                })

        return actions

    @staticmethod
    @transaction.atomic
    def reorder_pages(survey, page_order):
        """Reorder pages within a survey given a list of page IDs."""
        for idx, page_id in enumerate(page_order):
            SurveyPage.objects.filter(
                id=page_id, survey=survey
            ).update(order=idx)

    @staticmethod
    @transaction.atomic
    def reorder_questions(page, question_order):
        """Reorder questions within a page given a list of question IDs."""
        for idx, question_id in enumerate(question_order):
            Question.objects.filter(
                id=question_id, page=page
            ).update(order=idx)
