#!/usr/bin/env bash

docker compose -f docker-compose-dev.yml run --rm programas pre-commit run --all-files