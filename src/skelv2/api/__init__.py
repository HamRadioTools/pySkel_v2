#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""API package"""

__updated__ = "2025-12-15 17:27:08"

from .runtime import create_api_app, run_api_app

__all__ = ["create_api_app", "run_api_app"]
