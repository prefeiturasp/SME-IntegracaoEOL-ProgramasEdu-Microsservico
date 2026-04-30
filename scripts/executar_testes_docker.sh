#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

docker compose -f ../docker-compose-dev.yml build programas

docker compose -f ../docker-compose-dev.yml run --rm programas \
  python -m coverage run --source=apps manage.py test --no-input \
  --settings=config.settings_test

docker compose -f ../docker-compose-dev.yml run --rm programas \
  python -m coverage report --show-missing --fail-under=80