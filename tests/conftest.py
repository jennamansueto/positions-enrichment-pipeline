"""Shared test fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def config_dir() -> Path:
    """Return the path to the config directory."""
    return Path("config")


@pytest.fixture
def domains_dir(config_dir: Path) -> Path:
    return config_dir / "domains"


@pytest.fixture
def mappings_dir(config_dir: Path) -> Path:
    return config_dir / "mappings"


@pytest.fixture
def tmp_warehouse(tmp_path: Path) -> Path:
    """Temporary warehouse directory for test output."""
    wh = tmp_path / "warehouse"
    wh.mkdir()
    return wh
