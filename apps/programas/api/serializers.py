"""Serializers do domínio Programas."""

from typing import Any

from rest_framework import serializers


class TurmaSrmRegularDoAlunoSerializer(serializers.Serializer):
    """Serializa turmas SRM/regular do aluno PAEE."""

    codigo_aluno = serializers.IntegerField()
    codigo_turma = serializers.IntegerField()
    ano_letivo = serializers.IntegerField()
    tipo_turno = serializers.IntegerField(allow_null=True)
    codigo_situacao_matricula = serializers.IntegerField()
    situacao_matricula = serializers.CharField()
    data_situacao = serializers.DateField()
    turma_nome = serializers.CharField()


class TurmaPapResumoSerializer(serializers.Serializer):
    """Serializa turmas PAP da UE no ano letivo."""

    codigo_turma = serializers.CharField()
    turma_nome = serializers.CharField()


class AlunoTurmaProgramaPapSerializer(serializers.Serializer):
    """Serializa alunos verificados em turmas PAP."""

    codigo_aluno = serializers.IntegerField()
    codigo_turma = serializers.IntegerField()
    codigo_componente = serializers.IntegerField()
    descricao = serializers.CharField()


class AlunoTurmaPapSerializer(serializers.Serializer):
    """Serializa alunos PAP com turma, UE e DRE."""

    ano_letivo = serializers.IntegerField()
    codigo_turma = serializers.IntegerField()
    codigo_ue = serializers.CharField()
    codigo_dre = serializers.CharField()
    codigo_aluno = serializers.IntegerField()
    componente_curricular_id = serializers.IntegerField()


class ComponenteTurmaProgramaAlunoSerializer(serializers.Serializer):
    """Serializa componentes das turmas de programa do aluno."""

    codigo_aluno = serializers.CharField()
    codigo_turma = serializers.IntegerField()
    codigo_componente_curricular = serializers.IntegerField()
    nome_componente_curricular = serializers.CharField()


class DadosSrmPaeeColaborativoSerializer(serializers.Serializer):
    """Serializa dados de SRM/PAEE colaborativo do aluno."""

    codigo_turma = serializers.IntegerField()
    codigo_escola = serializers.CharField()
    turno = serializers.CharField()
    componente = serializers.CharField()
    codigo_componente = serializers.IntegerField()
    codigo_aluno = serializers.IntegerField()
    situacao_matricula = serializers.CharField()
    data_matricula = serializers.DateTimeField()


class TurmasProgramaRequestSerializer(serializers.Serializer):
    """Serializa a lista de códigos de turma a verificar."""

    codigos_turmas = serializers.ListField(
        child=serializers.CharField(),
        allow_empty=True,
    )

    def to_internal_value(self, data: Any) -> dict[str, Any]:
        """Aceita o corpo como lista crua e encapsula para validação.

        Args:
            data: Corpo recebido, podendo ser uma lista pura de códigos.

        Returns:
            Dicionário validado no formato esperado pelo serializer.
        """
        if isinstance(data, list):
            data = {"codigos_turmas": data}
        return super().to_internal_value(data)
