from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "distributions"

router = DefaultRouter()
router.register(r"channels", views.DistributionChannelViewSet, basename="channel")
router.register(r"campaigns", views.EmailCampaignViewSet, basename="campaign")

urlpatterns = [
    path(
        "survey/<uuid:survey_id>/channels/",
        views.SurveyDistributionChannelsView.as_view(),
        name="survey_channels",
    ),
    path(
        "track/<str:token>/",
        views.PublicChannelTrackView.as_view(),
        name="track_channel",
    ),
    path("", include(router.urls)),
]
