"""Testes de autenticação por API key."""

from django.test import RequestFactory, TestCase, override_settings
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from apps.core.authentication import ApiKeyAuthentication, UsuarioApiKey


def _make_drf_request(factory, headers=None):
    """Cria um request DRF a partir de um request Django
    com headers opcionais.
    """
    django_request = factory.get("/")
    if headers:
        for key, value in headers.items():
            meta_key = "HTTP_" + key.upper().replace("-", "_")
            django_request.META[meta_key] = value
    return Request(django_request)


class TestUsuarioApiKey(TestCase):
    def test_campos_padrao(self):
        """Verifica os valores padrão do usuário de API key."""
        usuario = UsuarioApiKey()
        self.assertEqual(usuario.username, "api_key_user")
        self.assertTrue(usuario.is_authenticated)
        self.assertTrue(usuario.is_active)

    def test_campos_customizados(self):
        """Verifica os valores customizados do usuário de API key."""
        usuario = UsuarioApiKey(username="outro", is_authenticated=False)
        self.assertEqual(usuario.username, "outro")
        self.assertFalse(usuario.is_authenticated)


class TestApiKeyAuthentication(TestCase):
    def setUp(self):
        """Configura a instância de autenticação e
        o RequestFactory para os testes.
        """
        self.auth = ApiKeyAuthentication()
        self.factory = RequestFactory()

    @override_settings(API_KEY="chave-secreta")
    def test_autenticacao_valida(self):
        """Verifica que uma chave correta resulta em
        autenticação bem-sucedida
        """
        request = _make_drf_request(
            self.factory, {"X-API-Key": "chave-secreta"}
        )
        resultado = self.auth.authenticate(request)
        self.assertIsNotNone(resultado)
        usuario, credencial = resultado
        self.assertIsInstance(usuario, UsuarioApiKey)
        self.assertTrue(usuario.is_authenticated)
        self.assertIsNone(credencial)

    @override_settings(API_KEY="chave-secreta")
    def test_sem_header_retorna_none(self):
        """Verifica que a ausência do header X-API-Key
        resulta em None,
        """
        request = _make_drf_request(self.factory)
        resultado = self.auth.authenticate(request)
        self.assertIsNone(resultado)

    @override_settings(API_KEY="chave-secreta")
    def test_chave_invalida_levanta_excecao(self):
        """Verifica que uma chave incorreta resulta
        em AuthenticationFailed
        """
        request = _make_drf_request(
            self.factory, {"X-API-Key": "chave-errada"}
        )
        with self.assertRaises(AuthenticationFailed) as ctx:
            self.auth.authenticate(request)
        self.assertIn("invalida", str(ctx.exception).lower())

    @override_settings(API_KEY="")
    def test_api_key_nao_configurada_levanta_excecao(self):
        """Verifica que se a API_KEY não estiver configurada,
        a autenticação falha com uma mensagem clara.
        """
        request = _make_drf_request(self.factory, {"X-API-Key": "qualquer"})
        with self.assertRaises(AuthenticationFailed) as ctx:
            self.auth.authenticate(request)
        self.assertIn("configurada", str(ctx.exception).lower())

    @override_settings(API_KEY="chave-secreta")
    def test_chave_case_sensitive(self):
        """Verifica que a autenticação é sensível a maiúsculas/minúsculas."""
        request = _make_drf_request(
            self.factory, {"X-API-Key": "Chave-Secreta"}
        )
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    @override_settings(API_KEY="chave-secreta")
    def test_chave_com_espaco_invalida(self):
        """Verifica que espaços extras na chave resultam em falha de autenticação."""
        request = _make_drf_request(
            self.factory, {"X-API-Key": " chave-secreta"}
        )
        with self.assertRaises(AuthenticationFailed):
            self.auth.authenticate(request)

    def test_keyword_correto(self):
        """Verifica se o keyword para o header é o esperado (X-API-Key)."""
        self.assertEqual(self.auth.keyword, "X-API-Key")
