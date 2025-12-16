#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Database management package"""

__updated__ = "2025-12-15 17:34:44"


from psycopg2 import pool
from typing import Any


minconn = 1  # fail-safe minimum number of connections to keep in the pool
maxconn = 20  # fail-safe maximum number of connections to keep in the pool


def create_pg_pool(config: dict) -> Any:
    """
    Create a psycopg2 SimpleConnectionPool based on configuration.
    """
    return pool.SimpleConnectionPool(
        host=config["PG_HOST"],
        port=config["PG_PORT"],
        user=config["PG_USER"],
        password=config["PG_PASSWORD"],
        database=config["PG_DBNAME"],
        minconn=int(config.get("PG_MIN_CONN", minconn)),
        maxconn=int(config.get("PG_MAX_CONN", maxconn)),
        sslmode=config["PG_SSLMODE"],
    )
