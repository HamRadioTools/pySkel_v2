#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""TESTS"""

__updated__ = "2025-12-15 20:42:13"

import json
import pytest

from skel.api import create_api_app
from skel.config import get_config


@pytest.fixture
def client():
    config = get_config()
    # Forcing API mode
    config["APP_TYPE"] = "api"
    config["SERVICE_NAME"] = "micro-service"
    config["SERVICE_ENV"] = "local"
    # Deactivting Redis to avoid requiring an external service.
    config["REDIS_ENABLED"] = False
    # Deactivting Postgres to avoid requiring an external service.
    config["PG_ENABLED"] = False

    app = create_api_app(config)
    app.testing = True
    with app.test_client() as client:
        yield client


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.content_type == "application/json"
    data = json.loads(resp.data)
    assert data["status"] == "ok"


def test_ready(client):
    resp = client.get("/ready")
    assert resp.status_code == 200
    data = json.loads(resp.data)
    assert data["status"] == "ready"


def test_root_discovery(client):
    resp = client.get("/")
    assert resp.status_code == 200
    payload = json.loads(resp.data)
    assert payload["service"] == "micro-service"
    assert payload["environment"] == "local"
    rels = {link["rel"] for link in payload["links"]}
    assert {"health", "ready"} <= rels


if __name__ == "__main__":
    pytest.main()
