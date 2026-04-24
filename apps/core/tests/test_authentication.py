"""Testes de autenticação por API key."""

import pytest
from django.test import RequestFactory, override_settings
from rest_framework.exceptions import AuthenticationFailed

from apps.core.authentication import ApiKeyAuthentication, UsuarioApiKey


@pytest.fixture()
def auth():
    return ApiKeyAuthentication()


@pytest.fixture()
def factory():
    return RequestFactory()


def _make_drf_request(factory, headers=None):
    """Cria um request DRF a partir de um request Django com headers opcionais."""
    from rest_framework.request import Request

    django_request = factory.get("/")
    if headers:
        for key, value in headers.items():
            # Django transforma headers em META com prefixo HTTP_
            meta_key = "HTTP_" + key.upper().replace("-", "_")
            django_request.META[meta_key] = value
    return Request(django_request)


class TestUsuarioApiKey:
    def test_campos_padrao(self):
        usuario = UsuarioApiKey()
        assert usuario.username == "api_key_user"
        assert usuario.is_authenticated is True
        assert usuario.is_active is True

    def test_campos_customizados(self):
        usuario = UsuarioApiKey(username="outro", is_authenticated=False)
        assert usuario.username == "outro"
        assert usuario.is_authenticated is False


class TestApiKeyAuthentication:
    @override_settings(API_KEY="chave-secreta")
    def test_autenticacao_valida(self, auth, factory):
        request = _make_drf_request(factory, {"X-API-Key": "chave-secreta"})
        resultado = auth.authenticate(request)
        assert resultado is not None
        usuario, credencial = resultado
        assert isinstance(usuario, UsuarioApiKey)
        assert usuario.is_authenticated is True
        assert credencial is None

    @override_settings(API_KEY="chave-secreta")
    def test_sem_header_retorna_none(self, auth, factory):
        request = _make_drf_request(factory)
        resultado = auth.authenticate(request)
        assert resultado is None

    @override_settings(API_KEY="chave-secreta")
    def test_chave_invalida_levanta_excecao(self, auth, factory):
        request = _make_drf_request(factory, {"X-API-Key": "chave-errada"})
        with pytest.raises(AuthenticationFailed) as exc:
            auth.authenticate(request)
        assert "invalida" in str(exc.value).lower()

    @override_settings(API_KEY="")
    def test_api_key_nao_configurada_levanta_excecao(self, auth, factory):
        request = _make_drf_request(factory, {"X-API-Key": "qualquer"})
        with pytest.raises(AuthenticationFailed) as exc:
            auth.authenticate(request)
        assert "configurada" in str(exc.value).lower()

    @override_settings(API_KEY="chave-secreta")
    def test_chave_case_sensitive(self, auth, factory):
        request = _make_drf_request(factory, {"X-API-Key": "Chave-Secreta"})
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    @override_settings(API_KEY="chave-secreta")
    def test_chave_com_espaco_invalida(self, auth, factory):
        request = _make_drf_request(factory, {"X-API-Key": " chave-secreta"})
        with pytest.raises(AuthenticationFailed):
            auth.authenticate(request)

    def test_keyword_correto(self, auth):
        assert auth.keyword == "X-API-Key"
