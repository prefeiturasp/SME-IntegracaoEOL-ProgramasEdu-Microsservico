"""Testes da integração com o SME Sidecar SDK."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from uuid import UUID

from django.conf import settings
from django.test import SimpleTestCase

import apps.core
from apps.core.apps import CoreConfig


class SidecarSdkConfigurationTestCase(SimpleTestCase):
    """Valida a configuração do SDK no processo Django."""

    def test_core_config_esta_registrado_explicitamente(self) -> None:
        """Verifica o registro explícito da configuração do app core."""
        self.assertIn("apps.core.apps.CoreConfig", settings.INSTALLED_APPS)

    def test_middleware_de_observabilidade_precede_middleware_django(
        self,
    ) -> None:
        """Verifica a precedência do SDK sobre os middlewares da aplicação."""
        middleware_sidecar = (
            "sme_sidecar_sdk.integrations.django.ObservabilityMiddleware"
        )
        middleware_gzip = "django.middleware.gzip.GZipMiddleware"

        self.assertIn(middleware_sidecar, settings.MIDDLEWARE)
        self.assertLess(
            settings.MIDDLEWARE.index(middleware_sidecar),
            settings.MIDDLEWARE.index(middleware_gzip),
        )

    @patch("sme_sidecar_sdk.runtime.configure")
    def test_ready_inicializa_runtime(
        self,
        mock_configure: MagicMock,
    ) -> None:
        """Verifica a inicialização do runtime no carregamento do app."""
        app_config = CoreConfig("apps.core", apps.core)

        app_config.ready()

        mock_configure.assert_called_once_with()


class SidecarSdkMiddlewareTestCase(SimpleTestCase):
    """Valida a correlação das requisições HTTP."""

    def test_reutiliza_request_id_recebido(self) -> None:
        """Devolve o identificador de correlação recebido."""
        response = self.client.get(
            "/rota-inexistente/",
            HTTP_X_REQUEST_ID="request-programasedu-123",
        )

        self.assertEqual(
            response.headers["X-Request-ID"],
            "request-programasedu-123",
        )

    def test_gera_request_id_quando_header_nao_e_enviado(self) -> None:
        """Gera um identificador de correlação para a requisição."""
        response = self.client.get("/rota-inexistente/")

        request_id = response.headers["X-Request-ID"]
        self.assertEqual(str(UUID(request_id)), request_id)
