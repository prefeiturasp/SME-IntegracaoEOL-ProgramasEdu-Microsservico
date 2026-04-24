"""Dados mock compartilhados pelos endpoints do microsservico de Programas.

Os shapes abaixo espelham os responses reais do EOL legado para os endpoints
que serão substituídos pelo domínio `programas` (ver CLAUDE.md).
"""

# ---------------------------------------------------------------------------
# EP-01 — GET /paee/turma-srm-e-regular/aluno/{codigoAluno}
# ---------------------------------------------------------------------------
TURMA_SRM_E_REGULAR_DO_ALUNO_MOCK = {
    "codigoAluno": 5594897,
    "tipoTurno": 1,
    "anoLetivo": 2026,
    "nomeAluno": "MIKAELLY VITORIA BARBOSA BASILIO DOS SANTOS",
    "nomeSocialAluno": None,
    "codigoSituacaoMatricula": 1,
    "situacaoMatricula": "Ativo",
    "dataSituacao": "2025-11-03T17:47:41.827Z",
    "dataNascimento": "2013-04-12T00:00:00Z",
    "numeroAlunoChamada": "000",
    "codigoTurma": 3030126,
    "nomeResponsavel": "NATALIA BARBOSA BULHOES",
    "tipoResponsavel": "1",
    "celularResponsavel": "11983115314",
    "dataAtualizacaoContato": "2024-02-05T20:16:39.513Z",
    "codigoTipoTurma": 1,
    "turmaNome": "9C",
    "etapaEnsino": None,
    "cicloEnsino": None,
    "descEtapaEnsino": None,
    "descCicloEnsino": None,
    "dataAtualizacaoTabela": "0001-01-01T00:00:00",
}

# ---------------------------------------------------------------------------
# EP-02 — GET /turmas-pap/{anoLetivo}/ues/{codigoEscola}
# ---------------------------------------------------------------------------
TURMAS_PAP_MOCK = [
    {"codigoTurma": "3172713", "turmaNome": "ID - PAP 2 ANO COLABORATIVO _ALFABETIZACAO"},
    {"codigoTurma": "3172715", "turmaNome": "IE - PAP 2 ANO COLABORATIVO _ALFABETIZACAO"},
    {"codigoTurma": "3172717", "turmaNome": "IF - PAP 2 ANO COLABORATIVO _ALFABETIZACAO"},
    {"codigoTurma": "3172718", "turmaNome": "IG - PAP 2 ANO COLABORATIVO _ALFABETIZACAO"},
    {"codigoTurma": "3172721", "turmaNome": "IH - PAP 2 ANO COLABORATIVO _ALFABETIZACAO"},
]

# ---------------------------------------------------------------------------
# EP-03 — GET /alunos-pap/{anoLetivo} (query filtrando por lista de alunos)
# ---------------------------------------------------------------------------
ALUNOS_PAP_MOCK = [
    {
        "codigoAluno": 6730137,
        "codigoTurma": 3082743,
        "codigoComponente": 1770,
        "descricao": "PAP PROJETO COLABORATIVO",
    },
    {
        "codigoAluno": 6730137,
        "codigoTurma": 3116156,
        "codigoComponente": 1322,
        "descricao": "PAP - RECUPERACAO DE APRENDIZAGENS",
    },
]

# ---------------------------------------------------------------------------
# EP-04 / EP-05 — /pap/ano-corrente e /pap/ano-letivo/{anoLetivo}
# Mesmo shape (AlunoTurmaPapDto).
# ---------------------------------------------------------------------------
ALUNOS_PAP_ANO_LETIVO_MOCK = [
    {
        "anoLetivo": 2026,
        "codigoTurma": 3094830,
        "codigoUe": "093611",
        "codigoDre": "109200",
        "codigoAluno": 4923405,
        "componenteCurricularId": 1770,
    },
    {
        "anoLetivo": 2026,
        "codigoTurma": 3159519,
        "codigoUe": "019704",
        "codigoDre": "108400",
        "codigoAluno": 4930727,
        "componenteCurricularId": 1770,
    },
]

# ---------------------------------------------------------------------------
# EP-06 — GET /{codigoAluno}/turmas-programa/{anoLetivo}/componentes-curriculares
# ---------------------------------------------------------------------------
COMPONENTES_CURRICULARES_TURMAS_PROGRAMA_ALUNO_MOCK = [
    {
        "codigoAluno": "6711583",
        "codigoTurma": 3082741,
        "codigoComponenteCurricular": 1770,
        "nomeComponenteCurricular": "PAP PROJETO COLABORATIVO",
    },
    {
        "codigoAluno": "6711583",
        "codigoTurma": 3127427,
        "codigoComponenteCurricular": 1769,
        "nomeComponenteCurricular": "POSL COMPARTILHADO",
    },
]

# ---------------------------------------------------------------------------
# EP-07 — GET /srm-paee/aluno/{codigoAluno}
# ---------------------------------------------------------------------------
DADOS_SRM_PAEE_COLABORATIVO_MOCK = [
    {
        "codigoTurma": 3105288,
        "codigoEscola": "092959",
        "turno": "Tarde",
        "componente": "SRM",
        "codigoComponente": 1030,
        "codigoAluno": 5285836,
        "situacaoMatricula": "1",
        "dataMatricula": "2025-12-11T18:25:28.597",
    }
]

# ---------------------------------------------------------------------------
# EP-08 — POST /turmas/turmas-programa
# Retorno é apenas a lista dos códigos que são turmas de programa.
# ---------------------------------------------------------------------------
TURMAS_PROGRAMA_MOCK = ["3092080", "3105288", "3105355"]


# ---------------------------------------------------------------------------
# Erros RFC 7807 padrão
# ---------------------------------------------------------------------------
ERRO_PADRAO = {
    "type": "https://tools.ietf.org/html/rfc7807",
    "title": "Recurso não encontrado",
    "status": 404,
    "detail": "O recurso solicitado não foi encontrado.",
    "instance": "/api/programas/mock",
}

ERRO_400 = {
    "type": "https://tools.ietf.org/html/rfc7807",
    "title": "Requisição inválida",
    "status": 400,
    "detail": "Parâmetros inválidos ou ausentes.",
    "instance": "/api/programas/mock",
}
