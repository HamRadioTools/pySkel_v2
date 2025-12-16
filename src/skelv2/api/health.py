#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""API package"""

__updated__ = "2025-12-16 12:53:52"

from flask import jsonify

from util.decorators import require_apikey


def register_health_routes(app, *, config: dict, stores: dict | None = None):
    """
    Register basic health/ready endpoints.

    - GET /health  -> simple liveness check
    - GET /ready   -> can be extended to check DB, etc.
    """
    service_name = config.get("SERVICE_NAME", "micro-service")
    service_version = config.get("SERVICE_VERSION", "0.1.0")
    redis_enabled = config.get("REDIS_ENABLED", False)
    stores = stores or {}
    redis_client = stores.get("redis")

    def protect(handler):
        if redis_enabled and redis_client:
            return require_apikey(stores)(handler)
        return handler

    @app.route("/health", methods=["GET"])
    # @protect
    def health():
        return jsonify(
            {
                "status": "ok",
                "service": service_name,
                "version": service_version,
            }
        )

    @app.route("/ready", methods=["GET"])
    # @protect
    def ready():
        pg_status = {"enabled": bool(config.get("PG_ENABLED", False)), "status": "disabled"}
        if pg_status["enabled"]:
            pool = stores.get("pg_pool")
            conn = None
            if pool is None:
                pg_status["status"] = "missing_pool"
            else:
                try:
                    conn = pool.getconn()
                    with conn.cursor() as cursor:
                        cursor.execute("SELECT 1;")
                        cursor.fetchone()
                    pg_status["status"] = "ok"
                except Exception as exc:  # pylint: disable=broad-except
                    pg_status["status"] = "error"
                    pg_status["error"] = str(exc)
                finally:
                    if conn:
                        pool.putconn(conn)

        redis_status = {
            "enabled": bool(config.get("REDIS_ENABLED", False)),
            "status": "disabled",
        }
        if redis_status["enabled"]:
            redis_client = stores.get("redis")
            if redis_client is None:
                redis_status["status"] = "missing_client"
            else:
                try:
                    redis_status["status"] = "ok" if redis_client.ping() else "error"
                except Exception as exc:  # pylint: disable=broad-except
                    redis_status["status"] = "error"
                    redis_status["error"] = str(exc)

        required_keys = ("SERVICE_NAME", "SERVICE_VERSION", "SERVICE_ENV")
        missing_keys = [key for key in required_keys if not config.get(key)]
        config_status = {
            "status": "ok" if not missing_keys else "missing",
            "missing": missing_keys,
        }

        overall_status = "ready"
        unhealthy = config_status["status"] != "ok" or any(
            status.get("status") not in ("ok", "disabled") for status in (pg_status, redis_status)
        )
        if unhealthy:
            overall_status = "degraded"

        return jsonify(
            {
                "status": overall_status,
                "database": pg_status,
                "cache": redis_status,
                "config": config_status,
            }
        )
