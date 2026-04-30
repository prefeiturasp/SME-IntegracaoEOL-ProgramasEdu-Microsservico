"""Configuração do app programas."""

from django.apps import AppConfig


class ProgramasConfig(AppConfig):
    """App de leitura do domínio Programas Educacionais (PAP/PAEE).

    Lê dados de programas_db, populado pelo SME-IntegracaoEOL-MS-ETL.
    Todos os models são read-only (managed=False).
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.programas"
    label = "programas"
