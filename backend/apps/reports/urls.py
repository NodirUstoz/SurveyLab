from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "reports"

router = DefaultRouter()
router.register(r"", views.ReportViewSet, basename="report")

scheduled_router = DefaultRouter()
scheduled_router.register(
    r"", views.ScheduledReportViewSet, basename="scheduled-report"
)

urlpatterns = [
    path(
        "survey/<uuid:survey_id>/",
        views.SurveyReportsView.as_view(),
        name="survey_reports",
    ),
    path(
        "shared/<str:share_token>/",
        views.SharedReportView.as_view(),
        name="shared_report",
    ),
    path("scheduled/", include(scheduled_router.urls)),
    path("", include(router.urls)),
]
