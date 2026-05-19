"""Configurações Django do SME-IntegracaoEOL-ProgramasEdu-Microsservico.

Microsserviço de leitura do domínio Programas Educacionais (PAP/PAEE).
Lê do banco programas_db, populado pelo SME-IntegracaoEOL-MS-ETL.
"""

import os
import sys
import urllib.parse
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY", "dev-secret-not-for-production"
)
DEBUG = os.environ.get("DJANGO_DEBUG", "True").lower() in ("true", "1")

ALLOWED_HOSTS = [
    host.strip()
    for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "*").split(",")
]

DB_POOL_SIZE = int(os.environ.get("DB_POOL_SIZE", "5"))
_POOL_OPTIONS = {
    "POOL_SIZE": DB_POOL_SIZE,
    "MAX_OVERFLOW": 0,
    "POOL_TIMEOUT": 30,
    "POOL_RECYCLE": 1800,
    "PRE_PING": True,
}


def _parse_db_url(url: Any) -> dict:
    """Faz o parse de uma URL postgres para dict de configuração Django."""
    if not url:
        return {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }

    if isinstance(url, bytes):
        url = url.decode("utf-8")

    parsed = urllib.parse.urlparse(str(url))
    return {
        "ENGINE": "dj_db_conn_pool.backends.postgresql",
        "NAME": parsed.path.lstrip("/"),
        "USER": parsed.username or "postgres",
        "PASSWORD": parsed.password or "postgres",
        "HOST": parsed.hostname or "localhost",
        "PORT": str(parsed.port or 5432),
        "POOL_OPTIONS": _POOL_OPTIONS,
    }


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "drf_spectacular",
    "apps.core",
    "apps.programas",
]

MIDDLEWARE = [
    "django.middleware.gzip.GZipMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

URL_BANCO_PROGRAMAS = os.environ.get("URL_BANCO_PROGRAMAS")

DATABASES = {
    "default": _parse_db_url(URL_BANCO_PROGRAMAS),
}

MODO_TESTE = "test" in sys.argv or os.environ.get(
    "USE_SQLITE_TEST", "False"
).lower() in ("true", "1")
if MODO_TESTE:
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }

TEST_RUNNER = "config.test_runner.ProgramasTestRunner"

AUTH_PASSWORD_VALIDATORS: list[dict[str, object]] = []

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

NIVEL_LOG = os.environ.get("NIVEL_LOG", "INFO")

API_KEY_HEADER = os.environ.get("API_KEY_HEADER", "X-API-Key")
API_KEY = (
    "test-api-key"
    if MODO_TESTE
    else os.environ.get("API_KEY", "dev-key-default")
)

REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "apps.core.authentication.ApiKeyAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "SME-IntegracaoEOL-ProgramasEdu-Microsservico API",
    "DESCRIPTION": (
        "Endpoints de leitura do domínio Programas Educacionais "
        "(PAP/PAEE).\n\n"
        "Substituem os endpoints legados do Pedagogico-API que hoje "
        "consultam o EOL/Elastic. Os dados vêm de programas_db, "
        "populado pelo SME-IntegracaoEOL-MS-ETL.\n\n"
        "Consumido pelo Transition Gateway, que agrega dados deste "
        "microsserviço com os domínios Alunos e Pedagógico."
    ),
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "APPEND_COMPONENTS": {
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": API_KEY_HEADER,
            }
        }
    },
    "SECURITY": [{"ApiKeyAuth": []}],
    "SWAGGER_UI_SETTINGS": {
        "syntaxHighlight": False,
    },
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "padrao": {
            "format": "%(asctime)s %(levelname)s %(name)s %(message)s",
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "padrao",
        }
    },
    "root": {
        "handlers": ["console"],
        "level": NIVEL_LOG,
    },
}
