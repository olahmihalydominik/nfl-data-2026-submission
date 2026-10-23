"""Checks our config against the real raw files. Needs NFL_RAW_DIR (skipped otherwise)."""

import csv

import pandas as pd
import pytest

from nflcombine.config import load_yaml
from nflcombine.io.schemas import BRONZE_SCHEMAS, ddl_columns

pytestmark = pytest.mark.data


@pytest.mark.parametrize("table", sorted(BRONZE_SCHEMAS))
def test_schema_matches_csv_header(raw, table):
    expected = [c for c, _ in ddl_columns(BRONZE_SCHEMAS[table])]
    for fname in load_yaml("pipeline.yaml")["raw_files"][table]:
        with open(raw / fname, newline="", encoding="utf-8") as f:
            header = next(csv.reader(f))
        assert header == expected, fname


def test_every_raw_drill_is_mapped(raw):
    df = pd.read_csv(raw / "combine_tracking.csv", usecols=["drill_type", "drill_name"])
    observed = set(map(tuple, df.drop_duplicates().to_numpy()))
    mapped = {(d["drill_type"], d["drill_name"]) for d in load_yaml("drill_mapping.yaml")["drills"]}
    assert observed - mapped == set(), "unmapped drills"
    assert mapped - observed == set(), "mapping lists drills that do not exist"
