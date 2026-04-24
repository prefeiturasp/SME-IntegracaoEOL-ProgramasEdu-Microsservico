"""Rotas da API do domínio Programas."""

from django.urls import path

from apps.programas.api.views import (
    ObterTurmaSrmERegularDoAlunoView,
    ObterTurmasPapView,
    VerificarSeAlunosSaoTurmaProgramaPapView,
    ObterAlunosPapAnoCorrenteView,
    ObterAlunosPapPorAnoLetivoView,
    ObterComponentesCurricularesTurmasProgramaAlunoView,
    ObterDadosSrmPaeeColaborativoView,
    ObterTurmasProgramaView
)

urlpatterns = [
    path(
        "paee/turma-srm-e-regular/aluno/<str:codigoAluno>",
        ObterTurmaSrmERegularDoAlunoView.as_view(),
        name="obter-turma-srm-e-regular-do-aluno",
    ),
    path(
        "turmas-pap/<str:anoLetivo>/ues/<str:codigoEscola>",
        ObterTurmasPapView.as_view(),
        name="obter-turmas-pap",
    ),
    path(
        "alunos-pap/<str:anoLetivo>",
        VerificarSeAlunosSaoTurmaProgramaPapView.as_view(),
        name="verificar-se-alunos-sao-turma-programa-pap",
    ),
    path(
        "pap/ano-corrente",
        ObterAlunosPapAnoCorrenteView.as_view(),
        name="obter-alunos-pap-ano-corrente",
    ),
    path(
        "pap/ano-letivo/<str:anoLetivo>",
        ObterAlunosPapPorAnoLetivoView.as_view(),
        name="obter-alunos-pap-por-ano-letivo",
    ),
    path(
        "<str:codigoAluno>/turmas-programa/<str:anoLetivo>/componentes-curriculares",
        ObterComponentesCurricularesTurmasProgramaAlunoView.as_view(),
        name="obter-componentes-curriculares-turmas-programa-aluno",
    ),
    path(
        "srm-paee/aluno/<str:codigoAluno>",
        ObterDadosSrmPaeeColaborativoView.as_view(),
        name="obter-dados-srm-paee-colaborativo",
    ),
    path(
        "turmas/turmas-programa",
        ObterTurmasProgramaView.as_view(),
        name="obter-turmas-programa",
    ),
]