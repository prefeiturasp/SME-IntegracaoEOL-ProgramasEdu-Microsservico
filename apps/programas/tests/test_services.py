"""Testes das funções de query em apps/programas/services.py."""

from __future__ import annotations

from datetime import UTC, date, datetime
from unittest.mock import patch

from django.test import TestCase

from apps.programas import services
from apps.programas.enums import CategoriaPrograma
from apps.programas.models import MatriculaTurmaPrograma, TurmaPrograma
from apps.programas.tests.helpers import (
    agora,
    seed_matriculas,
    seed_turmas,
)


class ObterTurmasPaeeDoAlunoTestCase(TestCase):
    def test_retorna_apenas_paee_do_aluno(self) -> None:
        seed_matriculas()
        resultado = services.obter_turmas_paee_do_aluno(codigo_aluno=5285836)
        self.assertEqual(len(resultado), 1)
        item = resultado[0]
        self.assertEqual(item.codigo_aluno, 5285836)
        self.assertEqual(item.codigo_turma, 3105288)
        self.assertEqual(item.tipo_turno, 2)
        # EP-01 não concatena descrição da grade — preserva apenas
        # nome_turma (o turmaNome agregado é usado pelo EP-02).
        self.assertEqual(item.turma_nome, "SD")
        self.assertEqual(item.codigo_situacao_matricula, 1)
        self.assertEqual(item.situacao_matricula, "Ativo")

    def test_retorna_vazio_se_aluno_nao_tem_paee(self) -> None:
        seed_matriculas()
        resultado = services.obter_turmas_paee_do_aluno(codigo_aluno=6730137)
        self.assertEqual(resultado, [])

    def test_filtra_por_situacao_matricula(self) -> None:
        seed_matriculas()
        MatriculaTurmaPrograma.objects.create(
            codigo_aluno=999,
            codigo_turma=3105288,
            codigo_componente_curricular=1030,
            nome_componente_curricular="SRM",
            codigo_situacao_matricula=2,
            descricao_situacao_matricula="Desistente",
            data_matricula=date(2026, 2, 1),
            data_situacao=date(2026, 2, 1),
            ano_letivo=2026,
            codigo_ue="092959",
            codigo_dre="108400",
            categoria=CategoriaPrograma.PAEE,
            criado_em=agora(),
        )
        resultado = services.obter_turmas_paee_do_aluno(codigo_aluno=999)
        self.assertEqual(resultado, [])


class ListarTurmasPapDaUeTestCase(TestCase):
    def test_retorna_turmas_pap_da_ue(self) -> None:
        seed_turmas()
        resultado = services.listar_turmas_pap_da_ue(
            ano_letivo=2026, codigo_ue="019660"
        )
        self.assertEqual(len(resultado), 2)
        self.assertEqual(resultado[0].codigo_turma, "3172713")
        self.assertEqual(
            resultado[0].turma_nome,
            "ID - PAP 2 ANO COLABORATIVO _ALFABETIZACAO",
        )
        self.assertEqual(resultado[1].codigo_turma, "3082743")
        self.assertEqual(
            resultado[1].turma_nome, "LC - PAP COLABORATIVO 3 / 4 E 5 ANO"
        )

    def test_retorna_vazio_para_ue_sem_pap(self) -> None:
        seed_turmas()
        resultado = services.listar_turmas_pap_da_ue(
            ano_letivo=2026, codigo_ue="999999"
        )
        self.assertEqual(resultado, [])

    def test_nao_retorna_paee(self) -> None:
        seed_turmas()
        resultado = services.listar_turmas_pap_da_ue(
            ano_letivo=2026, codigo_ue="092959"
        )
        self.assertEqual(resultado, [])

    def test_descricao_grade_nula_retorna_so_nome_turma(self) -> None:
        TurmaPrograma.objects.create(
            codigo_turma=3999999,
            nome_turma="XX",
            codigo_ue="019660",
            codigo_dre="108400",
            ano_letivo=2026,
            tipo_turno=1,
            descricao_turno="Manhã",
            descricao_grade=None,
            situacao="O",
            codigo_tipo_programa=650,
            categoria=CategoriaPrograma.PAP,
            criado_em=agora(),
            atualizado_em=agora(),
        )
        resultado = services.listar_turmas_pap_da_ue(
            ano_letivo=2026, codigo_ue="019660"
        )
        nomes = [r.turma_nome for r in resultado]
        self.assertIn("XX", nomes)


