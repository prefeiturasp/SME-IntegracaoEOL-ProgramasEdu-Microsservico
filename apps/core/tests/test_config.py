"""Testes das configurações de execução do microsserviço."""

from __future__ import annotations

import importlib
import os
import runpy
import sys
from unittest.mock import MagicMock, patch

from django.test import SimpleTestCase
from django.test.runner import DiscoverRunner

from config import settings
from config.test_runner import ProgramasTestRunner


class DatabaseSettingsTestCase(SimpleTestCase):
    """Valida a montagem das configurações de banco de dados."""

    def test_url_vazia_configura_sqlite_em_memoria(self) -> None:
        """Usa SQLite em memória quando nenhuma URL é informada."""
        resultado = settings._parse_db_url(None)

        self.assertEqual(
            resultado,
            {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": ":memory:",
            },
        )

    def test_url_em_bytes_usa_defaults_postgresql(self) -> None:
        """Decodifica bytes e preenche os defaults da conexão PostgreSQL."""
        resultado = settings._parse_db_url(b"postgresql:///programas")

        self.assertEqual(resultado["NAME"], "programas")
        self.assertEqual(resultado["USER"], "postgres")
        self.assertEqual(resultado["PASSWORD"], "postgres")
        self.assertEqual(resultado["HOST"], "localhost")
        self.assertEqual(resultado["PORT"], "5432")

    @patch.object(sys, "argv", ["manage.py", "runserver"])
    @patch.dict(
        os.environ,
        {
            "USE_SQLITE_TEST": "False",
            "URL_BANCO_PROGRAMAS": "postgresql://usuario:senha@db:5433/base",
        },
    )
    def test_carregamento_fora_do_modo_teste(self) -> None:
        """Preserva a conexão PostgreSQL quando o processo não é de teste."""
        configuracao = runpy.run_path(settings.__file__)

        self.assertFalse(configuracao["MODO_TESTE"])
        self.assertEqual(
            configuracao["DATABASES"]["default"]["ENGINE"],
            "dj_db_conn_pool.backends.postgresql",
        )


class ApplicationEntrypointsTestCase(SimpleTestCase):
    """Valida os pontos de entrada dos servidores da aplicação."""

    def test_asgi_disponibiliza_aplicacao(self) -> None:
        """Carrega o ponto de entrada ASGI."""
        modulo = importlib.import_module("config.asgi")

        self.assertTrue(callable(modulo.application))

    def test_wsgi_disponibiliza_aplicacao(self) -> None:
        """Carrega o ponto de entrada WSGI."""
        modulo = importlib.import_module("config.wsgi")

        self.assertTrue(callable(modulo.application))


class ProgramasTestRunnerTestCase(SimpleTestCase):
    """Valida a criação controlada das tabelas usadas nos testes."""

    @patch.object(DiscoverRunner, "setup_databases", return_value="resultado")
    @patch("config.test_runner.connections")
    @patch("config.test_runner.apps.get_models")
    def test_ignora_models_gerenciados_e_tabelas_duplicadas(
        self,
        get_models_mock: MagicMock,
        connections_mock: MagicMock,
        setup_databases_mock: MagicMock,
    ) -> None:
        """Cria uma vez cada tabela de model não gerenciado."""
        model_gerenciado = MagicMock()
        model_gerenciado._meta.managed = True
        primeiro_model = MagicMock()
        primeiro_model._meta.managed = False
        primeiro_model._meta.db_table = "tabela_compartilhada"
        segundo_model = MagicMock()
        segundo_model._meta.managed = False
        segundo_model._meta.db_table = "tabela_compartilhada"
        get_models_mock.return_value = [
            model_gerenciado,
            primeiro_model,
            segundo_model,
        ]
        editor = (
            connections_mock.__getitem__.return_value.schema_editor.return_value.__enter__.return_value
        )

        resultado = ProgramasTestRunner().setup_databases()

        self.assertEqual(resultado, "resultado")
        setup_databases_mock.assert_called_once_with()
        editor.create_model.assert_called_once_with(primeiro_model)
