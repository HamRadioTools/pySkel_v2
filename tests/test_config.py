#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Configuration helper tests."""

__updated__ = "2025-12-15 20:42:33"

from skel.config import get_config, str_to_bool


def test_str_to_bool_variants():
    assert str_to_bool("true") is True
    assert str_to_bool("False", default=True) is False
    assert str_to_bool(None, default=False) is False


def test_get_config_defaults(monkeypatch):
    monkeypatch.delenv("SERVICE_ENV", raising=False)
    monkeypatch.delenv("APP_TYPE", raising=False)
    config = get_config()
    assert config["SERVICE_ENV"] == "local"
    assert config["APP_TYPE"] == "none"
