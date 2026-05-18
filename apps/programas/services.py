"""Consultas de leitura do domínio Programas (programas_db)."""

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date, datetime
from typing import Any

import orjson
from django.db import connection
from django.utils import timezone

from apps.programas.enums import (
    CODIGO_COMPONENTE_PAEE_SRM,
    SITUACOES_MATRICULA_VALIDAS,
    SITUACOES_TURMA_ATIVAS,
    CategoriaPrograma,
)
from apps.programas.models import (
    AlunoPapAnoLetivo,
    AlunoPapAnoLetivoHistorico,
    ComponenteCurricularPrograma,
    MatriculaTurmaPrograma,
    TurmaPrograma,
)

# ---------------------------------------------------------------------------
# DTOs de saída (1 por endpoint)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class TurmaSrmRegularDoAlunoDTO:
    """Turma SRM/regular do aluno PAEE (shape reduzido)."""

    codigo_aluno: int
    codigo_turma: int
    ano_letivo: int
    tipo_turno: int | None
    codigo_situacao_matricula: int
    situacao_matricula: str
    data_situacao: date | None
    turma_nome: str


@dataclass(frozen=True)
class TurmaPapResumoDTO:
    """Turma PAP resumida (código e nome)."""

    codigo_turma: str
    turma_nome: str


@dataclass(frozen=True)
class AlunoTurmaProgramaPapDTO:
    """Aluno verificado em turma PAP."""

    codigo_aluno: int
    codigo_turma: int
    codigo_componente: int
    descricao: str


@dataclass(frozen=True)
class AlunoTurmaPapDTO:
    """Aluno PAP com turma, UE e DRE."""

    ano_letivo: int
    codigo_turma: int
    codigo_ue: str
    codigo_dre: str
    codigo_aluno: int
    componente_curricular_id: int


@dataclass(frozen=True)
class ComponenteTurmaProgramaAlunoDTO:
    """Componente curricular da turma de programa do aluno."""

    codigo_aluno: str
    codigo_turma: int
    codigo_componente_curricular: int
    nome_componente_curricular: str


@dataclass(frozen=True)
class DadosSrmPaeeColaborativoDTO:
    """Dados de SRM/PAEE colaborativo do aluno."""

    codigo_turma: int
    codigo_escola: str
    turno: str
    componente: str
    codigo_componente: int
    codigo_aluno: int
    situacao_matricula: str
    data_matricula: datetime | date


# ---------------------------------------------------------------------------
# EP-01 — GET /paee/turma-srm-e-regular/aluno/{codigo_aluno}
# ---------------------------------------------------------------------------
def obter_turmas_paee_do_aluno(
    codigo_aluno: int,
) -> list[TurmaSrmRegularDoAlunoDTO]:
    """Lista turmas PAEE em que o aluno está matriculado.

    Espelha BuscarTurmasSrmERegularDoAlunoQueryHandler do legado
    (origem ElasticSearch). Retorna shape reduzido: a 'turma regular' e
    dados de aluno são agregados pelo Transition Gateway.
    """
    qs = (
        MatriculaTurmaPrograma.objects.filter(
            codigo_aluno=codigo_aluno,
            categoria=CategoriaPrograma.PAEE,
            codigo_situacao_matricula__in=SITUACOES_MATRICULA_VALIDAS,
        )
        .values(
            "codigo_aluno",
            "codigo_turma",
            "ano_letivo",
            "codigo_situacao_matricula",
            "descricao_situacao_matricula",
            "data_situacao",
        )
        .order_by("-ano_letivo", "codigo_situacao_matricula")
    )

    codigos_turmas = {linha["codigo_turma"] for linha in qs}
    turmas_indexadas: dict[int, dict[str, Any]] = {
        t["codigo_turma"]: t
        for t in TurmaPrograma.objects.filter(
            codigo_turma__in=codigos_turmas
        ).values("codigo_turma", "tipo_turno", "nome_turma")
    }

    resultado: list[TurmaSrmRegularDoAlunoDTO] = []
    for linha in qs:
        turma = turmas_indexadas.get(linha["codigo_turma"], {})
        resultado.append(
            TurmaSrmRegularDoAlunoDTO(
                codigo_aluno=linha["codigo_aluno"],
                codigo_turma=linha["codigo_turma"],
                ano_letivo=linha["ano_letivo"],
                tipo_turno=turma.get("tipo_turno"),
                codigo_situacao_matricula=(linha["codigo_situacao_matricula"]),
                situacao_matricula=linha["descricao_situacao_matricula"],
                data_situacao=linha["data_situacao"],
                turma_nome=turma.get("nome_turma", ""),
            )
        )
    return resultado


