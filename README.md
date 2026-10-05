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

Os recursos transversais de observabilidade são fornecidos pelo
**SME Sidecar SDK v1.0.0**.

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


Hierarquia (espelha o MS-ETL):
`TipoPrograma`
         └── `TurmaPrograma`
                 ├── `TurmaProgramaComponenteCurricular`
                 └── `MatriculaTurmaPrograma`
     `ComponenteCurricularPrograma` — configuração que substitui
         constantes hardcoded do Pedagogico-API legado.
     `MatriculaTurmaProgramaHistorico` — lida de
         v_historico_matricula_cotic pelo ETL.

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

**SME Sidecar SDK**

| Variável | Padrão | Descrição |
|---|---|---|
| `SME_SDK_ENABLED` | `true` | Ativa o runtime do SDK |
| `SME_SERVICE_NAME` | `programasedu-ms` | Nome do serviço nos logs e traces |
| `SME_SERVICE_VERSION` | `0.1.0` | Versão publicada na telemetria |
| `SME_ENVIRONMENT` | `local` | Ambiente de execução |
| `SME_LOG_LEVEL` | `INFO` | Nível mínimo dos logs |
| `SME_LOG_FORMAT` | `json` | Formato `json` ou `console` |
| `SME_CORRELATION_ID_HEADER` | `X-Request-ID` | Header de correlação |
| `SME_OTEL_ENABLED` | `false` | Ativa tracing OpenTelemetry |
| `SME_OTEL_EXPORTER_OTLP_ENDPOINT` | `http://otel-collector:4317` | URL OTLP gRPC do collector ou Elastic APM |
| `SME_OTEL_EXPORTER_OTLP_HEADERS` | — | Headers do exporter em `chave=valor` |
| `SME_OTEL_EXPORTER_OTLP_INSECURE` | `true` | Desabilita TLS no transporte OTLP |
| `SME_BROKER_URL` | RabbitMQ local | URL AMQP para transporte opcional de logs |
| `SME_LOG_QUEUE` | — | Fila RabbitMQ que ativa o provider de logs |

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

O SME Sidecar SDK não altera o contrato de autenticação. A API Key continua
sendo validada pelo microsserviço e usada pelo Transition Gateway nas
chamadas entre serviços.

---

## Observabilidade

### Formato dos logs

Os logs são emitidos em JSON estruturado. Cada registro inclui os campos
de contexto aplicáveis:

| Campo         | Descrição                                               |
|---------------|---------------------------------------------------------|
| `timestamp`   | Data e hora do evento                                   |
| `level`       | Nível do log                                             |
| `logger`      | Módulo que gerou o log                                  |
| `event`       | Nome do evento estruturado                              |
| `service`     | Nome do serviço (`programasedu-ms`)                    |
| `environment` | Ambiente de execução                                  |
| `request_id`  | Identificador propagado via `X-Request-ID`              |
| `span_id`     | Identificador da operação atual, quando houver trace   |
| `trace_id`    | Identificador do trace, quando houver tracing habilitado |

O `ObservabilityMiddleware` do SDK emite o evento
`http_request_completed` com método, caminho, status e duração da
requisição, além de reutilizar ou gerar o `X-Request-ID` e devolvê-lo na
resposta.

### Pipeline de logs

```text
Aplicação
   │
   ├── stdout (sempre)
   │     JSON estruturado lido pelo runtime do container
   │
   └── RabbitMQ (quando SME_LOG_QUEUE está configurada)
         │
         └── Consumer (Logstash)
               │
               └── Elasticsearch → Kibana (Logs)
```

Para enviar logs ao Kibana via RabbitMQ, configure `SME_BROKER_URL` e
`SME_LOG_QUEUE`. O consumer da infraestrutura deve ler essa fila e indexar
os eventos no Elasticsearch. O `stdout` permanece como saída principal.

### Rastreamento distribuído

Quando `SME_OTEL_ENABLED=true`, o SDK instrumenta o Django e continua o
contexto `traceparent` recebido do Transition Gateway. Os spans são enviados
por OTLP ao Elastic APM ou a um OpenTelemetry Collector, permitindo
correlacionar Gateway e MS ProgramasEdu pelo mesmo `trace_id`.

No ambiente local de exemplo, o tracing permanece desabilitado. Habilite-o
somente quando o endpoint OTLP estiver acessível pelo container.

As opções de timeout, retry e circuit breaker passam a atuar quando o
serviço utiliza os clientes HTTP da SDK. Atualmente o MS ProgramasEdu não
realiza chamadas HTTP de saída.

Não registre API Keys, documentos pessoais, payloads completos ou outros
dados sensíveis nos logs e spans.

---

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/docs/` | Swagger UI interativo |
| `/api/schema/` | Schema OpenAPI 3 |

---

## Documentação (Sphinx)

Gera a documentação HTML a partir dos arquivos em `docs/`:

```bash
docker compose -f docker-compose-dev.yml run --rm programas \
  sphinx-build -b html docs docs/_build
```

O resultado fica em `docs/_build/index.html` (acessível no host via volume).

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
| EP-01 | GET  | `/api/alunos/paee/turma-srm-e-regular/aluno/<codigo_aluno>` |
| EP-02 | GET  | `/api/alunos/turmas-pap/<ano_letivo>/ues/<codigo_escola>` |
| EP-03 | GET  | `/api/alunos/alunos-pap/<ano_letivo>?codigosAlunos=...` |
| EP-04 | GET  | `/api/alunos/pap/ano-corrente` |
| EP-05 | GET  | `/api/alunos/pap/ano-letivo/<ano_letivo>` |
| EP-06 | GET  | `/api/alunos/<codigo_aluno>/turmas-programa/<ano_letivo>/componentes-curriculares` |
| EP-07 | GET  | `/api/alunos/srm-paee/aluno/<codigo_aluno>` |
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
