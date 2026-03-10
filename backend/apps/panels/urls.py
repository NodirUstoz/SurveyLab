from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers as nested_routers

from . import views

app_name = "panels"

router = DefaultRouter()
router.register(r"", views.ResearchPanelViewSet, basename="panel")

panel_router = nested_routers.NestedDefaultRouter(router, r"", lookup="panel")
panel_router.register(
    r"members", views.PanelMemberViewSet, basename="panel-members"
)

urlpatterns = [
    path("", include(router.urls)),
    path("", include(panel_router.urls)),
]
