"""Testes das funções de query em apps/programas/services.py."""

from __future__ import annotations

from datetime import UTC, date, datetime
from unittest.mock import MagicMock, patch

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
    """Valida a busca de turmas PAEE do aluno."""

    def test_retorna_apenas_paee_do_aluno(self) -> None:
        """Verifica que somente turmas PAEE do aluno são retornadas."""
        seed_matriculas()
        resultado = services.obter_turmas_paee_do_aluno(codigo_aluno=5285836)
        self.assertEqual(len(resultado), 1)
        item = resultado[0]
        self.assertEqual(item.codigo_aluno, 5285836)
        self.assertEqual(item.codigo_turma, 3105288)
        self.assertEqual(item.tipo_turno, 2)
        self.assertEqual(item.turma_nome, "SD")
        self.assertEqual(item.codigo_situacao_matricula, 1)
        self.assertEqual(item.situacao_matricula, "Ativo")

    def test_retorna_vazio_se_aluno_nao_tem_paee(self) -> None:
        """Verifica que aluno sem matrícula PAEE recebe lista vazia."""
        seed_matriculas()
        resultado = services.obter_turmas_paee_do_aluno(codigo_aluno=6730137)
        self.assertEqual(resultado, [])

    def test_filtra_por_situacao_matricula(self) -> None:
        """Verifica que matrículas em situação inválida são excluídas."""
        seed_matriculas()
        MatriculaTurmaPrograma.objects.create(
            codigo_aluno=999,
            codigo_turma=3105288,
            codigo_componente_curricular=1030,
            nome_componente_curricular="SRM",
            codigo_situacao_matricula=2,
            descricao_situacao_matricula="Desistente",
            data_matricula=datetime(2026, 2, 1, 11, 51, 46, 820000),
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
    """Valida a listagem de turmas PAP por UE e ano letivo."""

    def test_retorna_turmas_pap_da_ue(self) -> None:
        """Verifica que as turmas PAP da UE/ano são retornadas e nomeadas."""
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
        """Verifica que UE sem turma PAP recebe lista vazia."""
        seed_turmas()
        resultado = services.listar_turmas_pap_da_ue(
            ano_letivo=2026, codigo_ue="999999"
        )
        self.assertEqual(resultado, [])

    def test_nao_retorna_paee(self) -> None:
        """Verifica que turmas PAEE não vazam pela consulta PAP."""
        seed_turmas()
        resultado = services.listar_turmas_pap_da_ue(
            ano_letivo=2026, codigo_ue="092959"
        )
        self.assertEqual(resultado, [])

    def test_descricao_grade_nula_retorna_so_nome_turma(self) -> None:
        """Verifica que turma sem descrição de grade usa apenas nome_turma."""
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
    """Valida a verificação de alunos pertencentes a turmas PAP."""

    def test_retorna_alunos_pap_validos(self) -> None:
        """Verifica que alunos PAP com matrícula válida são retornados."""
        seed_matriculas()
        resultado = services.verificar_alunos_em_turma_pap(
            ano_letivo=2026, codigos_alunos=[6730137]
        )
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo_aluno, 6730137)
        self.assertEqual(resultado[0].codigo_componente, 1770)
        self.assertEqual(resultado[0].descricao, "PAP PROJETO COLABORATIVO")

    def test_lista_vazia_retorna_vazio(self) -> None:
        """Verifica que entrada vazia gera saída vazia."""
        seed_matriculas()
        resultado = services.verificar_alunos_em_turma_pap(
            ano_letivo=2026, codigos_alunos=[]
        )
        self.assertEqual(resultado, [])

    def test_aluno_paee_nao_aparece(self) -> None:
        """Verifica que aluno só PAEE não aparece na consulta PAP."""
        seed_matriculas()
        resultado = services.verificar_alunos_em_turma_pap(
            ano_letivo=2026, codigos_alunos=[5285836]
        )
        self.assertEqual(resultado, [])


class ListarAlunosPapAnoCorrenteTestCase(TestCase):
    """Valida a listagem de alunos PAP do ano corrente."""

    def test_filtra_por_ano_corrente(self) -> None:
        """Verifica que apenas matrículas do ano corrente são retornadas."""
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
        """Verifica que matrículas de outro ano não aparecem."""
        seed_matriculas()
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2030, 1, 1, tzinfo=UTC),
        ):
            resultado = services.listar_alunos_pap_ano_corrente()
        self.assertEqual(resultado, [])


class ListarAlunosPapPorAnoTestCase(TestCase):
    """Valida a listagem de alunos PAP por ano letivo encerrado."""

    def test_retorna_alunos_pap_do_ano(self) -> None:
        """Verifica que alunos PAP do ano encerrado são retornados."""
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
        """Verifica que ano corrente é tratado como inválido."""
        seed_matriculas()
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2026, 5, 1, tzinfo=UTC),
        ):
            resultado = services.listar_alunos_pap_por_ano(ano_letivo=2026)
        self.assertEqual(resultado, [])


