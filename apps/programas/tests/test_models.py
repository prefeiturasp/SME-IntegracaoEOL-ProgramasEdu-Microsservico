"""Testes dos models read-only do app programas — __str__ e shape básico."""

from __future__ import annotations

from datetime import datetime

from django.test import TestCase

from apps.programas.enums import (
    CategoriaPrograma,
    SituacaoMatricula,
    SituacaoTurma,
)
from apps.programas.models import (
    AlunoPapAnoLetivo,
    AlunoPapAnoLetivoHistorico,
    ComponenteCurricularPrograma,
    MatriculaTurmaPrograma,
    TipoPrograma,
    TurmaPrograma,
    TurmaProgramaComponenteCurricular,
)
from apps.programas.tests.helpers import agora


class TipoProgramaTestCase(TestCase):
    """Valida representação e mapeamento do model TipoPrograma."""

    def test_str(self) -> None:
        """Verifica a string amigável do tipo de programa."""
        tipo = TipoPrograma(
            codigo_tipo_programa=649,
            nome="PAP Recuperação",
            categoria=CategoriaPrograma.PAP,
        )
        self.assertEqual(str(tipo), "PAP Recuperação (649)")

    def test_db_table(self) -> None:
        """Verifica o nome da tabela mapeada."""
        self.assertEqual(TipoPrograma._meta.db_table, "tipo_programa")


class ComponenteCurricularProgramaTestCase(TestCase):
    """Valida representação do model ComponenteCurricularPrograma."""

    def test_str_inclui_categoria(self) -> None:
        """Verifica que a string amigável inclui nome, código e categoria."""
        comp = ComponenteCurricularPrograma(
            codigo_componente_curricular=1770,
            nome_componente_curricular="PAP PROJETO COLABORATIVO",
            categoria=CategoriaPrograma.PAP,
            vigente=True,
        )
        resultado = str(comp)
        self.assertIn("PAP PROJETO COLABORATIVO", resultado)
        self.assertIn("1770", resultado)
        self.assertIn("PAP", resultado)


class TurmaProgramaTestCase(TestCase):
    """Valida representação do model TurmaPrograma."""

    def test_str_inclui_codigo_e_ano(self) -> None:
        """Verifica se a string amigável inclui código da turma e ano."""
        turma = TurmaPrograma(
            codigo_turma=3082743,
            nome_turma="2A PAP",
            codigo_ue="019660",
            codigo_dre="108400",
            ano_letivo=2026,
            situacao="O",
            categoria=CategoriaPrograma.PAP,
            criado_em=agora(),
        )
        self.assertEqual(str(turma), "2A PAP (3082743) — 2026")


class TurmaProgramaComponenteCurricularTestCase(TestCase):
    """Valida representação do model TurmaProgramaComponenteCurricular."""

    def test_str(self) -> None:
        """Verifica que a string amigável inclui turma e componente."""
        registro = TurmaProgramaComponenteCurricular(
            codigo_turma=3082743,
            codigo_componente_curricular=1770,
            nome_componente_curricular="PAP PROJETO COLABORATIVO",
            criado_em=agora(),
        )
        resultado = str(registro)
        self.assertIn("3082743", resultado)
        self.assertIn("PAP PROJETO COLABORATIVO", resultado)
        self.assertIn("1770", resultado)


class MatriculaTurmaProgramaTestCase(TestCase):
    """Valida representação do model MatriculaTurmaPrograma."""

    def test_str(self) -> None:
        """Verifica que a string amigável inclui aluno, turma e componente."""
        matricula = MatriculaTurmaPrograma(
            codigo_aluno=6730137,
            codigo_turma=3082743,
            codigo_componente_curricular=1770,
            nome_componente_curricular="PAP",
            codigo_situacao_matricula=1,
            descricao_situacao_matricula="Ativo",
            data_matricula=datetime(2026, 2, 1, 11, 51, 46, 820000),
            ano_letivo=2026,
            codigo_ue="019660",
            codigo_dre="108400",
            categoria=CategoriaPrograma.PAP,
            criado_em=agora(),
        )
        resultado = str(matricula)
        self.assertIn("6730137", resultado)
        self.assertIn("3082743", resultado)
        self.assertIn("1770", resultado)


