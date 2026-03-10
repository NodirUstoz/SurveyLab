from django.urls import path

from . import views

app_name = "analytics"

urlpatterns = [
    path(
        "dashboard/",
        views.DashboardAnalyticsView.as_view(),
        name="dashboard",
    ),
    path(
        "survey/<uuid:survey_id>/",
        views.SurveyAnalyticsView.as_view(),
        name="survey_analytics",
    ),
    path(
        "survey/<uuid:survey_id>/refresh/",
        views.SurveyAnalyticsRefreshView.as_view(),
        name="survey_analytics_refresh",
    ),
    path(
        "survey/<uuid:survey_id>/cross-tabulation/",
        views.CrossTabulationView.as_view(),
        name="cross_tabulation",
    ),
]
