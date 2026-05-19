"""Views do domínio Programas."""

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
    """Retorna o path param convertido para int ou levanta ValueError."""
    try:
        return int(valor)
    except (TypeError, ValueError) as exc:
        raise ValueError(
            f"Parâmetro '{nome_param}' deve ser um inteiro válido: "
            f"recebido {valor!r}."
        ) from exc


# ---------------------------------------------------------------------------
# EP-01 — GET /paee/turma-srm-e-regular/aluno/{codigo_aluno}
# ---------------------------------------------------------------------------
class ObterTurmaSrmERegularDoAlunoView(APIView):
    """Retorna as turmas SRM e regular de um aluno PAEE."""

    @extend_schema(
        tags=_TAG_PAEE,
        summary="Obter turmas SRM/regular do aluno (shape reduzido)",
        description=(
            "Retorna apenas os campos pertencentes ao domínio Programas. "
            "Campos como nomeAluno, dataNascimento, nomeResponsavel, "
            "etapaEnsino e dataAtualizacaoTabela são responsabilidade dos "
            "domínios Alunos/Pedagógico — agregados pelo Transition "
            "Gateway na resposta final ao consumidor."
        ),
        parameters=[
            OpenApiParameter("codigo_aluno", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaSrmRegularDoAlunoSerializer(many=True)},
    )
    def get(self, request: Request, codigo_aluno: str) -> Response:
        try:
            codigo = _to_int(codigo_aluno, "codigo_aluno")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        dados = services.obter_turmas_paee_do_aluno(codigo_aluno=codigo)
        return Response(
            TurmaSrmRegularDoAlunoSerializer(dados, many=True).data
        )


# ---------------------------------------------------------------------------
# EP-02 — GET /turmas-pap/{ano_letivo}/ues/{codigo_escola}
# ---------------------------------------------------------------------------
class ObterTurmasPapView(APIView):
    """Lista turmas PAP de uma UE em um ano letivo."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="Listar turmas PAP por ano letivo e UE",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter("codigo_escola", str, OpenApiParameter.PATH),
        ],
        responses={200: TurmaPapResumoSerializer(many=True)},
    )
    def get(
        self, request: Request, ano_letivo: str, codigo_escola: str
    ) -> Response:
        try:
            ano = _to_int(ano_letivo, "ano_letivo")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        dados = services.listar_turmas_pap_da_ue(
            ano_letivo=ano, codigo_ue=codigo_escola
        )
        return Response(TurmaPapResumoSerializer(dados, many=True).data)


# ---------------------------------------------------------------------------
# EP-03 — GET /alunos-pap/{ano_letivo}
# ---------------------------------------------------------------------------
class VerificarSeAlunosSaoTurmaProgramaPapView(APIView):
    """Verifica quais alunos pertencem a turmas PAP no ano."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="Verificar se alunos pertencem a turmas PAP",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
            OpenApiParameter(
                "codigos_alunos",
                int,
                OpenApiParameter.QUERY,
                required=True,
                many=True,
            ),
        ],
        responses={200: AlunoTurmaProgramaPapSerializer(many=True)},
    )
    def get(self, request: Request, ano_letivo: str) -> Response:
        try:
            ano = _to_int(ano_letivo, "ano_letivo")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        codigos_raw = request.query_params.getlist("codigos_alunos")
        codigos: list[int] = []
        for codigo in codigos_raw:
            try:
                codigos.append(int(codigo))
            except (TypeError, ValueError):
                return Response(
                    {
                        "detail": (
                            "codigos_alunos deve conter apenas inteiros: "
                            f"recebido {codigo!r}."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        dados = services.verificar_alunos_em_turma_pap(
            ano_letivo=ano, codigos_alunos=codigos
        )
        return Response(AlunoTurmaProgramaPapSerializer(dados, many=True).data)


# ---------------------------------------------------------------------------
# EP-04 — GET /pap/ano-corrente
# ---------------------------------------------------------------------------
class ObterAlunosPapAnoCorrenteView(APIView):
    """Lista alunos PAP do ano corrente."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="Listar alunos PAP do ano corrente",
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(self, request: Request) -> HttpResponse:
        # O service devolve JSON pronto (json_agg no Postgres) e o
        # GZipMiddleware global comprime com Content-Length correto.
        # Streaming foi descartado: o WSGIServer (runserver) não emite
        # Transfer-Encoding: chunked e o Chrome falha a renderizar
        # respostas grandes sem length nem chunked.
        return HttpResponse(
            services.obter_alunos_pap_ano_corrente_json(),
            content_type="application/json",
        )


# ---------------------------------------------------------------------------
# EP-05 — GET /pap/ano-letivo/{ano_letivo}
# ---------------------------------------------------------------------------
class ObterAlunosPapPorAnoLetivoView(APIView):
    """Lista alunos PAP por ano letivo."""

    @extend_schema(
        tags=_TAG_PAP,
        summary="Listar alunos PAP por ano letivo",
        parameters=[
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
        ],
        responses={200: AlunoTurmaPapSerializer(many=True)},
    )
    def get(
        self, request: Request, ano_letivo: str
    ) -> HttpResponse | Response:
        try:
            ano = _to_int(ano_letivo, "ano_letivo")
        except ValueError as exc:
            return Response(
                {"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST
            )

        return HttpResponse(
            services.obter_alunos_pap_por_ano_json(ano_letivo=ano),
            content_type="application/json",
        )


# -------------------------------------------------------------------
# EP-06 — GET
# /{codigo_aluno}/turmas-programa/{ano_letivo}/componentes-curriculares
# -------------------------------------------------------------------
class ObterComponentesCurricularesTurmasProgramaAlunoView(APIView):
    """Lista componentes curriculares das turmas de programa do aluno."""

    @extend_schema(
        tags=_TAG_PAP,
        summary=("Componentes curriculares das turmas de programa do aluno"),
        parameters=[
            OpenApiParameter("codigo_aluno", str, OpenApiParameter.PATH),
            OpenApiParameter("ano_letivo", int, OpenApiParameter.PATH),
        ],
        responses={200: ComponenteTurmaProgramaAlunoSerializer(many=True)},
    )
    def get(
        self, request: Request, codigo_aluno: str, ano_letivo: str
    ) -> Response:
        try:
            codigo = _to_int(codigo_aluno, "codigo_aluno")
            ano = _to_int(ano_letivo, "ano_letivo")
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
# EP-07 — GET /srm-paee/aluno/{codigo_aluno}
# ---------------------------------------------------------------------------
class ObterDadosSrmPaeeColaborativoView(APIView):
    """Retorna dados de SRM/PAEE colaborativo do aluno."""

    @extend_schema(
        tags=_TAG_PAEE,
        summary="Dados de SRM/PAEE colaborativo do aluno",
        parameters=[
            OpenApiParameter("codigo_aluno", str, OpenApiParameter.PATH),
        ],
        responses={200: DadosSrmPaeeColaborativoSerializer(many=True)},
    )
    def get(self, request: Request, codigo_aluno: str) -> Response:
        try:
            codigo = _to_int(codigo_aluno, "codigo_aluno")
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
    """Filtra os códigos de turma que são turmas de programa."""

    @extend_schema(
        tags=_TAG_TURMAS,
        summary="Filtrar códigos de turma que são turmas de programa",
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
