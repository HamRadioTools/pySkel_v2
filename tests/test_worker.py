#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# pylint: disable=W0102,E0712,C0103,R0903,protected-access

"""Worker runtime tests."""

__updated__ = "2025-12-15 20:43:24"

import logging
import pytest

from skelv2.worker import runtime as worker_runtime


@pytest.fixture
def worker_config():
    return {"SERVICE_NAME": "worker-service"}


def test_perform_work_logs_heartbeat(worker_config, caplog):
    caplog.set_level(logging.INFO, logger="skelv2.worker.runtime")
    worker_runtime._perform_work(worker_config, {})  # noqa: SLF001
    assert "Worker heartbeat" in caplog.text
