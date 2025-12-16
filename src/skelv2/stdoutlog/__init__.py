#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Logging management package"""

__updated__ = "2025-12-15 20:00:43"

# re-export to import as `from skel.log import init_logging`
from .setup import init_logging

__all__ = ["init_logging"]