class VerificarAlunosEmTurmaPapTestCase(TestCase):
    def test_retorna_alunos_pap_validos(self) -> None:
        seed_matriculas()
        resultado = services.verificar_alunos_em_turma_pap(
            ano_letivo=2026, codigos_alunos=[6730137]
        )
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo_aluno, 6730137)
        self.assertEqual(resultado[0].codigo_componente, 1770)
        self.assertEqual(resultado[0].descricao, "PAP PROJETO COLABORATIVO")

    def test_lista_vazia_retorna_vazio(self) -> None:
        seed_matriculas()
        resultado = services.verificar_alunos_em_turma_pap(
            ano_letivo=2026, codigos_alunos=[]
        )
        self.assertEqual(resultado, [])

    def test_aluno_paee_nao_aparece(self) -> None:
        seed_matriculas()
        resultado = services.verificar_alunos_em_turma_pap(
            ano_letivo=2026, codigos_alunos=[5285836]
        )
        self.assertEqual(resultado, [])


class ListarAlunosPapAnoCorrenteTestCase(TestCase):
    def test_filtra_por_ano_corrente(self) -> None:
        seed_matriculas()
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2026, 5, 1, tzinfo=UTC),
        ):
            resultado = services.listar_alunos_pap_ano_corrente()
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].ano_letivo, 2026)
        self.assertEqual(resultado[0].codigo_aluno, 6730137)

    def test_outro_ano_retorna_vazio(self) -> None:
        seed_matriculas()
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2030, 1, 1, tzinfo=UTC),
        ):
            resultado = services.listar_alunos_pap_ano_corrente()
        self.assertEqual(resultado, [])


class ListarAlunosPapPorAnoTestCase(TestCase):
    def test_retorna_alunos_pap_do_ano(self) -> None:
        seed_matriculas()
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2030, 1, 1, tzinfo=UTC),
        ):
            resultado = services.listar_alunos_pap_por_ano(ano_letivo=2026)
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo_aluno, 6730137)
        self.assertEqual(resultado[0].codigo_ue, "019660")
        self.assertEqual(resultado[0].codigo_dre, "108400")
        self.assertEqual(resultado[0].componente_curricular_id, 1770)

    def test_ano_corrente_retorna_vazio(self) -> None:
        seed_matriculas()
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2026, 5, 1, tzinfo=UTC),
        ):
            resultado = services.listar_alunos_pap_por_ano(ano_letivo=2026)
        self.assertEqual(resultado, [])


class ListarComponentesTurmasAlunoTestCase(TestCase):
    def test_retorna_componentes_do_aluno(self) -> None:
        seed_matriculas()
        resultado = services.listar_componentes_turmas_aluno(
            codigo_aluno=6730137, ano_letivo=2026
        )
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo_aluno, "6730137")
        self.assertEqual(resultado[0].codigo_turma, 3082743)
        self.assertEqual(resultado[0].codigo_componente_curricular, 1770)


class ObterDadosSrmPaeeAlunoTestCase(TestCase):
    def test_retorna_dados_srm(self) -> None:
        seed_matriculas()
        resultado = services.obter_dados_srm_paee_aluno(codigo_aluno=5285836)
        self.assertEqual(len(resultado), 1)
        item = resultado[0]
        self.assertEqual(item.codigo_turma, 3105288)
        self.assertEqual(item.codigo_escola, "092959")
        self.assertEqual(item.turno, "Tarde")
        self.assertEqual(item.componente, "SRM")
        self.assertEqual(item.codigo_componente, 1030)
        self.assertEqual(item.situacao_matricula, "1")  # string

    def test_aluno_sem_srm_retorna_vazio(self) -> None:
        seed_matriculas()
        resultado = services.obter_dados_srm_paee_aluno(codigo_aluno=6730137)
        self.assertEqual(resultado, [])


class FiltrarCodigosQueSaoTurmaProgramaTestCase(TestCase):
    def test_retorna_apenas_existentes(self) -> None:
        seed_turmas()
        resultado = services.filtrar_codigos_que_sao_turma_programa(
            codigos_turmas=["3082743", "3105288", "9999999"]
        )
        self.assertEqual(sorted(resultado), ["3082743", "3105288"])

    def test_lista_vazia_retorna_vazio(self) -> None:
        self.assertEqual(
            services.filtrar_codigos_que_sao_turma_programa(codigos_turmas=[]),
            [],
        )

    def test_codigo_invalido_e_ignorado(self) -> None:
        seed_turmas()
        resultado = services.filtrar_codigos_que_sao_turma_programa(
            codigos_turmas=["abc", "3082743"]
        )
        self.assertEqual(resultado, ["3082743"])

    def test_so_invalidos_retorna_vazio(self) -> None:
        seed_turmas()
        resultado = services.filtrar_codigos_que_sao_turma_programa(
            codigos_turmas=["abc", "xyz"]
        )
        self.assertEqual(resultado, [])
