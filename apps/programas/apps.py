"""Configuração do app programas."""

from django.apps import AppConfig


class ProgramasConfig(AppConfig):
    """App de leitura do domínio Programas Educacionais (PAP/PAEE)."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.programas"
    label = "programas"
