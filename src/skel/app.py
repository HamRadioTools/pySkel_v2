#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Application entry point dispatcher."""

__updated__ = "2025-12-15 18:00:16"

import logging
import sys

from skel.api import run_api_app
from skel.config import get_config
from skel.worker import run_worker_app


def main() -> None:
    """
    Decide whether to launch the API or worker mode based on APP_TYPE.
    """
    config = get_config()
    app_type = config.get("APP_TYPE", "api")

    if app_type == "api":
        run_api_app(config)
    elif app_type == "worker":
        run_worker_app(config)
    else:
        logging.basicConfig(level=logging.ERROR)
        logging.error(
            "Invalid APP_TYPE %r. Use 'api' or 'worker'. Check your environment or .env file.",
            app_type,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
