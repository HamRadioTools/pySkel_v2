# pySkel v2

Skeleton template for a Python microservice, v2.0.

This skeleton code provides both an HTTP API (Flask + Gunicorn) and a worker loop starter so it feasible to bootstrap either execution mode quickly.

## Features

- Unified runtime dispatcher (`python -m skel.app`) that launches API or worker mode depending on `APP_TYPE`.
- Docker image + `entrypoint.sh` that read the same env vars inside the container.
- Redis-protected health endpoints (optional; automatically enabled when Redis is configured).
- Structured JSON logging, Postgres/Redis pools, and integration tests ready to extend.

## Quickstart

1. Install dependencies (dev + runtime):

   ```bash
   pip install poetry==1.8.3
   poetry install
   ```

2. Run the API:

   ```bash
   export APP_TYPE=api FLASK_PORT=9000
   poetry run python -m skel.app
   ```

3. Run the worker:

   ```bash
   export APP_TYPE=worker
   poetry run python -m skel.app
   ```

### Health endpoints

When `REDIS_ENABLED=true` and Redis credentials are provided, `/health` and `/ready` require a valid API key stored in Redis (`X-API-Key` header). If Redis is disabled, the endpoints remain open for local testing. This is an intentional design.

Example: seed an API key for quick tests (replace values as needed):

```bash
redis-cli -h $REDIS_HOST -p $REDIS_PORT -a "$REDIS_PASSWORD" \
  HSET "apikey:test-key" customer_id "local" tier "dev" disabled "0"

curl -H "X-API-Key: test-key" http://127.0.0.1:9000/health
```

### Tests

```bash
poetry run pytest
```

The test suite exercises the API routes, the worker heartbeat placeholder and config helpers in this base template. More tests will be required as soon as more funtionality is added to this template.

## Docker Image

Build the container with:

```bash
docker build -f iac/docker/alpine.dockerfile -t skel .
```

Runtime env vars:

- `APP_TYPE`: `api` or `worker` (required; defaults to `api` in the entrypoint).
- `GUNIPORT`: Gunicorn listening port (default 9000).
- `REDIS_*` / `PG_*`: configure backing services if needed.

`entrypoint.sh` runs Gunicorn with `skel.wsgi:app` for API mode, or starts the worker loop for worker mode.

## Logging

Both modes emit structured JSON logs via `JsonStdoutHandler`. The idea is to provide this structured format to engines that can preprocess and ingest this log formats like Loki and a SIEM, respectively.

API example:

```json
{
  "timestamp":"2024-01-15T12:00:00Z",
  "level":"INFO",
  "logger":"skel.api.runtime",
  "message":"GET /health",
  "service":"micro-service",
  "env":"local",
  "file":"/opt/app/src/skel/api/runtime.py",
  "line":35,
  "function":"root",
  "request_id":"e2c6b3a9-...",
  "http_method":"GET",
  "http_path":"/health",
  "remote_ip":"10.0.0.5",
  "redis_status":"ok"
}
```

Worker example:

```json
{
  "timestamp":"2024-01-15T12:05:00Z",
  "level":"INFO",
  "logger":"skel.worker.runtime",
  "message":"Worker heartbeat",
  "service":"worker-service",
  "env":"local",
  "file":"/opt/app/src/skel/worker/runtime.py",
  "line":24,
  "function":"_perform_work"
}
```
