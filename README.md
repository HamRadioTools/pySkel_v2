# pySkel v2

Skeleton template for a Python >=3.12 microservice (API + worker) with ready-to-wire observability and infra hooks.

## What’s Included

- API + worker entrypoint (`python -m skelv2.app`) controlled by `APP_TYPE` (`api`/`worker`).
- Container-friendly `entrypoint.sh` that runs Gunicorn for API or a Python module for worker; env-driven.
- Health/ready endpoints with optional Redis-backed API-key protection.
- Structured JSON logging, Postgres + Redis wiring, pytest scaffolding.
- Name/version alignment helper (`set_versname.py`) to keep code, env files, and folders consistent.

### Project Layout

- `src/skelv2/` — app package (renameable via `set_versname.py`).
  - `api/` — Flask bootstrap, routes, health checks.
  - `worker/` — worker loop placeholder.
  - `.env` — service-level defaults (used by `dotenv` on local).
- `.env` — outer file for local tooling (e.g., `PYTHONPATH="src/<pkg>"`).
- `entrypoint.sh` — container entrypoint; reads `APP_TYPE`, `APP_MODULE`, `GUNICORN_APP`, `WORKER_TARGET`.
- `pyproject.toml` — source of truth for project `name` and `version`.
- `set_versname.py` — synchronizes names/versions across code and env files.

### Configuration Flow

- Local: `.env` (outer) sets `PYTHONPATH="src/<package>"`; `src/<package>/.env` sets service defaults.
- Runtime config: `src/skelv2/config.py` loads from environment (12-factor). Use env vars in containers/CI.
- Startup:
  - `APP_TYPE=api` → Gunicorn runs `<APP_MODULE>.wsgi:app`.
  - `APP_TYPE=worker` → `python -m <WORKER_TARGET>`.
  - Defaults: `APP_MODULE=<project_name>`, `GUNICORN_APP=<project_name>.wsgi:app`, `WORKER_TARGET=<project_name>.app`.

### Name & version sync with `set_versname.py`

Run after changing `pyproject.toml` name/version to keep everything aligned.

What it does:

- Reads `[project].name` and `[project].version` plus `[tool.poetry].packages[*].include`.
- Updates `pyproject.toml` so project name and include match.
- Rewrites all `__version__` occurrences in `.py` files to the project version.
- Renames `src/<old>` folder to `src/<project_name>` if needed.
- Updates `src/<project_name>/.env`:
  - `SERVICE_NAME` (appends `-service` if missing)
  - `SERVICE_VERSION`
  - `APP_MODULE`, `GUNICORN_APP`, `WORKER_TARGET` (derived from project name)
- Updates outer `.env` `PYTHONPATH="src/<project_name>"`.

Usage:

```bash
python3 set_versname.py
```

## Quickstart

Install dependencies:

```bash
pip install poetry==1.8.3
poetry install
```

Run API:

```bash
export APP_TYPE=api FLASK_PORT=9000
poetry run python -m skelv2.app
```

Run worker:

```bash
export APP_TYPE=worker
poetry run python -m skelv2.app
```

## Docker

Build:

```bash
docker build -f iac/docker/alpine.dockerfile -t skelv2 .
```

Key env vars:

- `APP_TYPE`: `api` or `worker`
- `GUNIPORT`: Gunicorn port (default 9000)
- `APP_MODULE` / `GUNICORN_APP` / `WORKER_TARGET`: override module names if renamed
- `REDIS_*`, `PG_*`: backing services

`entrypoint.sh` chooses the command based on `APP_TYPE` and module vars.

## Health Endpoints

- `/health`: basic liveness, returns `service` and `version`.
- `/ready`: checks config presence, optional Redis/PG status.
- If `REDIS_ENABLED=true` and a Redis client is present, endpoints can be API-key protected (see `util.decorators.require_apikey`).

Seed a key for testing:

```bash
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a "$REDIS_PASSWORD" \
  HSET "apikey:test-key" customer_id "local" tier "dev" disabled "0"

curl -H "X-API-Key: test-key" http://127.0.0.1:9000/health
```

## Logging

Structured JSON to stdout (API and worker). Fields include service, env, file, line, request_id (API), etc., ready for log collectors (Loki/SIEM).

## Tests

```bash
poetry run pytest
```

## Future work

1. Extend easily with new routes/worker tasks.
1. Add new tests as new features are added.