# ---------------------------------------------------------------------------
# EP-02 — GET /turmas-pap/{ano_letivo}/ues/{codigo_escola}
# ---------------------------------------------------------------------------
def listar_turmas_pap_da_ue(
    ano_letivo: int, codigo_ue: str
) -> list[TurmaPapResumoDTO]:
    """Lista turmas PAP de uma UE em um ano letivo.

    O ``turmaNome`` segue o contrato legado:
    ``"<nome_turma> - <descricao_grade>"`` (ex.:
    ``"L0 - PAP COLABORATIVO 3 / 4 E 5 ANO"``). Quando ``descricao_grade``
    está nulo (turmas legadas ainda não reprocessadas pelo MS-ETL após
    a adição da coluna), retorna apenas ``nome_turma``.
    """
    qs = (
        TurmaPrograma.objects.filter(
            ano_letivo=ano_letivo,
            codigo_ue=codigo_ue,
            categoria=CategoriaPrograma.PAP,
            situacao__in=SITUACOES_TURMA_ATIVAS,
        )
        .values("codigo_turma", "nome_turma", "descricao_grade")
        .order_by("nome_turma")
    )
    return [
        TurmaPapResumoDTO(
            codigo_turma=str(linha["codigo_turma"]),
            turma_nome=(
                f"{linha['nome_turma']} - {linha['descricao_grade']}"
                if linha.get("descricao_grade")
                else linha["nome_turma"]
            ),
        )
        for linha in qs
    ]


# ---------------------------------------------------------------------------
# EP-03 — GET /alunos-pap/{ano_letivo}  (filtra por lista de codigos_alunos)
# ---------------------------------------------------------------------------
def verificar_alunos_em_turma_pap(
    ano_letivo: int, codigos_alunos: Sequence[int]
) -> list[AlunoTurmaProgramaPapDTO]:
    """Verifica quais dos alunos informados pertencem a turmas PAP."""
    if not codigos_alunos:
        return []

    componentes_pap_vigentes = ComponenteCurricularPrograma.objects.filter(
        categoria=CategoriaPrograma.PAP,
        vigente=True,
    ).values_list("codigo_componente_curricular", flat=True)

    qs = MatriculaTurmaPrograma.objects.filter(
        codigo_aluno__in=codigos_alunos,
        ano_letivo=ano_letivo,
        categoria=CategoriaPrograma.PAP,
        codigo_componente_curricular__in=list(componentes_pap_vigentes),
        codigo_situacao_matricula__in=SITUACOES_MATRICULA_VALIDAS,
    ).values(
        "codigo_aluno",
        "codigo_turma",
        "codigo_componente_curricular",
        "nome_componente_curricular",
    )
    return [
        AlunoTurmaProgramaPapDTO(
            codigo_aluno=linha["codigo_aluno"],
            codigo_turma=linha["codigo_turma"],
            codigo_componente=linha["codigo_componente_curricular"],
            descricao=linha["nome_componente_curricular"],
        )
        for linha in qs
    ]


# ---------------------------------------------------------------------------
# EP-04 — GET /pap/ano-corrente
# ---------------------------------------------------------------------------
def listar_alunos_pap_ano_corrente() -> list[AlunoTurmaPapDTO]:
    """Lista alunos PAP do ano corrente."""
    ano_corrente = timezone.now().year
    return _consultar_alunos_pap(AlunoPapAnoLetivo, ano_letivo=ano_corrente)


# ---------------------------------------------------------------------------
# EP-05 — GET /pap/ano-letivo/{ano_letivo}
# ---------------------------------------------------------------------------
def listar_alunos_pap_por_ano(ano_letivo: int) -> list[AlunoTurmaPapDTO]:
    """Lista alunos PAP do ano letivo informado."""
    if ano_letivo >= timezone.now().year:
        return []
    return _consultar_alunos_pap(
        AlunoPapAnoLetivoHistorico, ano_letivo=ano_letivo
    )


