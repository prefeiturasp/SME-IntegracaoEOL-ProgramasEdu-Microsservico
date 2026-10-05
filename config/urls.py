"""Rotas principais do SME-IntegracaoEOL-ProgramasEdu-Microsservico."""

from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

from apps.core.health import HealthView

urlpatterns = [
    path("api/v1/programasedu/health/", HealthView.as_view(), name="health"),
    path(
        "programasedu/api/v1/schema/",
        SpectacularAPIView.as_view(
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="schema",
    ),
    path(
        "programasedu/api/v1/docs/",
        SpectacularSwaggerView.as_view(
            url_name="schema",
            authentication_classes=[],
            permission_classes=[AllowAny],
        ),
        name="swagger-ui",
    ),
    path("api/v1/programasedu/", include("apps.programas.api.urls")),
]
