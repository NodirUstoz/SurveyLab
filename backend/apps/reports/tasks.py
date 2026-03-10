"""Celery tasks for report generation."""
import io
import logging

from celery import shared_task
from django.utils import timezone

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2, default_retry_delay=120)
def generate_report(self, report_id):
    """Generate a report file (PDF, DOCX, etc.)."""
    try:
        from apps.analytics.models import SurveyAnalytics, QuestionAnalytics
        from apps.analytics.services import AnalyticsService
        from apps.responses.models import SurveyResponse, Answer
        from apps.surveys.models import Question
        from .models import Report

        report = Report.objects.select_related("survey", "created_by").get(
            id=report_id
        )

        survey = report.survey

        # Ensure analytics are up to date
        analytics, _ = SurveyAnalytics.objects.get_or_create(survey=survey)
        AnalyticsService._update_survey_level_stats(analytics, survey)
        AnalyticsService._update_question_stats(analytics, survey)

        # Build report data
        questions = Question.objects.filter(
            page__survey=survey
        ).order_by("page__order", "order")

        responses = SurveyResponse.objects.filter(survey=survey)
        if report.response_status_filter and report.response_status_filter != "all":
            responses = responses.filter(status=report.response_status_filter)
        if report.date_range_start:
            responses = responses.filter(submitted_at__gte=report.date_range_start)
        if report.date_range_end:
            responses = responses.filter(submitted_at__lte=report.date_range_end)

        report_data = {
            "survey_title": survey.title,
            "survey_description": survey.description,
            "total_responses": analytics.total_responses,
            "completion_rate": analytics.completion_rate,
            "average_duration": analytics.average_duration_seconds,
            "generated_at": timezone.now().isoformat(),
        }

        if report.include_summary:
            report_data["summary"] = {
                "complete": analytics.complete_responses,
                "partial": analytics.partial_responses,
                "disqualified": analytics.disqualified_responses,
                "languages": analytics.language_distribution,
            }

        if report.include_charts:
            question_data = []
            for q in questions:
                try:
                    qa = QuestionAnalytics.objects.get(question=q)
                    question_data.append({
                        "question": q.text,
                        "type": q.question_type,
                        "total_answers": qa.total_answers,
                        "distribution": qa.option_distribution,
                        "average": qa.numeric_average,
                        "nps_score": qa.nps_score,
                    })
                except QuestionAnalytics.DoesNotExist:
                    pass
            report_data["questions"] = question_data

        # Generate output file based on format
        if report.output_format == "pdf":
            file_content = _generate_pdf_report(report_data)
            filename = f"report-{report.id}.pdf"
            content_type = "application/pdf"
        elif report.output_format == "html":
            file_content = _generate_html_report(report_data)
            filename = f"report-{report.id}.html"
            content_type = "text/html"
        else:
            file_content = _generate_html_report(report_data)
            filename = f"report-{report.id}.html"
            content_type = "text/html"

        from django.core.files.base import ContentFile
        report.file.save(filename, ContentFile(file_content))
        report.file_size_bytes = len(file_content)
        report.status = Report.Status.READY
        report.generated_at = timezone.now()
        report.save(update_fields=[
            "file", "file_size_bytes", "status", "generated_at",
        ])

        # Notify the user
        from apps.notifications.services import NotificationService
        NotificationService.notify_export_ready(
            report.created_by,
            survey,
            f"/reports/{report.id}/download",
        )

        logger.info(f"Report {report_id} generated successfully.")

    except Report.DoesNotExist:
        logger.error(f"Report {report_id} not found.")
    except Exception as exc:
        logger.error(f"Error generating report {report_id}: {exc}")
        try:
            from .models import Report
            Report.objects.filter(id=report_id).update(
                status=Report.Status.FAILED
            )
        except Exception:
            pass
        raise self.retry(exc=exc)