class AlunoPapAnoLetivoTestCase(TestCase):
    """Valida representação e mapeamento do model AlunoPapAnoLetivo."""

    def test_str_e_db_table(self) -> None:
        """Verifica a string amigável e o mapeamento read-only do model."""
        aluno = AlunoPapAnoLetivo(
            codigo_aluno=6730137,
            codigo_turma=3082743,
            codigo_componente_curricular=1770,
            ano_letivo=2026,
            codigo_ue="019660",
            codigo_dre="108400",
        )
        resultado = str(aluno)
        self.assertIn("6730137", resultado)
        self.assertIn("3082743", resultado)
        self.assertIn("1770", resultado)
        self.assertIn("2026", resultado)
        self.assertEqual(
            AlunoPapAnoLetivo._meta.db_table, "aluno_pap_ano_letivo"
        )
        self.assertFalse(AlunoPapAnoLetivo._meta.managed)


class AlunoPapAnoLetivoHistoricoTestCase(TestCase):
    """Valida representação e mapeamento do model AlunoPapAnoLetivoHistorico."""

    def test_str_e_db_table(self) -> None:
        """Verifica a string amigável e o mapeamento read-only do histórico."""
        aluno = AlunoPapAnoLetivoHistorico(
            codigo_aluno=6730137,
            codigo_turma=3082743,
            codigo_componente_curricular=1770,
            ano_letivo=2026,
            codigo_ue="019660",
            codigo_dre="108400",
        )
        resultado = str(aluno)
        self.assertIn("6730137", resultado)
        self.assertIn("histórico", resultado)
        self.assertEqual(
            AlunoPapAnoLetivoHistorico._meta.db_table,
            "aluno_pap_ano_letivo_historico",
        )
        self.assertFalse(AlunoPapAnoLetivoHistorico._meta.managed)


class SituacaoTurmaGetDescricaoTestCase(TestCase):
    """Valida a tradução de códigos em SituacaoTurma.get_descricao."""

    def test_none_retorna_nao_informada(self) -> None:
        """Verifica que código None resulta em 'Não Informada'."""
        self.assertEqual(SituacaoTurma.get_descricao(None), "Não Informada")

    def test_codigos_validos(self) -> None:
        """Verifica a tradução de cada código válido de situação de turma."""
        casos = [
            ("O", "Organizada"),
            ("A", "Não Organizada"),
            ("C", "Concluída"),
            ("E", "Extinta"),
        ]
        for codigo, esperado in casos:
            with self.subTest(codigo=codigo):
                self.assertEqual(SituacaoTurma.get_descricao(codigo), esperado)

    def test_codigo_desconhecido_retorna_desconhecido(self) -> None:
        """Verifica que código fora do enum resulta em 'Desconhecido'."""
        self.assertEqual(SituacaoTurma.get_descricao("X"), "Desconhecido")


class SituacaoMatriculaGetDescricaoTestCase(TestCase):
    """Valida a tradução de códigos em SituacaoMatricula.get_descricao."""

    def test_none_retorna_nao_informada(self) -> None:
        """Verifica que código None resulta em 'Não Informada'."""
        self.assertEqual(
            SituacaoMatricula.get_descricao(None), "Não Informada"
        )

    def test_codigo_nao_numerico_retorna_desconhecido(self) -> None:
        """Verifica que strings não numéricas resultam em 'Desconhecido'."""
        self.assertEqual(
            SituacaoMatricula.get_descricao("abc"), "Desconhecido"
        )

    def test_codigo_int_valido(self) -> None:
        """Verifica a tradução de um código inteiro válido."""
        self.assertEqual(SituacaoMatricula.get_descricao(1), "Ativo")

    def test_codigo_string_numerica(self) -> None:
        """Verifica que strings numéricas são aceitas como código."""
        self.assertEqual(SituacaoMatricula.get_descricao("5"), "Concluído")

    def test_todos_os_codigos_validos(self) -> None:
        """Verifica a tradução de todos os códigos de situação de matrícula."""
        esperados = {
            1: "Ativo",
            2: "Desistente",
            3: "Transferido",
            4: "Vínculo Indevido",
            5: "Concluído",
            6: "Pendente de Rematrícula",
            7: "Falecido",
            8: "Não Compareceu",
            10: "Rematriculado",
            11: "Deslocamento",
            12: "Cessado",
            13: "Sem continuidade",
            14: "Remanejado Saída",
            15: "Reclassificado Saída",
            16: "Transferido SED",
            17: "Dispensado Ed. Física",
        }
        for codigo, esperado in esperados.items():
            with self.subTest(codigo=codigo):
                self.assertEqual(
                    SituacaoMatricula.get_descricao(codigo), esperado
                )

    def test_codigo_inteiro_desconhecido_retorna_desconhecido(self) -> None:
        """Verifica que código fora do enum resulta em 'Desconhecido'."""
        self.assertEqual(SituacaoMatricula.get_descricao(99), "Desconhecido")