class ConsultarAlunosPapJsonPostgresqlTestCase(TestCase):
    """Valida a serialização otimizada executada diretamente no PostgreSQL."""

    @patch("apps.programas.services.connection")
    def test_consulta_tabela_atual_e_codifica_texto(
        self, connection_mock: MagicMock
    ) -> None:
        """Executa a consulta atual e converte o JSON textual para bytes."""
        connection_mock.vendor = "postgresql"
        cursor = connection_mock.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = ('[{"codigo_aluno":6730137}]',)

        resultado = services._consultar_alunos_pap_json(ano_letivo=2026)

        cursor.execute.assert_called_once_with(
            services._SQL_ALUNOS_PAP_ATUAL,
            {"ano_letivo": 2026},
        )
        self.assertEqual(resultado, b'[{"codigo_aluno":6730137}]')

    @patch("apps.programas.services.connection")
    def test_consulta_historico_e_preserva_bytes(
        self, connection_mock: MagicMock
    ) -> None:
        """Executa a consulta histórica e preserva um resultado em bytes."""
        connection_mock.vendor = "postgresql"
        cursor = connection_mock.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = (b"[]",)

        resultado = services._consultar_alunos_pap_json(
            ano_letivo=2025,
            historico=True,
        )

        cursor.execute.assert_called_once_with(
            services._SQL_ALUNOS_PAP_HISTORICO,
            {"ano_letivo": 2025},
        )
        self.assertEqual(resultado, b"[]")

    @patch("apps.programas.services.connection")
    def test_retorna_array_vazio_quando_consulta_nao_traz_linha(
        self, connection_mock: MagicMock
    ) -> None:
        """Normaliza a ausência de linha para um array JSON vazio."""
        connection_mock.vendor = "postgresql"
        cursor = connection_mock.cursor.return_value.__enter__.return_value
        cursor.fetchone.return_value = None

        resultado = services._consultar_alunos_pap_json(ano_letivo=2026)

        self.assertEqual(resultado, b"[]")


class ListarComponentesTurmasAlunoTestCase(TestCase):
    """Valida a listagem de componentes das turmas do aluno."""

    def test_retorna_componentes_do_aluno(self) -> None:
        """Verifica os componentes das turmas de programa do aluno."""
        seed_matriculas()
        resultado = services.listar_componentes_turmas_aluno(
            codigo_aluno=6730137, ano_letivo=2026
        )
        self.assertEqual(len(resultado), 1)
        self.assertEqual(resultado[0].codigo_aluno, "6730137")
        self.assertEqual(resultado[0].codigo_turma, 3082743)
        self.assertEqual(resultado[0].codigo_componente_curricular, 1770)


class ObterDadosSrmPaeeAlunoTestCase(TestCase):
    """Valida a obtenção de dados SRM/PAEE colaborativo do aluno."""

    def test_retorna_dados_srm(self) -> None:
        """Verifica os campos retornados para o aluno com matrícula SRM."""
        seed_matriculas()
        resultado = services.obter_dados_srm_paee_aluno(codigo_aluno=5285836)
        self.assertEqual(len(resultado), 1)
        item = resultado[0]
        self.assertEqual(item.codigo_turma, 3105288)
        self.assertEqual(item.codigo_escola, "092959")
        self.assertEqual(item.turno, "Tarde")
        self.assertEqual(item.componente, "SRM")
        self.assertEqual(item.codigo_componente, 1030)
        self.assertEqual(item.situacao_matricula, "1")

    def test_aluno_sem_srm_retorna_vazio(self) -> None:
        """Verifica que aluno sem SRM recebe lista vazia."""
        seed_matriculas()
        resultado = services.obter_dados_srm_paee_aluno(codigo_aluno=6730137)
        self.assertEqual(resultado, [])

    @patch("apps.programas.services.TurmaPrograma")
    @patch("apps.programas.services.MatriculaTurmaPrograma")
    def test_converte_data_matricula_para_datetime(
        self,
        matricula_model_mock: MagicMock,
        turma_model_mock: MagicMock,
    ) -> None:
        """Converte uma data sem horário antes de montar o contrato."""
        matriculas = [
            {
                "codigo_aluno": 5285836,
                "codigo_turma": 3105288,
                "codigo_ue": "092959",
                "codigo_componente_curricular": 1030,
                "nome_componente_curricular": "SRM",
                "codigo_situacao_matricula": 1,
                "data_matricula": date(2026, 2, 1),
            }
        ]
        matricula_model_mock.objects.filter.return_value.values.return_value.order_by.return_value = (  # noqa: E501
            matriculas
        )
        turma_model_mock.objects.filter.return_value.values.return_value = [
            {"codigo_turma": 3105288, "descricao_turno": "Tarde"}
        ]

        resultado = services.obter_dados_srm_paee_aluno(codigo_aluno=5285836)

        self.assertEqual(
            resultado[0].data_matricula,
            datetime(2026, 2, 1),
        )


class FiltrarCodigosQueSaoTurmaProgramaTestCase(TestCase):
    """Valida o filtro de códigos que correspondem a turmas de programa."""

    def test_retorna_apenas_existentes(self) -> None:
        """Verifica que apenas códigos existentes são devolvidos."""
        seed_turmas()
        resultado = services.filtrar_codigos_que_sao_turma_programa(
            codigos_turmas=["3082743", "3105288", "9999999"]
        )
        self.assertEqual(sorted(resultado), ["3082743", "3105288"])

    def test_lista_vazia_retorna_vazio(self) -> None:
        """Verifica que entrada vazia gera saída vazia."""
        self.assertEqual(
            services.filtrar_codigos_que_sao_turma_programa(codigos_turmas=[]),
            [],
        )

    def test_codigo_invalido_e_ignorado(self) -> None:
        """Verifica que códigos não numéricos são ignorados."""
        seed_turmas()
        resultado = services.filtrar_codigos_que_sao_turma_programa(
            codigos_turmas=["abc", "3082743"]
        )
        self.assertEqual(resultado, ["3082743"])

    def test_so_invalidos_retorna_vazio(self) -> None:
        """Verifica que entrada toda inválida resulta em lista vazia."""
        seed_turmas()
        resultado = services.filtrar_codigos_que_sao_turma_programa(
            codigos_turmas=["abc", "xyz"]
        )
        self.assertEqual(resultado, [])
