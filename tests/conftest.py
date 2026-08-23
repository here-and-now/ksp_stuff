"""Pytest collection. unittest.TestCase files still run as-is.

New tests: plain functions + assert in this package. Do not add
unittest.TestCase to a new file. Runner is ``python -m pytest``.
"""

from __future__ import annotations

import pytest


def pytest_report_header(config: pytest.Config) -> str:
    return "kspstuff: pytest collects unittest.TestCase and native tests"
