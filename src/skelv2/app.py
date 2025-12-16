#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903

"""Application entry point dispatcher."""

__updated__ = "2025-12-16 13:04:33"

import logging
import sys

from api import run_api_app
from config import get_config
from worker import run_worker_app
from stdoutlog import init_logging


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
        init_logging(config)
        logging.error(
            "Invalid APP_TYPE %r. Use 'api' or 'worker'. Check your environment or .env file.",
            app_type,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