def _consultar_alunos_pap(
    model: type[AlunoPapAnoLetivo] | type[AlunoPapAnoLetivoHistorico],
    ano_letivo: int,
) -> list[AlunoTurmaPapDTO]:
    """Lê a tabela pré-agregada e devolve os DTOs PAP."""
    # codigo_componente_curricular é exposto como componente_curricular_id.
    qs = model.objects.filter(ano_letivo=ano_letivo).values(
        "ano_letivo",
        "codigo_turma",
        "codigo_ue",
        "codigo_dre",
        "codigo_aluno",
        "codigo_componente_curricular",
    )
    return [
        AlunoTurmaPapDTO(
            ano_letivo=linha["ano_letivo"],
            codigo_turma=linha["codigo_turma"],
            codigo_ue=linha["codigo_ue"],
            codigo_dre=linha["codigo_dre"],
            codigo_aluno=linha["codigo_aluno"],
            componente_curricular_id=linha["codigo_componente_curricular"],
        )
        for linha in qs
    ]


def obter_alunos_pap_ano_corrente_json() -> bytes:
    """Retorna o JSON dos alunos PAP do ano corrente."""
    # json_agg no Postgres + GZip: Content-Length estável p/ navegador.
    ano_corrente = timezone.now().year
    return _consultar_alunos_pap_json(
        ano_letivo=ano_corrente, historico=False
    )


def obter_alunos_pap_por_ano_json(ano_letivo: int) -> bytes:
    """Retorna o JSON dos alunos PAP do ano letivo informado."""
    if ano_letivo >= timezone.now().year:
        return b"[]"
    return _consultar_alunos_pap_json(
        ano_letivo=ano_letivo, historico=True
    )

_SQL_ALUNOS_PAP_ATUAL = """
    SELECT COALESCE(json_agg(row_to_json(t)), '[]'::json)::text
    FROM (
        SELECT app.ano_letivo                   AS "ano_letivo",
               app.codigo_turma                 AS "codigo_turma",
               app.codigo_ue                    AS "codigo_ue",
               app.codigo_dre                   AS "codigo_dre",
               app.codigo_aluno                 AS "codigo_aluno",
               app.codigo_componente_curricular AS "componente_curricular_id"
        FROM aluno_pap_ano_letivo app
        WHERE app.ano_letivo = %(ano_letivo)s
    ) t
"""

_SQL_ALUNOS_PAP_HISTORICO = """
    SELECT COALESCE(json_agg(row_to_json(t)), '[]'::json)::text
    FROM (
        SELECT app.ano_letivo                   AS "ano_letivo",
               app.codigo_turma                 AS "codigo_turma",
               app.codigo_ue                    AS "codigo_ue",
               app.codigo_dre                   AS "codigo_dre",
               app.codigo_aluno                 AS "codigo_aluno",
               app.codigo_componente_curricular AS "componente_curricular_id"
        FROM aluno_pap_ano_letivo_historico app
        WHERE app.ano_letivo = %(ano_letivo)s
    ) t
"""


def _consultar_alunos_pap_json(
    ano_letivo: int,
    historico: bool = False,
) -> bytes:
    """Retorna o array JSON de alunos PAP em bytes."""
    # Postgres: json_agg no banco. SQLite (testes): ORM + orjson.
    model: type[AlunoPapAnoLetivo] | type[AlunoPapAnoLetivoHistorico] = (
        AlunoPapAnoLetivoHistorico if historico else AlunoPapAnoLetivo
    )
    if connection.vendor == "postgresql":
        sql = (
            _SQL_ALUNOS_PAP_HISTORICO
            if historico
            else _SQL_ALUNOS_PAP_ATUAL
        )
        with connection.cursor() as cur:
            cur.execute(sql, {"ano_letivo": ano_letivo})
            row = cur.fetchone()
        texto = row[0] if row and row[0] is not None else "[]"
        return (
            texto.encode("utf-8")
            if isinstance(texto, str)
            else bytes(texto)
        )
    qs = model.objects.filter(ano_letivo=ano_letivo).values(
        "ano_letivo",
        "codigo_turma",
        "codigo_ue",
        "codigo_dre",
        "codigo_aluno",
        "codigo_componente_curricular",
    )
    return orjson.dumps(
        [
            {
                "ano_letivo": linha["ano_letivo"],
                "codigo_turma": linha["codigo_turma"],
                "codigo_ue": linha["codigo_ue"],
                "codigo_dre": linha["codigo_dre"],
                "codigo_aluno": linha["codigo_aluno"],
                "componente_curricular_id": linha[
                    "codigo_componente_curricular"
                ],
            }
            for linha in qs
        ],
        default=str,
    )


