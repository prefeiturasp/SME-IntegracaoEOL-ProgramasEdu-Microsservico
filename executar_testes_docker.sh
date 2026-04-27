#!/usr/bin/env bash
# Executa os testes do microsserviço Programas via Docker, espelhando o
# fluxo usado pelo SME-IntegracaoEOL-MS-ETL: build, coverage run, report.
#
# Cobertura mínima exigida: 80% (regra institucional).
set -euo pipefail

cd "$(dirname "$0")"

docker compose -f docker-compose-dev.yml build programas

docker compose -f docker-compose-dev.yml run --rm programas \
  python -m coverage run --source=apps \
    manage.py test --no-input --settings=config.settings_test

docker compose -f docker-compose-dev.yml run --rm programas \
  python -m coverage report --show-missing --fail-under=80
