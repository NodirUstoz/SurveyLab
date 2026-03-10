from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = "templates_app"

router = DefaultRouter()
router.register(r"", views.SurveyTemplateViewSet, basename="template")

urlpatterns = [
    path("", include(router.urls)),
]