# ---------------------------------------------------------------------------
# EP-06 — GET
# /{codigo_aluno}/turmas-programa/{ano_letivo}/componentes-curriculares
# ---------------------------------------------------------------------------
def listar_componentes_turmas_aluno(
    codigo_aluno: int, ano_letivo: int
) -> list[ComponenteTurmaProgramaAlunoDTO]:
    """Componentes curriculares das turmas de programa do aluno em um ano."""
    qs = (
        MatriculaTurmaPrograma.objects.filter(
            codigo_aluno=codigo_aluno,
            ano_letivo=ano_letivo,
            codigo_situacao_matricula__in=SITUACOES_MATRICULA_VALIDAS,
        )
        .values(
            "codigo_aluno",
            "codigo_turma",
            "codigo_componente_curricular",
            "nome_componente_curricular",
        )
        .distinct()
        .order_by("codigo_turma", "codigo_componente_curricular")
    )
    return [
        ComponenteTurmaProgramaAlunoDTO(
            codigo_aluno=str(linha["codigo_aluno"]),
            codigo_turma=linha["codigo_turma"],
            codigo_componente_curricular=(
                linha["codigo_componente_curricular"]
            ),
            nome_componente_curricular=linha["nome_componente_curricular"],
        )
        for linha in qs
    ]


# ---------------------------------------------------------------------------
# EP-07 — GET /srm-paee/aluno/{codigo_aluno}
# ---------------------------------------------------------------------------
def obter_dados_srm_paee_aluno(
    codigo_aluno: int,
) -> list[DadosSrmPaeeColaborativoDTO]:
    """Dados de SRM/PAEE colaborativo do aluno (componente=1030)."""
    qs = (
        MatriculaTurmaPrograma.objects.filter(
            codigo_aluno=codigo_aluno,
            codigo_componente_curricular=CODIGO_COMPONENTE_PAEE_SRM,
            codigo_situacao_matricula__in=SITUACOES_MATRICULA_VALIDAS,
        )
        .values(
            "codigo_aluno",
            "codigo_turma",
            "codigo_ue",
            "codigo_componente_curricular",
            "nome_componente_curricular",
            "codigo_situacao_matricula",
            "data_matricula",
        )
        .order_by("codigo_situacao_matricula", "data_matricula")
    )

    codigos_turmas = {linha["codigo_turma"] for linha in qs}
    turmas_turno: dict[int, str] = {
        t["codigo_turma"]: t["descricao_turno"]
        for t in TurmaPrograma.objects.filter(
            codigo_turma__in=codigos_turmas
        ).values("codigo_turma", "descricao_turno")
    }

    resultado: list[DadosSrmPaeeColaborativoDTO] = []
    for linha in qs:
        resultado.append(
            DadosSrmPaeeColaborativoDTO(
                codigo_turma=linha["codigo_turma"],
                codigo_escola=linha["codigo_ue"],
                turno=turmas_turno.get(linha["codigo_turma"], ""),
                componente=linha["nome_componente_curricular"],
                codigo_componente=linha["codigo_componente_curricular"],
                codigo_aluno=linha["codigo_aluno"],
                situacao_matricula=str(linha["codigo_situacao_matricula"]),
                data_matricula=linha["data_matricula"],
            )
        )
    return resultado


# ---------------------------------------------------------------------------
# EP-08 — POST /turmas/turmas-programa
# ---------------------------------------------------------------------------
def filtrar_codigos_que_sao_turma_programa(
    codigos_turmas: Sequence[str],
) -> list[str]:
    """Retorna o subconjunto dos códigos informados que são turmas de programa.

    Como turma_programa é populada exclusivamente com cd_tipo_turma=3
    do EOL, basta testar a existência do código na tabela.
    """
    if not codigos_turmas:
        return []

    codigos_int: list[int] = []
    for codigo in codigos_turmas:
        try:
            codigos_int.append(int(codigo))
        except (TypeError, ValueError):
            continue

    if not codigos_int:
        return []

    encontrados = TurmaPrograma.objects.filter(
        codigo_turma__in=codigos_int
    ).values_list("codigo_turma", flat=True)

    return [str(c) for c in encontrados]
