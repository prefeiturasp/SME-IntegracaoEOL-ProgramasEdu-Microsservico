"""Views mock do domínio Programas (EP-01 a EP-08).

Substituirão endpoints legados do Pedagogico-API que hoje consultam EOL/Elastic
(ver CLAUDE.md — "Endpoints do Pedagogico-API legado a substituir pelo domínio programas").
"""

from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.mock_data import (
    ALUNOS_PAP_ANO_LETIVO_MOCK,
    ALUNOS_PAP_MOCK,
    COMPONENTES_CURRICULARES_TURMAS_PROGRAMA_ALUNO_MOCK,
    DADOS_SRM_PAEE_COLABORATIVO_MOCK,
    TURMA_SRM_E_REGULAR_DO_ALUNO_MOCK,
    TURMAS_PAP_MOCK,
    TURMAS_PROGRAMA_MOCK,
)

_TAG_PAP = ["Programas — PAP"]
_TAG_PAEE = ["Programas — PAEE/SRM"]
_TAG_TURMAS = ["Programas — Turmas"]


# ---------------------------------------------------------------------------
# EP-01 — GET /paee/turma-srm-e-regular/aluno/{codigoAluno}
# ---------------------------------------------------------------------------
class ObterTurmaSrmERegularDoAlunoView(APIView):
    """EP-01 — Obter turmas SRM e regular de um aluno PAEE."""

    @extend_schema(
        tags=_TAG_PAEE,
        summary="EP-01 | Obter turmas SRM e regular do aluno",
        parameters=[
            OpenApiParameter("codigoAluno", str, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(self, request: Request, codigoAluno: str) -> Response:
        """Retorna lista mock de turmas SRM/regular do aluno."""
        return Response([TURMA_SRM_E_REGULAR_DO_ALUNO_MOCK])


# ---------------------------------------------------------------------------
# EP-02 — GET /turmas-pap/{anoLetivo}/ues/{codigoEscola}
# ---------------------------------------------------------------------------
class ObterTurmasPapView(APIView):
    """EP-02 — Listar turmas PAP de uma UE em um ano letivo."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-02 | Listar turmas PAP por ano letivo e UE",
        parameters=[
            OpenApiParameter("anoLetivo", str, OpenApiParameter.PATH),
            OpenApiParameter("codigoEscola", str, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(
        self, request: Request, anoLetivo: str, codigoEscola: str
    ) -> Response:
        """Retorna lista mock de turmas PAP."""
        return Response(TURMAS_PAP_MOCK)


# ---------------------------------------------------------------------------
# EP-03 — GET /alunos-pap/{anoLetivo}
# ---------------------------------------------------------------------------
class VerificarSeAlunosSaoTurmaProgramaPapView(APIView):
    """EP-03 — Verificar quais alunos pertencem a turmas PAP em um ano."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-03 | Verificar se alunos pertencem a turmas PAP",
        parameters=[
            OpenApiParameter("anoLetivo", str, OpenApiParameter.PATH),
        ],
        request=list,
        responses={200: list},
    )
    def get(self, request: Request, anoLetivo: str) -> Response:
        """Retorna lista mock de alunos PAP."""
        return Response(ALUNOS_PAP_MOCK)


# ---------------------------------------------------------------------------
# EP-04 — GET /pap/ano-corrente
# ---------------------------------------------------------------------------
class ObterAlunosPapAnoCorrenteView(APIView):
    """EP-04 — Listar alunos PAP do ano corrente."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-04 | Listar alunos PAP do ano corrente",
        responses={200: list},
    )
    def get(self, request: Request) -> Response:
        """Retorna lista mock de alunos PAP do ano corrente."""
        return Response(ALUNOS_PAP_ANO_LETIVO_MOCK)


# ---------------------------------------------------------------------------
# EP-05 — GET /pap/ano-letivo/{anoLetivo}
# ---------------------------------------------------------------------------
class ObterAlunosPapPorAnoLetivoView(APIView):
    """EP-05 — Listar alunos PAP por ano letivo."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-05 | Listar alunos PAP por ano letivo",
        parameters=[
            OpenApiParameter("anoLetivo", str, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(self, request: Request, anoLetivo: str) -> Response:
        """Retorna lista mock de alunos PAP filtrada por ano letivo."""
        return Response(ALUNOS_PAP_ANO_LETIVO_MOCK)


# ---------------------------------------------------------------------------
# EP-06 — GET /{codigoAluno}/turmas-programa/{anoLetivo}/componentes-curriculares
# ---------------------------------------------------------------------------
class ObterComponentesCurricularesTurmasProgramaAlunoView(APIView):
    """EP-06 — Componentes curriculares das turmas de programa do aluno."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-06 | Componentes curriculares das turmas de programa do aluno",
        parameters=[
            OpenApiParameter("codigoAluno", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", str, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(
        self, request: Request, codigoAluno: str, anoLetivo: str
    ) -> Response:
        """Retorna lista mock de componentes das turmas de programa do aluno."""
        return Response(COMPONENTES_CURRICULARES_TURMAS_PROGRAMA_ALUNO_MOCK)


# ---------------------------------------------------------------------------
# EP-07 — GET /srm-paee/aluno/{codigoAluno}
# ---------------------------------------------------------------------------
class ObterDadosSrmPaeeColaborativoView(APIView):
    """EP-07 — Dados de SRM/PAEE colaborativo do aluno."""

    @extend_schema(
        tags=_TAG_PAEE,
        summary="EP-07 | Dados de SRM/PAEE colaborativo do aluno",
        parameters=[
            OpenApiParameter("codigoAluno", str, OpenApiParameter.PATH),
        ],
        responses={200: list},
    )
    def get(self, request: Request, codigoAluno: str) -> Response:
        """Retorna lista mock de dados SRM/PAEE do aluno."""
        return Response(DADOS_SRM_PAEE_COLABORATIVO_MOCK)


# ---------------------------------------------------------------------------
# EP-08 — POST /turmas/turmas-programa
# ---------------------------------------------------------------------------
class ObterTurmasProgramaView(APIView):
    """EP-08 — Filtrar códigos de turma que são turmas de programa."""

    @extend_schema(
        tags=_TAG_TURMAS,
        summary="EP-08 | Filtrar códigos de turma que são turmas de programa",
        request=list,
        responses={200: list},
    )
    def post(self, request: Request) -> Response:
        """Retorna lista mock de códigos de turma que são de programa."""
        return Response(TURMAS_PROGRAMA_MOCK)
