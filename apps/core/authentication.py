"""Autenticação por API Key."""

from __future__ import annotations

from typing import TYPE_CHECKING

from django.conf import settings
from rest_framework import exceptions, status
from rest_framework.authentication import BaseAuthentication
from rest_framework.permissions import IsAuthenticated

if TYPE_CHECKING:
    from rest_framework.request import Request


class UsuarioApiKey:
    """Pseudo-usuário retornado após autenticação bem-sucedida via API Key."""

    is_staff = False
    is_anonymous = False

    def __init__(
        self,
        username: str = "api_key_user",
        is_authenticated: bool = True,
        is_active: bool = True,
    ) -> None:
        self.username = username
        self.is_authenticated = is_authenticated
        self.is_active = is_active

    def __str__(self) -> str:
        return self.username


class ApiKeyAuthentication(BaseAuthentication):
    """Valida requisições via API Key."""

    keyword = "X-API-Key"

    def authenticate(
        self, request: Request
    ) -> tuple[UsuarioApiKey, None] | None:
        """Autentica a requisição pelo header de API Key."""
        header_name = getattr(settings, "API_KEY_HEADER", "x-api-key")
        api_key = getattr(settings, "API_KEY", "")
        meta_key = "HTTP_" + header_name.upper().replace("-", "_")
        key_fornecida = request.META.get(meta_key)

        if key_fornecida is None:
            return None
        if not api_key:
            raise exceptions.AuthenticationFailed("API Key nao configurada.")
        if key_fornecida != api_key:
            err = exceptions.AuthenticationFailed("API Key invalida.")
            err.status_code = status.HTTP_403_FORBIDDEN
            raise err
        return (UsuarioApiKey(), None)

    def authenticate_header(self, request: Request) -> str:
        """Retorna o header de autenticação esperado."""
        return getattr(settings, "API_KEY_HEADER", "x-api-key")


ApiKeyPermission = IsAuthenticated