def _generate_pdf_report(data):
    """Generate a PDF report using ReportLab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(data.get("survey_title", "Report"), styles["Title"]))
    elements.append(Spacer(1, 0.3 * inch))

    # Summary
    if "summary" in data:
        elements.append(Paragraph("Summary", styles["Heading2"]))
        summary = data["summary"]
        summary_text = (
            f"Total Responses: {data.get('total_responses', 0)} | "
            f"Complete: {summary.get('complete', 0)} | "
            f"Partial: {summary.get('partial', 0)} | "
            f"Completion Rate: {data.get('completion_rate', 0):.1f}%"
        )
        elements.append(Paragraph(summary_text, styles["Normal"]))
        elements.append(Spacer(1, 0.2 * inch))

    # Questions
    if "questions" in data:
        elements.append(Paragraph("Question Results", styles["Heading2"]))
        for q in data["questions"]:
            elements.append(
                Paragraph(f"Q: {q['question']}", styles["Heading4"])
            )
            details = f"Type: {q['type']} | Answers: {q.get('total_answers', 0)}"
            if q.get("average") is not None:
                details += f" | Average: {q['average']:.2f}"
            if q.get("nps_score") is not None:
                details += f" | NPS: {q['nps_score']:.0f}"
            elements.append(Paragraph(details, styles["Normal"]))
            elements.append(Spacer(1, 0.1 * inch))

    elements.append(Spacer(1, 0.3 * inch))
    elements.append(
        Paragraph(
            f"Generated: {data.get('generated_at', '')}",
            styles["Normal"],
        )
    )

    doc.build(elements)
    return buffer.getvalue()


def _generate_html_report(data):
    """Generate an HTML report."""
    questions_html = ""
    for q in data.get("questions", []):
        avg_str = f" | Average: {q['average']:.2f}" if q.get("average") else ""
        nps_str = f" | NPS: {q['nps_score']:.0f}" if q.get("nps_score") else ""
        questions_html += f"""
        <div style="margin-bottom: 16px; padding: 12px; border: 1px solid #e5e7eb; border-radius: 8px;">
            <h4 style="margin: 0 0 8px 0;">{q['question']}</h4>
            <p style="color: #6b7280; margin: 0;">
                Type: {q['type']} | Answers: {q.get('total_answers', 0)}{avg_str}{nps_str}
            </p>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{data.get('survey_title', 'Report')}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 40px auto; padding: 0 20px; color: #1f2937; }}
        h1 {{ color: #4f46e5; border-bottom: 2px solid #4f46e5; padding-bottom: 8px; }}
        .summary {{ background: #f9fafb; padding: 20px; border-radius: 8px; margin: 20px 0; }}
        .stat {{ display: inline-block; margin-right: 24px; }}
        .stat-value {{ font-size: 24px; font-weight: bold; color: #4f46e5; }}
        .stat-label {{ font-size: 12px; color: #6b7280; text-transform: uppercase; }}
    </style>
</head>
<body>
    <h1>{data.get('survey_title', 'Report')}</h1>
    <p>{data.get('survey_description', '')}</p>

    <div class="summary">
        <h2>Summary</h2>
        <div class="stat">
            <div class="stat-value">{data.get('total_responses', 0)}</div>
            <div class="stat-label">Total Responses</div>
        </div>
        <div class="stat">
            <div class="stat-value">{data.get('completion_rate', 0):.1f}%</div>
            <div class="stat-label">Completion Rate</div>
        </div>
        <div class="stat">
            <div class="stat-value">{data.get('average_duration', 0):.0f}s</div>
            <div class="stat-label">Avg Duration</div>
        </div>
    </div>

    <h2>Question Results</h2>
    {questions_html}

    <footer style="margin-top: 40px; padding-top: 16px; border-top: 1px solid #e5e7eb; color: #9ca3af; font-size: 12px;">
        Generated by SurveyLab on {data.get('generated_at', '')}
    </footer>
</body>
</html>"""
    return html.encode("utf-8")
