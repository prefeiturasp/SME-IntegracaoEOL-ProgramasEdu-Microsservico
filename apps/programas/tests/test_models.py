"""Testes dos models read-only do app programas — __str__ e shape básico."""

from __future__ import annotations

from datetime import date

from django.test import TestCase

from apps.programas.enums import CategoriaPrograma
from apps.programas.models import (
    ComponenteCurricularPrograma,
    MatriculaTurmaPrograma,
    TipoPrograma,
    TurmaPrograma,
    TurmaProgramaComponenteCurricular,
)
from apps.programas.tests.helpers import agora


class TipoProgramaTestCase(TestCase):
    def test_str(self) -> None:
        tipo = TipoPrograma(
            codigo_tipo_programa=649,
            nome="PAP Recuperação",
            categoria=CategoriaPrograma.PAP,
        )
        self.assertEqual(str(tipo), "PAP Recuperação (649)")

    def test_db_table(self) -> None:
        self.assertEqual(TipoPrograma._meta.db_table, "tipo_programa")


class ComponenteCurricularProgramaTestCase(TestCase):
    def test_str_inclui_categoria(self) -> None:
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
    def test_str_inclui_codigo_e_ano(self) -> None:
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
    def test_str(self) -> None:
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
    def test_str(self) -> None:
        matricula = MatriculaTurmaPrograma(
            codigo_aluno=6730137,
            codigo_turma=3082743,
            codigo_componente_curricular=1770,
            nome_componente_curricular="PAP",
            codigo_situacao_matricula=1,
            descricao_situacao_matricula="Ativo",
            data_matricula=date(2026, 2, 1),
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
