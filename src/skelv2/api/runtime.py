#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Flask API bootstrap helpers."""

from __future__ import annotations

__updated__ = "2025-12-16 20:03:18"

import logging
import time
from flask import Flask, g, jsonify, url_for

from db import init_datastores
from stdoutlog import init_logging
from util.request_id import get_or_create_request_id

from .health import register_health_routes


def create_api_app(config: dict) -> Flask:
    """
    Create the Flask app with logging and datastores initialized.
    """
    init_logging(config)
    stores = init_datastores(config)

    app = Flask(__name__)
    app.json.sort_keys = False

    # Allow Werkzeug / Gunicorn access logs to flow to our JSON handler
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.disabled = False
    werkzeug_logger.setLevel(logging.INFO)
    werkzeug_logger.propagate = True  # keep stdout logging in every env

    metadata = {
        "service": config.get("SERVICE_NAME"),
        "version": config.get("SERVICE_VERSION"),
        "environment": config.get("SERVICE_ENV"),
    }

    ############################################################################
    #
    # Captureing requests before processing them
    #
    ############################################################################

    @app.before_request
    def _log_request_start():
        g.request_started_at = time.perf_counter()
        get_or_create_request_id()

    ############################################################################
    #
    # Apex endpoint, informational and HATEOAS
    #
    ############################################################################

    @app.route("/", methods=["GET"])
    def root():
        """
        HATEOAS-style discovery endpoint for automatic clients.
        """
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
                #
                # ...
                #
            ],
        }
        return jsonify(discovery)

    ############################################################################
    #
    # CODE SHOULD COME HEREIN THE FORM OF REGISTERED MODULES / FUNCTIONS
    #   |    |    |    |    |    |    |    |    |    |    |    |    |
    #   v    v    v    v    v    v    v    v    v    v    v    v    v
    #
    # Steps:
    # ------
    # 1. Create a module in this package folder
    # 2. Code endpoints and functions
    # 3. Register below the routers
    #
    ############################################################################

    register_health_routes(app, config=config, stores=stores)

    return app


def run_api_app(config: dict) -> None:
    """
    Helper that creates and runs the Flask application in API mode.
    """
    app = create_api_app(config)

    debug_flag = config.get("FLASK_DEBUG")
    if isinstance(debug_flag, str):
        debug_flag = debug_flag.lower() in {"1", "true", "t", "yes", "y"}
    elif debug_flag is None:
        debug_flag = config.get("LOG_LEVEL", "").upper() == "DEBUG"

    app.run(
        host=config.get("FLASK_HOST"),
        port=config.get("FLASK_PORT"),
        debug=bool(debug_flag),
    )
