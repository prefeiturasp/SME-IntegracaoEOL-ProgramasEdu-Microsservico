"""Views do domínio Programas (EP-01 a EP-08).

Substituem os endpoints legados do Pedagogico-API que hoje consultam
EOL/Elastic. Os dados vêm de programas_db, populado pelo
SME-IntegracaoEOL-MS-ETL.

EP-01 retorna shape reduzido — campos de aluno/pedagógico ausentes
são agregados pelo Transition Gateway.
"""

from collections.abc import Iterable, Iterator
from typing import Any

import orjson
from django.http import HttpResponse
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.programas import services
from apps.programas.api.serializers import (
    AlunoTurmaPapSerializer,
    AlunoTurmaProgramaPapSerializer,
    ComponenteTurmaProgramaAlunoSerializer,
    DadosSrmPaeeColaborativoSerializer,
    TurmaPapResumoSerializer,
    TurmasProgramaRequestSerializer,
    TurmaSrmRegularDoAlunoSerializer,
)

_TAG_PAP = ["Programas — PAP"]
_TAG_PAEE = ["Programas — PAEE/SRM"]
_TAG_TURMAS = ["Programas — Turmas"]


def _to_int(valor: str, nome_param: str) -> int:
    """Faz a conversão do path param para int ou retorna
    ValueError com contexto.
    """
    try:
        return int(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Parâmetro '{nome_param}' deve ser um inteiro válido: "
            f"recebido {valor!r}."
        ) from exc


_PAGINACAO_LIMITE_DEFAULT = 100
_PAGINACAO_LIMITE_MAX = 500


