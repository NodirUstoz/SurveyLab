"""Analytics computation services."""
import logging
import statistics
from collections import Counter, defaultdict
from datetime import timedelta

from django.db.models import Avg, Count, F, Q
from django.utils import timezone

from apps.responses.models import Answer, SurveyResponse
from apps.surveys.models import Question
from .models import CrossTabulation, QuestionAnalytics, SurveyAnalytics

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for computing and updating survey analytics."""

    @staticmethod
    def update_analytics_for_response(survey_response):
        """Incrementally update analytics after a new response is submitted."""
        survey = survey_response.survey
        analytics, _ = SurveyAnalytics.objects.get_or_create(survey=survey)

        AnalyticsService._update_survey_level_stats(analytics, survey)
        AnalyticsService._update_question_stats(analytics, survey)

        logger.info(f"Analytics updated for survey {survey.id}")

    @staticmethod
    def _update_survey_level_stats(analytics, survey):
        """Recompute top-level survey statistics."""
        responses = SurveyResponse.objects.filter(survey=survey)

        status_counts = responses.values("status").annotate(
            count=Count("id")
        )
        status_map = {item["status"]: item["count"] for item in status_counts}

        analytics.total_responses = responses.count()
        analytics.complete_responses = status_map.get("complete", 0)
        analytics.partial_responses = status_map.get("partial", 0)
        analytics.disqualified_responses = status_map.get("disqualified", 0)

        if analytics.total_responses > 0:
            analytics.completion_rate = (
                analytics.complete_responses / analytics.total_responses * 100
            )

        # Duration stats
        durations = list(
            responses.filter(duration_seconds__isnull=False)
            .values_list("duration_seconds", flat=True)
        )
        if durations:
            analytics.average_duration_seconds = statistics.mean(durations)
            analytics.median_duration_seconds = statistics.median(durations)

        # Language distribution
        lang_counts = responses.values("language").annotate(count=Count("id"))
        analytics.language_distribution = {
            item["language"]: item["count"] for item in lang_counts
        }

        # Response trend - last 30 days
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_counts = (
            responses.filter(submitted_at__gte=thirty_days_ago)
            .extra(select={"day": "DATE(submitted_at)"})
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")
        )
        analytics.response_trend = [
            {"date": str(item["day"]), "count": item["count"]}
            for item in daily_counts
        ]

        # Last response timestamp
        last = responses.order_by("-submitted_at").first()
        if last:
            analytics.last_response_at = last.submitted_at

        # Drop-off rates per page
        pages = survey.pages.order_by("order")
        drop_off = {}
        for page in pages:
            page_questions = page.questions.values_list("id", flat=True)
            answered_count = (
                Answer.objects.filter(
                    question_id__in=page_questions,
                    response__survey=survey,
                )
                .values("response")
                .distinct()
                .count()
            )
            drop_off[str(page.id)] = {
                "page_title": page.title or f"Page {page.order + 1}",
                "respondents_reached": answered_count,
                "rate": round(
                    (1 - answered_count / analytics.total_responses) * 100, 1
                )
                if analytics.total_responses > 0
                else 0,
            }
        analytics.drop_off_rates = drop_off

        analytics.save()

    @staticmethod
    def _update_question_stats(analytics, survey):
        """Compute per-question analytics."""
        questions = Question.objects.filter(page__survey=survey).select_related(
            "page"
        )

        for question in questions:
            q_analytics, _ = QuestionAnalytics.objects.get_or_create(
                survey_analytics=analytics, question=question
            )

            answers = Answer.objects.filter(
                question=question, response__survey=survey
            )

            q_analytics.total_answers = answers.count()
            q_analytics.skip_count = (
                analytics.total_responses - q_analytics.total_answers
            )
            q_analytics.answer_rate = (
                q_analytics.total_answers / analytics.total_responses * 100
                if analytics.total_responses > 0
                else 0
            )

            # Type-specific aggregations
            if question.question_type in (
                Question.QuestionType.MULTIPLE_CHOICE,
                Question.QuestionType.CHECKBOX,
                Question.QuestionType.DROPDOWN,
            ):
                AnalyticsService._compute_choice_stats(q_analytics, answers)

            elif question.question_type in (
                Question.QuestionType.RATING,
                Question.QuestionType.NPS,
            ):
                AnalyticsService._compute_numeric_stats(
                    q_analytics, answers, question
                )

            elif question.question_type == Question.QuestionType.OPEN_ENDED:
                AnalyticsService._compute_text_stats(q_analytics, answers)

            elif question.question_type == Question.QuestionType.MATRIX:
                AnalyticsService._compute_matrix_stats(q_analytics, answers)

            elif question.question_type == Question.QuestionType.RANKING:
                AnalyticsService._compute_ranking_stats(q_analytics, answers)

            q_analytics.save()

    @staticmethod
    def _compute_choice_stats(q_analytics, answers):
        """Compute distribution for choice-based questions."""
        option_counts = defaultdict(int)
        for answer in answers.prefetch_related("selected_options"):
            for opt in answer.selected_options.all():
                option_counts[str(opt.id)] += 1
        q_analytics.option_distribution = dict(option_counts)

    @staticmethod
    def _compute_numeric_stats(q_analytics, answers, question):
        """Compute statistical measures for numeric/rating questions."""
        values = list(
            answers.filter(numeric_value__isnull=False)
            .values_list("numeric_value", flat=True)
        )
        if not values:
            return

        q_analytics.numeric_average = statistics.mean(values)
        q_analytics.numeric_median = statistics.median(values)
        q_analytics.numeric_min = min(values)
        q_analytics.numeric_max = max(values)
        if len(values) > 1:
            q_analytics.numeric_std_dev = statistics.stdev(values)

        # NPS calculation
        if question.question_type == Question.QuestionType.NPS:
            promoters = sum(1 for v in values if v >= 9)
            passives = sum(1 for v in values if 7 <= v <= 8)
            detractors = sum(1 for v in values if v <= 6)
            total = len(values)

            q_analytics.nps_promoters = promoters
            q_analytics.nps_passives = passives
            q_analytics.nps_detractors = detractors
            q_analytics.nps_score = (
                ((promoters - detractors) / total) * 100 if total > 0 else 0
            )

    @staticmethod
    def _compute_text_stats(q_analytics, answers):
        """Compute text analytics: word frequency and average length."""
        texts = list(answers.values_list("text_value", flat=True))
        if not texts:
            return

        lengths = [len(t) for t in texts if t]
        q_analytics.average_text_length = (
            statistics.mean(lengths) if lengths else 0
        )

        # Word frequency for word cloud
        word_counts = Counter()
        stop_words = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "it", "this", "that", "and", "or", "but", "not", "i", "we",
            "you", "he", "she", "they", "my", "your", "his", "her",
            "its", "our", "their",
        }
        for text in texts:
            if text:
                words = text.lower().split()
                for word in words:
                    cleaned = word.strip(".,!?;:'\"()-")
                    if cleaned and len(cleaned) > 2 and cleaned not in stop_words:
                        word_counts[cleaned] += 1

        q_analytics.word_cloud_data = dict(word_counts.most_common(100))

    @staticmethod
    def _compute_matrix_stats(q_analytics, answers):
        """Aggregate matrix question responses."""
        aggregation = defaultdict(lambda: defaultdict(int))
        for answer in answers:
            if answer.matrix_values:
                for row_label, col_value in answer.matrix_values.items():
                    aggregation[row_label][str(col_value)] += 1

        q_analytics.matrix_aggregation = {
            row: dict(cols) for row, cols in aggregation.items()
        }

    @staticmethod
    def _compute_ranking_stats(q_analytics, answers):
        """Compute average rank positions for ranking questions."""
        rank_sums = defaultdict(list)
        for answer in answers:
            if answer.ranking_values:
                for position, option_id in enumerate(answer.ranking_values):
                    rank_sums[str(option_id)].append(position + 1)

        q_analytics.option_distribution = {
            opt_id: round(statistics.mean(positions), 2)
            for opt_id, positions in rank_sums.items()
        }

    @staticmethod
    def compute_cross_tabulation(survey, question_a, question_b):
        """Compute cross-tabulation between two questions."""
        responses = SurveyResponse.objects.filter(
            survey=survey, status="complete"
        )

        contingency = defaultdict(lambda: defaultdict(int))
        for response in responses:
            answer_a = Answer.objects.filter(
                response=response, question=question_a
            ).first()
            answer_b = Answer.objects.filter(
                response=response, question=question_b
            ).first()

            if answer_a and answer_b:
                val_a = answer_a.display_value or "N/A"
                val_b = answer_b.display_value or "N/A"
                contingency[val_a][val_b] += 1

        table = {k: dict(v) for k, v in contingency.items()}

        # Chi-square computation
        chi_sq, p_val, cramers = AnalyticsService._chi_square(table)

        cross_tab, _ = CrossTabulation.objects.update_or_create(
            survey=survey,
            question_a=question_a,
            question_b=question_b,
            defaults={
                "contingency_table": table,
                "chi_square_statistic": chi_sq,
                "p_value": p_val,
                "cramers_v": cramers,
            },
        )
        return cross_tab

    @staticmethod
    def _chi_square(table):
        """Simplified chi-square test on a contingency table dict."""
        if not table:
            return None, None, None

        all_cols = set()
        for row_data in table.values():
            all_cols.update(row_data.keys())
        all_cols = sorted(all_cols)
        rows = sorted(table.keys())

        if len(rows) < 2 or len(all_cols) < 2:
            return None, None, None

        # Build matrix
        matrix = []
        for r in rows:
            row_vals = [table.get(r, {}).get(c, 0) for c in all_cols]
            matrix.append(row_vals)

        n = sum(sum(row) for row in matrix)
        if n == 0:
            return None, None, None

        row_totals = [sum(row) for row in matrix]
        col_totals = [sum(matrix[i][j] for i in range(len(rows))) for j in range(len(all_cols))]

        chi_sq = 0.0
        for i in range(len(rows)):
            for j in range(len(all_cols)):
                expected = row_totals[i] * col_totals[j] / n
                if expected > 0:
                    chi_sq += (matrix[i][j] - expected) ** 2 / expected

        k = min(len(rows), len(all_cols))
        cramers = (chi_sq / (n * (k - 1))) ** 0.5 if n > 0 and k > 1 else 0

        return round(chi_sq, 4), None, round(cramers, 4)
