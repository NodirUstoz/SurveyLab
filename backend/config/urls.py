from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/surveys/", include("apps.surveys.urls")),
    path("api/v1/responses/", include("apps.responses.urls")),
    path("api/v1/analytics/", include("apps.analytics.urls")),
    path("api/v1/distributions/", include("apps.distributions.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),
    path("api/v1/reports/", include("apps.reports.urls")),
    path("api/v1/panels/", include("apps.panels.urls")),
    path("api/v1/templates/", include("apps.templates_app.urls")),
    # API Schema
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
