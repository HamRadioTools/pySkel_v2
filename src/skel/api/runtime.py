#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Flask API bootstrap helpers."""

from __future__ import annotations

__updated__ = "2025-12-15 20:21:03"

import logging
import time
from flask import Flask, g, jsonify, url_for

from skel.db import init_datastores
from skel.logging import init_logging
from skel.util.request_id import get_or_create_request_id

from .health import register_health_routes


def create_api_app(config: dict) -> Flask:
    """
    Create the Flask app with logging and datastores initialized.
    """
    init_logging(config)
    stores = init_datastores(config)

    app = Flask(__name__)
    logging.getLogger("werkzeug").disabled = True

    @app.before_request
    def _log_request_start():
        g.request_started_at = time.perf_counter()
        get_or_create_request_id()

    metadata = {
        "service": config.get("SERVICE_NAME"),
        "version": config.get("SERVICE_VERSION"),
        "environment": config.get("SERVICE_ENV"),
    }

    @app.route("/", methods=["GET"])
    def root():
        """
        HATEOAS-style discovery endpoint for automatic clients.
        """
        ##
        ## CODE SHOULD COME HERE
        ##
        discovery = {
            "service": metadata["service"],
            "version": metadata["version"],
            "environment": metadata["environment"],
            "links": [
                {
                    "rel": "health",
                    "href": url_for("health", _external=True),
                    "method": "GET",
                    "description": "Liveness probe",
                },
                {
                    "rel": "ready",
                    "href": url_for("ready", _external=True),
                    "method": "GET",
                    "description": "Readiness probe",
                },
            ],
        }
        return jsonify(discovery)

    register_health_routes(app, config=config, stores=stores)

    return app


def run_api_app(config: dict) -> None:
    """
    Helper that creates and runs the Flask application in API mode.
    """
    app = create_api_app(config)
    app.run(host=config.get("FLASK_HOST"), port=config.get("FLASK_PORT"))
