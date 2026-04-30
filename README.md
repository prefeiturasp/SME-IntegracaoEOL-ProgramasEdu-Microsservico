# SME-IntegracaoEOL-ProgramasEdu-Microsservico

Microsserviço de leitura do domínio **Programas Educacionais (PAP/PAEE)** da SME-SP.

Substitui os endpoints legados do `SME-Pedagogico-API-master` que hoje
consultam o EOL/Elastic. Os dados vêm do Postgres `programas_db`,
populado pelo `SME-IntegracaoEOL-MS-ETL`. Este microsserviço opera
exclusivamente em modo **read-only** — todos os models declaram
`Meta.managed = False` (DDL é responsabilidade do MS-ETL).

Consumido pelo **Transition Gateway**, que agrega as respostas deste
microsserviço com os domínios Alunos e Pedagógico antes de devolver ao
cliente final.

---

## Estrutura

```
apps/programas/
├── api/
│   ├── serializers.py    # 7 serializers DRF (camelCase do legado)
│   ├── urls.py           # 8 paths (EP-01 a EP-08)
│   └── views.py          # 8 APIView
├── management/
│   └── commands/
├── tests/
│   ├── helpers.py
│   ├── test_api.py
│   ├── test_models.py
│   └── test_services.py
├── apps.py
├── enums.py              # CategoriaPrograma, SituacaoTurma, SituacaoMatricula
│                         # + SITUACOES_MATRICULA_VALIDAS, SITUACOES_TURMA_ATIVAS
│                         # + CODIGO_COMPONENTE_PAEE_SRM = 1030
├── models.py             # 5 models read-only (managed=False)
└── services.py           # 7 DTOs frozen (dataclass) + funções de query por endpoint
                          # EP-04/EP-05: variante list_ (DRF) + iter_ (streaming)
```

Tabelas lidas em `programas_db`:

| Modelo | Tabela |
|--------|--------|
| `TipoPrograma` | `tipo_programa` |
| `ComponenteCurricularPrograma` | `componente_curricular_programa` |
| `TurmaPrograma` | `turma_programa` |
| `TurmaProgramaComponenteCurricular` | `turma_programa_componente_curricular` |
| `MatriculaTurmaPrograma` | `matricula_turma_programa` |

---

## Variáveis de ambiente

Copie `.env.example` para `.env` e ajuste conforme o ambiente:

| Variável | Padrão | Descrição |
|---|---|---|
| `DJANGO_SECRET_KEY` | _(obrigatória em produção)_ | Chave secreta do Django |
| `DJANGO_DEBUG` | `1` | `1` = debug on, `0` = produção |
| `DJANGO_ALLOWED_HOSTS` | `*` | Hosts permitidos (vírgula separado) |
| `API_KEY` | `dev-key-default` | Chave usada no header de autenticação |
| `API_KEY_HEADER` | `X-API-Key` | Nome do header de autenticação |
| `URL_BANCO_PROGRAMAS` | _(ver abaixo)_ | DSN Postgres do `programas_db` |
| `DB_POOL_SIZE` | `5` | Tamanho do pool de conexões (`dj_db_conn_pool`) |
| `PORT_WEB` | `8001` | Porta do servidor web no Docker |
| `PORT_DEBUGPY` | `5678` | Porta do debugger remoto (debugpy) |
| `NIVEL_LOG` | `INFO` | Nível de log (`DEBUG`, `INFO`, `WARNING`, …) |
| `AMBIENTE_APLICACAO` | `local` | Identificador de ambiente nos logs |

`URL_BANCO_PROGRAMAS` padrão (aponta para o container do MS-ETL):
```
postgresql://postgres:postgres@sme_sgp_ms_etl_postgres:5432/programas_db
```

> O banco usa **connection pooling** via `dj_db_conn_pool` com
> `POOL_SIZE=DB_POOL_SIZE`, `MAX_OVERFLOW=0`, `POOL_RECYCLE=1800s` e
> `PRE_PING=True`.

---

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose
- Cluster Postgres com `programas_db` populado pelo MS-ETL
  (em dev, sobe junto com o `docker-compose-dev.yml` do MS-ETL)

---

## Rodar com Docker (desenvolvimento)

