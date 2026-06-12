"""Testes dos endpoints HTTP do app programas."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any
from unittest.mock import patch

from django.http import StreamingHttpResponse
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from apps.programas.tests.helpers import (
    seed_matriculas,
    seed_turmas,
)


def _autenticado() -> APIClient:
    """Retorna um APIClient com header de API key configurado."""
    cliente = APIClient()
    cliente.credentials(HTTP_X_API_KEY="test-api-key")
    return cliente


def _body_json(resp: Any) -> Any:
    """Lê o corpo JSON da resposta, inclusive em StreamingHttpResponse."""
    if isinstance(resp, StreamingHttpResponse):
        return json.loads(b"".join(resp.streaming_content).decode("utf-8"))
    return resp.json()


class AutenticacaoTestCase(TestCase):
    """Valida as respostas de autenticação dos endpoints."""

    def test_sem_api_key_retorna_401(self) -> None:
        """Verifica que requisição sem API key retorna 401."""
        cliente = APIClient()
        url = reverse("obter-alunos-pap-ano-corrente")
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_api_key_invalida_retorna_403(self) -> None:
        """Verifica que API key incorreta retorna 403."""
        cliente = APIClient()
        cliente.credentials(HTTP_X_API_KEY="errada")
        url = reverse("obter-alunos-pap-ano-corrente")
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)


class EP01TurmaSrmRegularDoAlunoTestCase(TestCase):
    """Valida o endpoint de turmas SRM/regular do aluno PAEE."""

    def test_retorna_shape_reduzido(self) -> None:
        """Verifica o shape do payload — só campos do domínio Programas."""
        seed_matriculas()
        cliente = _autenticado()
        url = reverse(
            "obter-turma-srm-e-regular-do-aluno",
            kwargs={"codigo_aluno": "5285836"},
        )
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body), 1)
        item = body[0]
        for campo in [
            "codigo_aluno",
            "codigo_turma",
            "ano_letivo",
            "tipo_turno",
            "codigo_situacao_matricula",
            "situacao_matricula",
            "data_situacao",
            "turma_nome",
        ]:
            self.assertIn(campo, item)
        for campo in [
            "nome_aluno",
            "data_nascimento",
            "nome-responsavel",
            "etapa_ensino",
            "ciclo_ensino",
        ]:
            self.assertNotIn(campo, item)

    def test_codigo_invalido_retorna_400(self) -> None:
        """Verifica que codigo_aluno não numérico retorna 400."""
        cliente = _autenticado()
        url = reverse(
            "obter-turma-srm-e-regular-do-aluno",
            kwargs={"codigo_aluno": "abc"},
        )
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, 400)


class EP02TurmasPapTestCase(TestCase):
    """Valida o endpoint de turmas PAP por UE e ano letivo."""

    def test_retorna_turmas_da_ue(self) -> None:
        """Verifica os campos e a ordem das turmas PAP retornadas."""
        seed_turmas()
        cliente = _autenticado()
        url = reverse(
            "obter-turmas-pap",
            kwargs={"ano_letivo": "2026", "codigo_escola": "019660"},
        )
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body), 2)
        self.assertEqual(body[0]["codigo_turma"], "3172713")
        self.assertEqual(
            body[0]["turma_nome"],
            "ID - PAP 2 ANO COLABORATIVO _ALFABETIZACAO",
        )
        self.assertEqual(body[1]["codigo_turma"], "3082743")
        self.assertEqual(
            body[1]["turma_nome"], "LC - PAP COLABORATIVO 3 / 4 E 5 ANO"
        )

    def test_ano_invalido_retorna_400(self) -> None:
        """Verifica que ano_letivo não numérico retorna 400."""
        cliente = _autenticado()
        url = reverse(
            "obter-turmas-pap",
            kwargs={"ano_letivo": "abc", "codigo_escola": "019660"},
        )
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, 400)


class EP03VerificarAlunosTurmaProgramaPapTestCase(TestCase):
    """Valida o endpoint de verificação de alunos em turma PAP."""

    def test_retorna_alunos_validos(self) -> None:
        """Verifica os alunos PAP retornados para os códigos informados."""
        seed_matriculas()
        cliente = _autenticado()
        url = reverse(
            "verificar-se-alunos-sao-turma-programa-pap",
            kwargs={"ano_letivo": "2026"},
        )
        resp = cliente.get(url, {"codigos_alunos": ["6730137"]})
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["codigo_aluno"], 6730137)
        self.assertEqual(body[0]["codigo_componente"], 1770)

    def test_codigos_alunos_invalido_retorna_400(self) -> None:
        """Verifica que codigos_alunos com valor não numérico retorna 400."""
        cliente = _autenticado()
        url = reverse(
            "verificar-se-alunos-sao-turma-programa-pap",
            kwargs={"ano_letivo": "2026"},
        )
        resp = cliente.get(url, {"codigos_alunos": ["abc"]})
        self.assertEqual(resp.status_code, 400)


class EP04AlunosPapAnoCorrenteTestCase(TestCase):
    """Valida o endpoint de alunos PAP do ano corrente."""

    def test_retorna_alunos_pap(self) -> None:
        """Verifica os alunos PAP retornados para o ano corrente mockado."""
        seed_matriculas()
        cliente = _autenticado()
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2026, 5, 1, tzinfo=UTC),
        ):
            url = reverse("obter-alunos-pap-ano-corrente")
            resp = cliente.get(url)
        self.assertEqual(resp.status_code, 200)
        body = _body_json(resp)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["ano_letivo"], 2026)
        self.assertEqual(body[0]["componente_curricular_id"], 1770)


class EP05AlunosPapPorAnoLetivoTestCase(TestCase):
    """Valida o endpoint de alunos PAP por ano letivo."""

    def test_retorna_alunos_do_ano(self) -> None:
        """Verifica os alunos PAP retornados para o ano encerrado."""
        seed_matriculas()
        cliente = _autenticado()
        url = reverse(
            "obter-alunos-pap-por-ano-letivo",
            kwargs={"ano_letivo": "2026"},
        )
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2030, 1, 1, tzinfo=UTC),
        ):
            resp = cliente.get(url)
            body = _body_json(resp)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["codigo_aluno"], 6730137)

    def test_ano_corrente_retorna_array_vazio(self) -> None:
        """Verifica que o ano corrente retorna array vazio."""
        seed_matriculas()
        cliente = _autenticado()
        url = reverse(
            "obter-alunos-pap-por-ano-letivo",
            kwargs={"ano_letivo": "2026"},
        )
        with patch(
            "apps.programas.services.timezone.now",
            return_value=datetime(2026, 5, 1, tzinfo=UTC),
        ):
            resp = cliente.get(url)
            body = _body_json(resp)
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(body, [])


class EP06ComponentesTurmasProgramaAlunoTestCase(TestCase):
    """Valida o endpoint de componentes das turmas de programa do aluno."""

    def test_retorna_componentes(self) -> None:
        """Verifica os componentes das turmas de programa do aluno."""
        seed_matriculas()
        cliente = _autenticado()
        url = reverse(
            "obter-componentes-curriculares-turmas-programa-aluno",
            kwargs={"codigo_aluno": "6730137", "ano_letivo": "2026"},
        )
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body), 1)
        self.assertEqual(body[0]["codigo_aluno"], "6730137")
        self.assertEqual(body[0]["codigo_componente_curricular"], 1770)
        self.assertEqual(
            body[0]["nome_componente_curricular"], "PAP PROJETO COLABORATIVO"
        )


class EP07DadosSrmPaeeColaborativoTestCase(TestCase):
    """Valida o endpoint de dados SRM/PAEE colaborativo do aluno."""

    def test_retorna_dados_srm(self) -> None:
        """Verifica os campos retornados para o aluno com matrícula SRM."""
        seed_matriculas()
        cliente = _autenticado()
        url = reverse(
            "obter-dados-srm-paee-colaborativo",
            kwargs={"codigo_aluno": "5285836"},
        )
        resp = cliente.get(url)
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(len(body), 1)
        item = body[0]
        self.assertEqual(item["codigo_turma"], 3105288)
        self.assertEqual(item["codigo_escola"], "092959")
        self.assertEqual(item["turno"], "Tarde")
        self.assertEqual(item["situacao_matricula"], "1")


class EP08TurmasProgramaTestCase(TestCase):
    """Valida o endpoint que filtra códigos de turma de programa."""

    def test_retorna_codigos_existentes(self) -> None:
        """Verifica que apenas códigos existentes são devolvidos."""
        seed_turmas()
        cliente = _autenticado()
        url = reverse("obter-turmas-programa")
        resp = cliente.post(
            url, ["3082743", "3105288", "9999999"], format="json"
        )
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(sorted(body), ["3082743", "3105288"])

    def test_lista_vazia(self) -> None:
        """Verifica que lista vazia no corpo gera resposta vazia."""
        cliente = _autenticado()
        url = reverse("obter-turmas-programa")
        resp = cliente.post(url, [], format="json")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.json(), [])
