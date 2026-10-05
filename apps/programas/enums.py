"""Enums e mapeamentos do domínio Programas."""

from enum import IntEnum, StrEnum

from django.db import models


class CategoriaPrograma(models.TextChoices):
    """Categoria de programa — PAP ou PAEE."""

    PAP = "PAP", "PAP"
    PAEE = "PAEE", "PAEE"


class SituacaoTurma(StrEnum):
    """Situação da turma escolar."""

    ORGANIZADA = "O"
    NAO_ORGANIZADA = "A"
    CONCLUIDA = "C"
    EXTINTA = "E"

    @classmethod
    def get_descricao(cls, codigo: str | None) -> str:
        """Retorna a descrição amigável para o código.

        Args:
            codigo: Código da situação. ``None`` é aceito.

        Returns:
            Descrição correspondente. ``"Não Informada"`` quando ``codigo``
            é ``None`` e ``"Desconhecido"`` para códigos fora do enum.
        """
        if codigo is None:
            return "Não Informada"

        mapeamento = {
            cls.ORGANIZADA: "Organizada",
            cls.NAO_ORGANIZADA: "Não Organizada",
            cls.CONCLUIDA: "Concluída",
            cls.EXTINTA: "Extinta",
        }
        try:
            return mapeamento[cls(codigo)]
        except ValueError:
            return "Desconhecido"


class SituacaoMatricula(IntEnum):
    """Situação da matrícula do aluno."""

    ATIVO = 1
    DESISTENTE = 2
    TRANSFERIDO = 3
    VINCULO_INDEVIDO = 4
    CONCLUIDO = 5
    PENDENTE_REMATRICULA = 6
    FALECIDO = 7
    NAO_COMPARECEU = 8
    REMATRICULADO = 10
    DESLOCAMENTO = 11
    CESSADO = 12
    SEM_CONTINUIDADE = 13
    REMANEJADO_SAIDA = 14
    RECLASSIFICADO_SAIDA = 15
    TRANSFERIDO_SED = 16
    DISPENSADO_ED_FISICA = 17

    @classmethod
    def get_descricao(cls, codigo: int | str | None) -> str:
        """Retorna a descrição amigável para o código.

        Args:
            codigo: Código inteiro ou string numérica. ``None`` é aceito.

        Returns:
            Descrição correspondente. ``"Não Informada"`` quando ``codigo``
            é ``None`` e ``"Desconhecido"`` para valores não numéricos ou
            fora do enum.
        """
        if codigo is None:
            return "Não Informada"

        try:
            cod_int = int(codigo)
        except (ValueError, TypeError):
            return "Desconhecido"

        mapeamento = {
            cls.ATIVO: "Ativo",
            cls.DESISTENTE: "Desistente",
            cls.TRANSFERIDO: "Transferido",
            cls.VINCULO_INDEVIDO: "Vínculo Indevido",
            cls.CONCLUIDO: "Concluído",
            cls.PENDENTE_REMATRICULA: "Pendente de Rematrícula",
            cls.FALECIDO: "Falecido",
            cls.NAO_COMPARECEU: "Não Compareceu",
            cls.REMATRICULADO: "Rematriculado",
            cls.DESLOCAMENTO: "Deslocamento",
            cls.CESSADO: "Cessado",
            cls.SEM_CONTINUIDADE: "Sem continuidade",
            cls.REMANEJADO_SAIDA: "Remanejado Saída",
            cls.RECLASSIFICADO_SAIDA: "Reclassificado Saída",
            cls.TRANSFERIDO_SED: "Transferido SED",
            cls.DISPENSADO_ED_FISICA: "Dispensado Ed. Física",
        }
        try:
            return mapeamento[cls(cod_int)]
        except ValueError:
            return "Desconhecido"


SITUACOES_MATRICULA_VALIDAS: tuple[int, ...] = (
    SituacaoMatricula.ATIVO,
    SituacaoMatricula.CONCLUIDO,
    SituacaoMatricula.PENDENTE_REMATRICULA,
    SituacaoMatricula.REMATRICULADO,
    SituacaoMatricula.SEM_CONTINUIDADE,
)

SITUACOES_TURMA_ATIVAS: tuple[str, ...] = (
    SituacaoTurma.ORGANIZADA,
    SituacaoTurma.NAO_ORGANIZADA,
    SituacaoTurma.CONCLUIDA,
    SituacaoTurma.EXTINTA,
)

CODIGO_COMPONENTE_PAEE_SRM: int = 1030
