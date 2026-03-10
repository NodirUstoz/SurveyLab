from django.urls import path

from . import views

app_name = "responses"

urlpatterns = [
    path("submit/", views.SubmitResponseView.as_view(), name="submit"),
    path("save-partial/", views.SavePartialResponseView.as_view(), name="save_partial"),
    path(
        "resume/<str:session_key>/",
        views.ResumeSessionView.as_view(),
        name="resume_session",
    ),
    path(
        "survey/<uuid:survey_id>/",
        views.SurveyResponseListView.as_view(),
        name="survey_responses",
    ),
    path(
        "<uuid:pk>/",
        views.SurveyResponseDetailView.as_view(),
        name="response_detail",
    ),
    path(
        "survey/<uuid:survey_id>/export/",
        views.ExportResponsesView.as_view(),
        name="export_responses",
    ),
]
