"""Serializers DRF do domínio Programas.

Mapeiam os DTOs retornados por apps.programas.services para o shape
camelCase esperado pelos consumidores do contrato legado (EP-01 a EP-07).

EP-08 retorna list[str] cru — sem serializer dedicado.

EP-01 retorna shape reduzido: campos de aluno (nomeAluno, dataNascimento
etc.) e pedagógico (etapaEnsino, cicloEnsino) são responsabilidade de
outros domínios e serão agregados pelo Transition Gateway.
"""

from typing import Any

from rest_framework import serializers


class TurmaSrmRegularDoAlunoSerializer(serializers.Serializer):
    """EP-01 — Turmas SRM/regular do aluno PAEE (shape reduzido).

    Campos out-of-scope (vindos via Transition Gateway, agregando MS
    Alunos / MS Pedagógico): nomeAluno, nomeSocialAluno, dataNascimento,
    numeroAlunoChamada, nomeResponsavel, tipoResponsavel,
    celularResponsavel, dataAtualizacaoContato, codigoTipoTurma,
    etapaEnsino, cicloEnsino, descEtapaEnsino, descCicloEnsino,
    dataAtualizacaoTabela.
    """

    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    anoLetivo = serializers.IntegerField(source="ano_letivo")
    tipoTurno = serializers.IntegerField(source="tipo_turno", allow_null=True)
    codigoSituacaoMatricula = serializers.IntegerField(
        source="codigo_situacao_matricula"
    )
    situacaoMatricula = serializers.CharField(source="situacao_matricula")
    dataSituacao = serializers.DateField(
        source="data_situacao", allow_null=True
    )
    turmaNome = serializers.CharField(source="turma_nome")


class TurmaPapResumoSerializer(serializers.Serializer):
    """EP-02 — Turmas PAP da UE no ano letivo."""

    codigoTurma = serializers.CharField(source="codigo_turma")
    turmaNome = serializers.CharField(source="turma_nome")


class AlunoTurmaProgramaPapSerializer(serializers.Serializer):
    """EP-03 — Verificação de alunos PAP."""

    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoComponente = serializers.IntegerField(source="codigo_componente")
    descricao = serializers.CharField()


class AlunoTurmaPapSerializer(serializers.Serializer):
    """EP-04 / EP-05 — Alunos PAP do ano corrente / por ano letivo."""

    anoLetivo = serializers.IntegerField(source="ano_letivo")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoUe = serializers.CharField(source="codigo_ue")
    codigoDre = serializers.CharField(source="codigo_dre")
    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    componenteCurricularId = serializers.IntegerField(
        source="componente_curricular_id"
    )


class ComponenteTurmaProgramaAlunoSerializer(serializers.Serializer):
    """EP-06 — Componentes das turmas de programa do aluno."""

    codigoAluno = serializers.CharField(source="codigo_aluno")
    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoComponenteCurricular = serializers.IntegerField(
        source="codigo_componente_curricular"
    )
    nomeComponenteCurricular = serializers.CharField(
        source="nome_componente_curricular"
    )


class DadosSrmPaeeColaborativoSerializer(serializers.Serializer):
    """EP-07 — Dados de SRM/PAEE colaborativo do aluno.

    OBS: ``situacaoMatricula`` é exposta como string ("1") preservando o
    contrato do legado (que retornava o valor de st_matricula como char).
    """

    codigoTurma = serializers.IntegerField(source="codigo_turma")
    codigoEscola = serializers.CharField(source="codigo_escola")
    turno = serializers.CharField()
    componente = serializers.CharField()
    codigoComponente = serializers.IntegerField(source="codigo_componente")
    codigoAluno = serializers.IntegerField(source="codigo_aluno")
    situacaoMatricula = serializers.CharField(source="situacao_matricula")
    dataMatricula = serializers.DateField(source="data_matricula")


class TurmasProgramaRequestSerializer(serializers.Serializer):
    """EP-08 — Body de POST /turmas/turmas-programa.

    Aceita uma lista de strings com códigos de turma a verificar. Fiel
    ao contrato legado (``IEnumerable<string>``).
    """

    codigos_turmas = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """O legado aceita o body como uma lista crua [str, str, ...].
        Encapsulamos para o ListField validar normalmente.
        """
        if isinstance(data, list):
            data = {"codigos_turmas": data}
        return super().to_internal_value(data)
