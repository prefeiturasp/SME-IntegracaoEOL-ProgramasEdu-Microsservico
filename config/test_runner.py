"""Test runner customizado para o microsserviço Programas.

Os models do app ``programas`` declaram ``Meta.managed = False`` em
produção (DDL é responsabilidade do ``SME-IntegracaoEOL-MS-ETL``).
Em testes isso impediria o Django de criar as tabelas no banco de
testes. Este runner marca temporariamente todos os models do app como
gerenciáveis antes de criar o banco, permitindo que o test runner
padrão crie o schema via ``schema_editor`` e os testes manipulem dados
normalmente.
"""

from __future__ import annotations

from django.test.runner import DiscoverRunner


class ProgramasTestRunner(DiscoverRunner):
    """Runner que torna models managed=False criáveis em testes."""

    def setup_databases(self, **kwargs):  # type: ignore[no-untyped-def]
        from apps.programas import models as programas_models

        for model in (
            programas_models.TipoPrograma,
            programas_models.ComponenteCurricularPrograma,
            programas_models.TurmaPrograma,
            programas_models.TurmaProgramaComponenteCurricular,
            programas_models.MatriculaTurmaPrograma,
            programas_models.MatriculaTurmaProgramaHistorico,
        ):
            model._meta.managed = True

        return super().setup_databases(**kwargs)
