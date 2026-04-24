# SME-SGP-MS-Programas

Microsserviço **mock** do domínio Programas para o SGP (Sistema de Gestão Pedagógica) da SME-SP.

Todos os endpoints retornam dados estáticos — sem banco de dados, sem regras de negócio — para uso em testes de integração, desenvolvimento de front-end e validação de contratos de API.

---

## Estrutura dos Apps

| App | Responsabilidade | Endpoints |
|-----|-----------------|-----------|
| `apps.programas` | Programas, atribuições, validações, titulares | EP-01 a EP-08 |

Os modelos ETL que cada app cobre:

- **programas**: `TipoPrograma`, `ComponenteCurricularPrograma`, `TurmaPrograma`, `TurmaProgramaComponenteCurricular`, `MatriculaTurmaPrograma`

---

## Pré-requisitos

- Python 3.12+
- Docker e Docker Compose (para rodar via container)

---

## Rodar localmente (sem Docker)

```bash
# 1. Copiar o .env
cp .env.example .env

# 2. Instalar dependências
pip install -r requirements/local.txt

# 3. Aplicar migrations (SQLite, apenas tabelas internas do Django)
python manage.py migrate

# 4. Rodar o servidor
python manage.py runserver 0.0.0.0:8001
```

Acesse em: http://localhost:8001/api/docs/

---

## Rodar com Docker (desenvolvimento)

```bash
cp .env.example .env
docker compose -f docker-compose-dev.yml up --build
```

Acesse em: http://localhost:8001/api/docs/

---

## Rodar com Docker (produção)

```bash
cp .env.example .env
# Edite .env: DJANGO_DEBUG=0, DJANGO_SECRET_KEY=...
docker compose up --build
```

---

## Autenticação

Todos os endpoints exigem o header `X-API-Key` com o valor configurado em `API_KEY` (`.env`).

Valor padrão em desenvolvimento: `dev-key-default`

```bash
curl -H "X-API-Key: dev-key-default" http://localhost:8001/api/programas/7654321/
```

---

## Documentação da API

| URL | Descrição |
|-----|-----------|
| `/api/docs/` | Swagger UI interativo |
| `/api/schema/` | Schema OpenAPI 3 (JSON/YAML) |

---

## Endpoints implementados

### Programas (EP-01 a EP-23)

| ID | Método | Path |
|----|--------|------|
| EP-01 | GET | `paee/turma-srm-e-regular/aluno/<str:codigoAluno>` |
| EP-02 | GET | `turmas-pap/<str:anoLetivo>/ues/<str:codigoEscola>` |
| EP-03 | GET | `alunos-pap/<str:anoLetivo>` |
| EP-04 | GET | `pap/ano-corrente` |
| EP-05 | GET | `pap/ano-letivo/<str:anoLetivo>` |
| EP-06 | GET | `<str:codigoAluno>/turmas-programa/<str:anoLetivo>/componentes-curriculares` |
| EP-07 | GET | `srm-paee/aluno/<str:codigoAluno>` |
| EP-08 | GET | `turmas/turmas-programa` |

---

## Referências

- Contrato completo: `../swagger_contrato_microsservico.md`
- Projeto ETL de referência: `../SME-SGP-MS-ETL/`