O `docker-compose-dev.yml` deste repositório anexa o container à network
do MS-ETL (`sme-integracaoeol-ms-etl_default`) e aponta `URL_BANCO_PROGRAMAS`
para o container `sme_sgp_ms_etl_postgres`.

Pré-requisito: o `docker-compose-dev.yml` do **MS-ETL** já estar de pé
(o Postgres precisa estar rodando antes deste microsserviço).

```bash
cp .env.example .env
docker compose -f docker-compose-dev.yml up --build
```

Acesse em: <http://localhost:8001/programasedu/api/v1/docs/>

---

## Rodar localmente (sem Docker)

```bash
cp .env.example .env
# Ajuste URL_BANCO_PROGRAMAS para localhost:5432 se necessário

pip install -r requirements/local.txt
python manage.py runserver 0.0.0.0:8001
```

> Não rode `python manage.py migrate` para o banco `programas_db` —
> ele é gerenciado exclusivamente pelo MS-ETL.

---

## Autenticação

Todos os endpoints exigem o header `X-API-Key`:

```bash
curl -H "X-API-Key: dev-key-default" \
  http://localhost:8001/api/pap/ano-corrente
```

> A autenticação cross-service via Transition Gateway (proposta com
> Sidecar) é escopo futuro. Hoje a autenticação é apenas a chave estática
> usada para acesso direto ao Swagger e validação de contrato.

---

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/docs/` | Swagger UI interativo |
| `/api/schema/` | Schema OpenAPI 3 |

---

## Testes

Os testes seguem o padrão do MS-ETL (`django.test.TestCase` +
`coverage`). Execução via Docker:

```bash
./executar_testes_docker.sh
```

Equivalente a:

```bash
docker compose -f docker-compose-dev.yml build programas

docker compose -f docker-compose-dev.yml run --rm programas \
  python -m coverage run --source=apps \
    manage.py test --no-input

docker compose -f docker-compose-dev.yml run --rm programas \
  python -m coverage report --show-missing --fail-under=80
```

Cobertura mínima: **80%**.

Os models do app são `managed=False` em produção (DDL é do MS-ETL).
Em testes, o `config/test_runner.py` (`ProgramasTestRunner`) marca os
models como gerenciáveis antes de criar o banco SQLite em memória, de
forma que os `TestCase` possam fazer `Model.objects.create(...)`
normalmente.

---

## Endpoints

| ID | Método | Path |
|----|--------|------|
| EP-01 | GET  | `/api/alunos/paee/turma-srm-e-regular/aluno/<codigoAluno>` |
| EP-02 | GET  | `/api/alunos/turmas-pap/<anoLetivo>/ues/<codigoEscola>` |
| EP-03 | GET  | `/api/alunos/alunos-pap/<anoLetivo>?codigosAlunos=...` |
| EP-04 | GET  | `/api/alunos/pap/ano-corrente` |
| EP-05 | GET  | `/api/alunos/pap/ano-letivo/<anoLetivo>` |
| EP-06 | GET  | `/api/alunos/<codigoAluno>/turmas-programa/<anoLetivo>/componentes-curriculares` |
| EP-07 | GET  | `/api/alunos/srm-paee/aluno/<codigoAluno>` |
| EP-08 | POST | `/api/turmas/turmas-programa` |

### Observações sobre o contrato

- **EP-01** retorna **shape reduzido** — apenas os campos pertencentes
  ao domínio Programas. Campos como `nomeAluno`, `dataNascimento`,
  `nomeResponsavel`, `etapaEnsino` etc. são responsabilidade dos
  domínios `Alunos` e `Pedagogico` e são agregados pelo Transition
  Gateway antes da resposta final.
- **EP-08** aceita `list[str]` no body, fiel ao contrato legado
  (`IEnumerable<string>`).
- **EP-07** retorna `situacaoMatricula` como string (`"1"`) preservando
  o legado.

---

## Referências

- Endpoints originais: `SME-Pedagogico-API-master` — `AlunoController.cs` e `TurmaController.cs`
  (seção "Endpoints do Pedagogico-API legado a substituir").
- Models de origem: `../SME-IntegracaoEOL-MS-ETL/apps/programas/models.py`.
