"""Configuracao do app professores."""

from django.apps import AppConfig


class ProgramasConfig(AppConfig):
    """App mock do domínio Programas."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.programas"
    label = "programas"
