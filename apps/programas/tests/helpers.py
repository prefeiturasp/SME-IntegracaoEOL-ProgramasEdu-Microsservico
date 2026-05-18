"""Helpers compartilhados pelos testes do app programas."""

from __future__ import annotations

from datetime import UTC, date, datetime

from apps.programas.enums import CategoriaPrograma
from apps.programas.models import (
    AlunoPapAnoLetivo,
    AlunoPapAnoLetivoHistorico,
    ComponenteCurricularPrograma,
    MatriculaTurmaPrograma,
    MatriculaTurmaProgramaHistorico,
    TipoPrograma,
    TurmaPrograma,
)

NOME_PROJETO_COLABORATIVO = "PAP PROJETO COLABORATIVO"


def agora() -> datetime:
    """Datetime fixo usado em ``criado_em`` / ``atualizado_em``."""
    return datetime(2026, 4, 1, tzinfo=UTC)


def seed_componentes() -> None:
    """Cria componentes curriculares PAP e PAEE para os testes."""
    ComponenteCurricularPrograma.objects.create(
        codigo_componente_curricular=1322,
        nome_componente_curricular="PAP - RECUPERACAO DE APRENDIZAGENS",
        categoria=CategoriaPrograma.PAP,
        vigente=True,
    )
    ComponenteCurricularPrograma.objects.create(
        codigo_componente_curricular=1770,
        nome_componente_curricular=NOME_PROJETO_COLABORATIVO,
        categoria=CategoriaPrograma.PAP,
        vigente=True,
    )
    ComponenteCurricularPrograma.objects.create(
        codigo_componente_curricular=1054,
        nome_componente_curricular="RECUPERACAO PARALELA PORTUGUES",
        categoria=CategoriaPrograma.PAP,
        vigente=False,
    )
    ComponenteCurricularPrograma.objects.create(
        codigo_componente_curricular=1030,
        nome_componente_curricular="SRM",
        categoria=CategoriaPrograma.PAEE,
        vigente=True,
    )


def seed_tipos() -> None:
    """Cria tipos de programa PAP e PAEE para os testes."""
    TipoPrograma.objects.create(
        codigo_tipo_programa=649,
        nome="PAP Recuperação",
        categoria=CategoriaPrograma.PAP,
        ativo=True,
    )
    TipoPrograma.objects.create(
        codigo_tipo_programa=656,
        nome="PAEE SRM",
        categoria=CategoriaPrograma.PAEE,
        ativo=True,
    )


def seed_turmas() -> dict[int, TurmaPrograma]:
    """Cria turmas PAP e PAEE de teste e retorna
    um dict indexado por codigo_turma.
    """
    turmas: dict[int, TurmaPrograma] = {}
    turmas[3082743] = TurmaPrograma.objects.create(
        codigo_turma=3082743,
        nome_turma="LC",
        codigo_ue="019660",
        codigo_dre="108400",
        ano_letivo=2026,
        tipo_turno=1,
        descricao_turno="Manhã",
        descricao_grade="PAP COLABORATIVO 3 / 4 E 5 ANO",
        situacao="O",
        codigo_tipo_programa=650,
        categoria=CategoriaPrograma.PAP,
        criado_em=agora(),
        atualizado_em=agora(),
    )
    turmas[3105288] = TurmaPrograma.objects.create(
        codigo_turma=3105288,
        nome_turma="SD",
        codigo_ue="092959",
        codigo_dre="108400",
        ano_letivo=2026,
        tipo_turno=2,
        descricao_turno="Tarde",
        descricao_grade="SRM COMPLEMENTAR DA",
        situacao="O",
        codigo_tipo_programa=656,
        categoria=CategoriaPrograma.PAEE,
        criado_em=agora(),
        atualizado_em=agora(),
    )
    turmas[3172713] = TurmaPrograma.objects.create(
        codigo_turma=3172713,
        nome_turma="ID",
        codigo_ue="019660",
        codigo_dre="108400",
        ano_letivo=2026,
        tipo_turno=1,
        descricao_turno="Manhã",
        descricao_grade="PAP 2 ANO COLABORATIVO _ALFABETIZACAO",
        situacao="O",
        codigo_tipo_programa=650,
        categoria=CategoriaPrograma.PAP,
        criado_em=agora(),
        atualizado_em=agora(),
    )
    return turmas


def seed_matriculas() -> list[MatriculaTurmaPrograma]:
    """Cria componentes, turmas e matrículas de programa para os testes."""
    seed_componentes()
    seed_turmas()
    matriculas: list[MatriculaTurmaPrograma] = [
        MatriculaTurmaPrograma.objects.create(
            codigo_aluno=6730137,
            codigo_turma=3082743,
            codigo_componente_curricular=1770,
            nome_componente_curricular=NOME_PROJETO_COLABORATIVO,
            codigo_situacao_matricula=1,
            descricao_situacao_matricula="Ativo",
            data_matricula=date(2026, 2, 1),
            data_situacao=date(2026, 2, 1),
            ano_letivo=2026,
            codigo_ue="019660",
            codigo_dre="108400",
            categoria=CategoriaPrograma.PAP,
            criado_em=agora(),
            atualizado_em=agora(),
        ),
        MatriculaTurmaPrograma.objects.create(
            codigo_aluno=5285836,
            codigo_turma=3105288,
            codigo_componente_curricular=1030,
            nome_componente_curricular="SRM",
            codigo_situacao_matricula=1,
            descricao_situacao_matricula="Ativo",
            data_matricula=date(2025, 12, 11),
            data_situacao=date(2025, 12, 11),
            ano_letivo=2026,
            codigo_ue="092959",
            codigo_dre="108400",
            categoria=CategoriaPrograma.PAEE,
            criado_em=agora(),
            atualizado_em=agora(),
        ),
    ]
    MatriculaTurmaProgramaHistorico.objects.create(
        codigo_aluno=6730137,
        codigo_turma=3082743,
        codigo_componente_curricular=1770,
        nome_componente_curricular=NOME_PROJETO_COLABORATIVO,
        codigo_situacao_matricula=1,
        descricao_situacao_matricula="Ativo",
        data_matricula=date(2026, 2, 1),
        data_situacao=date(2026, 2, 1),
        ano_letivo=2026,
        codigo_ue="019660",
        codigo_dre="108400",
        categoria=CategoriaPrograma.PAP,
        criado_em=agora(),
        atualizado_em=agora(),
    )
    seed_alunos_pap()
    return matriculas


def seed_alunos_pap() -> None:
    """Popula as tabelas pré-agregadas PAP usadas nos testes."""
    # Só a linha PAP (6730137); o aluno PAEE (5285836) não entra.
    AlunoPapAnoLetivo.objects.create(
        codigo_aluno=6730137,
        codigo_turma=3082743,
        codigo_componente_curricular=1770,
        ano_letivo=2026,
        codigo_ue="019660",
        codigo_dre="108400",
    )
    AlunoPapAnoLetivoHistorico.objects.create(
        codigo_aluno=6730137,
        codigo_turma=3082743,
        codigo_componente_curricular=1770,
        ano_letivo=2026,
        codigo_ue="019660",
        codigo_dre="108400",
    )
