#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Configuration helper tests."""

__updated__ = "2025-12-15 20:42:33"

from skelv2.config import get_config, str_to_bool


def test_str_to_bool_variants():
    assert str_to_bool("true") is True
    assert str_to_bool("False", default=True) is False
    assert str_to_bool(None, default=False) is False


def test_get_config_defaults(monkeypatch):
    monkeypatch.delenv("SERVICE_ENV", raising=False)
    monkeypatch.delenv("APP_TYPE", raising=False)
    monkeypatch.delenv("FLASK_DEBUG", raising=False)
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    config = get_config()
    assert config["SERVICE_ENV"] == "local"
    assert config["APP_TYPE"] == "none"
    assert config["FLASK_DEBUG"] is None
    assert config["LOG_LEVEL"] == "DEBUG"


def test_get_config_flask_debug_override(monkeypatch):
    monkeypatch.setenv("SERVICE_ENV", "prod")
    monkeypatch.setenv("LOG_LEVEL", "info")
    monkeypatch.setenv("FLASK_DEBUG", "true")
    config = get_config()
    assert config["LOG_LEVEL"] == "info"
    assert config["FLASK_DEBUG"] == "true"
