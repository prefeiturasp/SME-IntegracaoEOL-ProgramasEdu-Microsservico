"""Rotas da API do domínio Programas."""

from django.urls import path

from apps.programas.api.views import (
    ObterAlunosPapAnoCorrenteView,
    ObterAlunosPapPorAnoLetivoView,
    ObterComponentesCurricularesTurmasProgramaAlunoView,
    ObterDadosSrmPaeeColaborativoView,
    ObterTurmasPapView,
    ObterTurmasProgramaView,
    ObterTurmaSrmERegularDoAlunoView,
    VerificarSeAlunosSaoTurmaProgramaPapView,
)

urlpatterns = [
    # ------------------------------------------------------------------
    # AlunoController do legado → /api/alunos/...
    # ------------------------------------------------------------------
    path(
        "alunos/paee/turma-srm-e-regular/aluno/<str:codigo_aluno>",
        ObterTurmaSrmERegularDoAlunoView.as_view(),
        name="obter-turma-srm-e-regular-do-aluno",
    ),
    path(
        "alunos/turmas-pap/<str:ano_letivo>/ues/<str:codigo_escola>",
        ObterTurmasPapView.as_view(),
        name="obter-turmas-pap",
    ),
    path(
        "alunos/alunos-pap/<str:ano_letivo>",
        VerificarSeAlunosSaoTurmaProgramaPapView.as_view(),
        name="verificar-se-alunos-sao-turma-programa-pap",
    ),
    path(
        "alunos/pap/ano-corrente",
        ObterAlunosPapAnoCorrenteView.as_view(),
        name="obter-alunos-pap-ano-corrente",
    ),
    path(
        "alunos/pap/ano-letivo/<str:ano_letivo>",
        ObterAlunosPapPorAnoLetivoView.as_view(),
        name="obter-alunos-pap-por-ano-letivo",
    ),
    path(
        "alunos/<str:codigo_aluno>/turmas-programa/<str:ano_letivo>"
        "/componentes-curriculares",
        ObterComponentesCurricularesTurmasProgramaAlunoView.as_view(),
        name="obter-componentes-curriculares-turmas-programa-aluno",
    ),
    path(
        "alunos/srm-paee/aluno/<str:codigo_aluno>",
        ObterDadosSrmPaeeColaborativoView.as_view(),
        name="obter-dados-srm-paee-colaborativo",
    ),
    # ------------------------------------------------------------------
    # TurmaController do legado → /api/turmas/...
    # ------------------------------------------------------------------
    path(
        "turmas/turmas-programa",
        ObterTurmasProgramaView.as_view(),
        name="obter-turmas-programa",
    ),
]