def _paginar_lista(
    lista: list[Any], request: Request
) -> tuple[list[Any], Response | None]:
    """Pagina ``lista`` por ``?limit`` e ``?offset`` preservando o contrato.

    Retorna ``(slice, None)`` em sucesso ou ``([], erro_400)`` quando os
    parâmetros são inválidos. Limite default ``100`` e máximo ``500`` —
    cliente que omitir ``limit`` recebe os primeiros ``100`` itens.
    """
    try:
        limit = int(
            request.query_params.get("limit", _PAGINACAO_LIMITE_DEFAULT)
        )
        offset = int(request.query_params.get("offset", 0))
    except (TypeError, ValueError):
        return [], Response(
            {"detail": "Parâmetros 'limit' e 'offset' devem ser inteiros."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    if limit <= 0 or offset < 0:
        return [], Response(
            {"detail": "Parâmetros 'limit' (>0) e 'offset' (>=0) inválidos."},
            status=status.HTTP_400_BAD_REQUEST,
        )
    limit = min(limit, _PAGINACAO_LIMITE_MAX)
    return lista[offset : offset + limit], None


def _stream_json_array(items: Iterable[dict[str, Any]]) -> Iterator[bytes]:
    """Serializa um iterable como array JSON em chunks de bytes.

    Mantém o mesmo shape do contrato legado (``[{...}, {...}]``) mas sem
    materializar a lista inteira em memória — cada item vai pro socket
    assim que sai do cursor do banco.
    """
    yield b"["
    primeiro = True
    for item in items:
        if primeiro:
            primeiro = False
        else:
            yield b","
        yield json.dumps(item, default=str).encode("utf-8")
    yield b"]"


# ---------------------------------------------------------------------------
# EP-01 — GET /paee/turma-srm-e-regular/aluno/{codigoAluno}
# ---------------------------------------------------------------------------
class ObterTurmaSrmERegularDoAlunoView(APIView):
    """EP-01 — Obter turmas SRM e regular de um aluno PAEE."""

    @extend_schema(
        tags=_TAG_PAEE,
        summary="EP-01 | Obter turmas SRM/regular do aluno (shape reduzido)",
        description=(
            "Retorna apenas os campos pertencentes ao domínio Programas. "
            "Campos como nomeAluno, dataNascimento, nomeResponsavel, "
            "etapaEnsino e dataAtualizacaoTabela são responsabilidade dos "
            "domínios Alunos/Pedagógico — agregados pelo Transition "
            "Gateway na resposta final ao consumidor."
        ),
        parameters=[
            OpenApiParameter("codigoAluno", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaSrmRegularDoAlunoSerializer(many=True)},
    )
    def get(self, request: Request, codigoAluno: str) -> Response:
        try:
            codigo = _to_int(codigoAluno, "codigoAluno")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        dados = services.obter_turmas_paee_do_aluno(codigo_aluno=codigo)
        return Response(
            TurmaSrmRegularDoAlunoSerializer(dados, many=True).data
        )


# ---------------------------------------------------------------------------
# EP-02 — GET /turmas-pap/{anoLetivo}/ues/{codigoEscola}
# ---------------------------------------------------------------------------
class ObterTurmasPapView(APIView):
    """EP-02 — Listar turmas PAP de uma UE em um ano letivo."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-02 | Listar turmas PAP por ano letivo e UE",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter("codigoEscola", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaPapResumoSerializer(many=True)},
    )
    def get(
        self, request: Request, anoLetivo: str, codigoEscola: str
    ) -> Response:
        try:
            ano = _to_int(anoLetivo, "anoLetivo")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        dados = services.listar_turmas_pap_da_ue(
            ano_letivo=ano, codigo_ue=codigoEscola
        )
        return Response(TurmaPapResumoSerializer(dados, many=True).data)


# ---------------------------------------------------------------------------
# EP-03 — GET /alunos-pap/{anoLetivo}
# ---------------------------------------------------------------------------
class VerificarSeAlunosSaoTurmaProgramaPapView(APIView):
    """EP-03 — Verificar quais alunos pertencem a turmas PAP em um ano.

    O legado recebe a lista de codigosAlunos via query param
    (``codigosAlunos`` repetido) — preservamos o mesmo contrato.
    """

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-03 | Verificar se alunos pertencem a turmas PAP",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigosAlunos",
                int,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
            ),
            OpenApiParameter("limit", int, OpenApiParameter.QUERY),
            OpenApiParameter("offset", int, OpenApiParameter.QUERY),
        ],
        responses={200: AlunoTurmaProgramaPapSerializer(many=True)},
    )
    def get(self, request: Request, anoLetivo: str) -> Response:
        try:
            ano = _to_int(anoLetivo, "anoLetivo")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        codigos_raw = request.query_params.getlist("codigosAlunos")
        codigos: list[int] = []
        for codigo in codigos_raw:
            try:
                codigos.append(int(codigo))
            except (TypeError, ValueError):
                return Response(
                    {
                        "detail": (
                            "codigosAlunos deve conter apenas inteiros: "
                            f"recebido {codigo!r}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        dados = services.verificar_alunos_em_turma_pap(
            ano_letivo=ano, codigos_alunos=codigos
        )
        pagina, erro = _paginar_lista(dados, request)
        if erro is not None:
            return erro
        return Response(
            AlunoTurmaProgramaPapSerializer(pagina, many=True).data
        )


# ---------------------------------------------------------------------------
# EP-04 — GET /pap/ano-corrente
# ---------------------------------------------------------------------------
class ObterAlunosPapAnoCorrenteView(APIView):
    """EP-04 — Listar alunos PAP do ano corrente.

    Utiliza ``orjson`` em vez de ``json.dump`` devido a grande quantidade de retorno.
    Permite ``Content-Length`` definido (gzip/brotli mais eficientes,
    progresso no browser).
    """

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-04 | Listar alunos PAP do ano corrente",
        parameters=[
            OpenApiParameter("limit", int, OpenApiParameter.QUERY),
            OpenApiParameter("offset", int, OpenApiParameter.QUERY),
        ],
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(self, request: Request) -> HttpResponse | Response:
        dados = list(services.iter_alunos_pap_ano_corrente())
        pagina, erro = _paginar_lista(dados, request)
        if erro is not None:
            return erro
        return HttpResponse(
            orjson.dumps(pagina, default=str),
            content_type="application/json",
        )


# ---------------------------------------------------------------------------
# EP-05 — GET /pap/ano-letivo/{anoLetivo}
# ---------------------------------------------------------------------------
class ObterAlunosPapPorAnoLetivoView(APIView):
    """EP-05 — Listar alunos PAP por ano letivo (mesma estratégia do EP-04)."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="EP-05 | Listar alunos PAP por ano letivo",
        parameters=[
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(self, request: Request, anoLetivo: str) -> HttpResponse | Response:
        try:
            ano = _to_int(anoLetivo, "anoLetivo")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        dados = list(services.iter_alunos_pap_por_ano(ano_letivo=ano))
        return HttpResponse(
            orjson.dumps(dados, default=str),
            content_type="application/json",
        )


# -------------------------------------------------------------------
# EP-06 — GET
# /{codigoAluno}/turmas-programa/{anoLetivo}/componentes-curriculares
# -------------------------------------------------------------------
class ObterComponentesCurricularesTurmasProgramaAlunoView(APIView):
    """EP-06 — Componentes curriculares das turmas de programa do aluno."""

    @extend_schema(
        tags=_TAG_PAP,
        summary=(
            "EP-06 | Componentes curriculares das turmas de programa do aluno"
        ),
        parameters=[
            OpenApiParameter("codigoAluno", str, OpenApiParameter.PATH),
            OpenApiParameter("anoLetivo", int, OpenApiParameter.PATH),
        ],
        responses={200: ComponenteTurmaProgramaAlunoSerializer(many=True)},
    )
    def get(
        self, request: Request, codigoAluno: str, anoLetivo: str
    ) -> Response:
        try:
            codigo = _to_int(codigoAluno, "codigoAluno")
            ano = _to_int(anoLetivo, "anoLetivo")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        dados = services.listar_componentes_turmas_aluno(
            codigo_aluno=codigo, ano_letivo=ano
        )
        return Response(
            ComponenteTurmaProgramaAlunoSerializer(dados, many=True).data
        )


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
        responses={200: DadosSrmPaeeColaborativoSerializer(many=True)},
    )
    def get(self, request: Request, codigoAluno: str) -> Response:
        try:
            codigo = _to_int(codigoAluno, "codigoAluno")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        dados = services.obter_dados_srm_paee_aluno(codigo_aluno=codigo)
        return Response(
            DadosSrmPaeeColaborativoSerializer(dados, many=True).data
        )


# ---------------------------------------------------------------------------
# EP-08 — POST /turmas/turmas-programa
# ---------------------------------------------------------------------------
class ObterTurmasProgramaView(APIView):
    """EP-08 — Filtrar códigos de turma que são turmas de programa.

    Body: lista de strings (códigos de turma) — fiel ao contrato legado
    (``IEnumerable<string>``).
    """

    @extend_schema(
        tags=_TAG_TURMAS,
        summary="EP-08 | Filtrar códigos de turma que são turmas de programa",
        request={
            "application/json": {
                "type": "array",
                "items": {"type": "string"},
                "example": ["3105355", "3092080", "3105288", "3306279"],
            }
        },
        responses={200: {"type": "array", "items": {"type": "string"}}},
    )
    def post(self, request: Request) -> Response:
        serializer = TurmasProgramaRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        codigos = serializer.validated_data["codigos_turmas"]

        encontrados = services.filtrar_codigos_que_sao_turma_programa(
            codigos_turmas=codigos
        )
        return Response(encontrados)
