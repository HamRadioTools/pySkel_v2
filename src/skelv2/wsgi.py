#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Gunicorn entry point for the API."""

from __future__ import annotations

__updated__ = "2025-12-16 03:04:23"

from api import create_api_app
from config import get_config

app = create_api_app(get_config())
