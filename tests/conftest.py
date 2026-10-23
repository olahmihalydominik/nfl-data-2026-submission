import os
from pathlib import Path

import pytest

from nflcombine.config import load_yaml


def pytest_addoption(parser):
    parser.addoption("--run-todo", action="store_true", help="run contract tests for unimplemented code")


def raw_dir() -> Path | None:
    p = os.environ.get("NFL_RAW_DIR")
    return Path(p) if p and Path(p).is_dir() else None


def pytest_collection_modifyitems(config, items):
    skip_todo = pytest.mark.skip(reason="todo: pass --run-todo once implemented")
    skip_data = pytest.mark.skip(reason="data: set NFL_RAW_DIR to the folder with the Kaggle CSVs")
    for item in items:
        if "todo" in item.keywords and not config.getoption("--run-todo"):
            item.add_marker(skip_todo)
        if "data" in item.keywords and raw_dir() is None:
            item.add_marker(skip_data)


@pytest.fixture(scope="session")
def raw() -> Path:
    return raw_dir()


@pytest.fixture(scope="session")
def kin_cfg() -> dict:
    return load_yaml("pipeline.yaml")["kinematics"]
