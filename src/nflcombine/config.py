"""Settings + YAML config loading.

Resolution order for the config directory:
  1. $NFL_CONF_DIR
  2. `nflcombine/_conf` inside the installed wheel (what Databricks jobs use)
  3. `<repo>/conf` (local editable install)
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Any

import yaml

from nflcombine import __version__

CONF_FILES = ("pipeline.yaml", "drill_mapping.yaml", "positions.yaml", "outcome_definitions.yaml")


def conf_dir() -> Path:
    if env := os.environ.get("NFL_CONF_DIR"):
        return Path(env)
    packaged = Path(__file__).parent / "_conf"
    if packaged.is_dir():
        return packaged
    return Path(__file__).resolve().parents[2] / "conf"


@cache
def load_yaml(name: str) -> dict[str, Any]:
    """Load `conf/<name>` (e.g. "pipeline.yaml"). Cached: config is read-only during a run."""
    with open(conf_dir() / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def config_hash() -> str:
    """Short hash over all config files -> stored as `_config_hash` lineage column."""
    h = hashlib.sha256()
    for name in CONF_FILES:
        h.update((conf_dir() / name).read_bytes())
    return h.hexdigest()[:12]


@dataclass(frozen=True)
class Settings:
    catalog: str = field(default_factory=lambda: os.environ.get("NFL_CATALOG", "bdb2027"))
    raw_dir: str = field(default_factory=lambda: os.environ.get("NFL_RAW_DIR", "/Volumes/bdb2027/bronze/raw"))
    pipeline_version: str = field(default_factory=lambda: os.environ.get("NFL_PIPELINE_VERSION", __version__))

    @property
    def pipeline(self) -> dict[str, Any]:
        return load_yaml("pipeline.yaml")

    def table(self, layer: str, name: str) -> str:
        """Fully qualified UC table name, e.g. settings.table("silver", "dim_player")."""
        schema = self.pipeline["schemas"][layer]
        return f"{self.catalog}.{schema}.{name}"

    def raw_paths(self, bronze_table: str) -> list[str]:
        return [f"{self.raw_dir.rstrip('/')}/{f}" for f in self.pipeline["raw_files"][bronze_table]]
