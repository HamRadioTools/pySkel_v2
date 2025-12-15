#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""API package"""

__updated__ = "2025-12-15 17:28:19"

from flask import jsonify

from skel.util.decorators import require_apikey


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
    @protect
    def health():
        return jsonify(
            {
                "status": "ok",
                "service": service_name,
                "version": service_version,
            }
        )

    @app.route("/ready", methods=["GET"])
    @protect
    def ready():
        # In future we can add checks: DB connectivity, config sanity, etc.
        return jsonify({"status": "ready"})
