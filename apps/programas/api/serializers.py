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

    codigo_aluno = serializers.IntegerField()
    codigo_turma = serializers.IntegerField()
    ano_letivo = serializers.IntegerField()
    tipo_turno = serializers.IntegerField(allow_null=True)
    codigo_situacao_matricula = serializers.IntegerField()
    situacao_matricula = serializers.CharField()
    data_situacao = serializers.DateField()
    turma_nome = serializers.CharField()


class TurmaPapResumoSerializer(serializers.Serializer):
    """EP-02 — Turmas PAP da UE no ano letivo."""

    codigo_turma = serializers.CharField()
    turma_nome = serializers.CharField()


class AlunoTurmaProgramaPapSerializer(serializers.Serializer):
    """EP-03 — Verificação de alunos PAP."""

    codigo_aluno = serializers.IntegerField()
    codigo_turma = serializers.IntegerField()
    codigo_componente = serializers.IntegerField()
    descricao = serializers.CharField()


class AlunoTurmaPapSerializer(serializers.Serializer):
    """EP-04 / EP-05 — Alunos PAP do ano corrente / por ano letivo."""

    ano_letivo = serializers.IntegerField()
    codigo_turma = serializers.IntegerField()
    codigo_ue = serializers.CharField()
    codigo_dre = serializers.CharField()
    codigo_aluno = serializers.IntegerField()
    componente_curricular_id = serializers.IntegerField()


class ComponenteTurmaProgramaAlunoSerializer(serializers.Serializer):
    """EP-06 — Componentes das turmas de programa do aluno."""

    codigo_aluno = serializers.CharField()
    codigo_turma = serializers.IntegerField()
    codigo_componente_curricular = serializers.IntegerField()
    nome_componente_curricular = serializers.CharField()


class DadosSrmPaeeColaborativoSerializer(serializers.Serializer):
    """EP-07 — Dados de SRM/PAEE colaborativo do aluno.

    OBS: ``situacaoMatricula`` é exposta como string ("1") preservando o
    contrato do legado (que retornava o valor de st_matricula como char).
    """

    codigo_turma = serializers.IntegerField()
    codigo_escola = serializers.CharField()
    turno = serializers.CharField()
    componente = serializers.CharField()
    codigo_componente = serializers.IntegerField()
    codigo_aluno = serializers.IntegerField()
    situacao_matricula = serializers.CharField()
    data_matricula = serializers.DateField()


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
