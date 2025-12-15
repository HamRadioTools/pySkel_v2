#!/bin/sh

set -eu

DEFAULT_PORT=9000
PORT="${GUNIPORT:-$DEFAULT_PORT}"
APP_TYPE="${APP_TYPE:-api}"
GUNICORN_APP="${GUNICORN_APP:-skel.wsgi:app}"

poetry_exec() {
    if command -v poetry >/dev/null 2>&1; then
        poetry run "$@"
    else
        "$@"
    fi
}

case "$APP_TYPE" in
    api)
        echo "Starting API via Gunicorn on port $PORT"
        exec poetry_exec gunicorn -b "0.0.0.0:${PORT}" "$GUNICORN_APP" --access-logfile=-
        ;;
    worker)
        echo "Starting worker process"
        exec poetry_exec python -m skel.app
        ;;
    *)
        echo "Unknown APP_TYPE: $APP_TYPE" >&2
        exit 2
        ;;
esac
