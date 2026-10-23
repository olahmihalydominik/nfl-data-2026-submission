from collections import Counter

from nflcombine.cli import TASKS, resolve
from nflcombine.config import Settings, config_hash, load_yaml
from nflcombine.io.schemas import BRONZE_SCHEMAS

SIDES = {"LEFT", "RIGHT", "NONE"}


def test_pipeline_yaml_bronze_tables_have_schemas_and_counts():
    p = load_yaml("pipeline.yaml")
    assert set(p["raw_files"]) == set(BRONZE_SCHEMAS) == set(p["expected_row_counts"])


def test_drill_mapping_well_formed():
    m = load_yaml("drill_mapping.yaml")
    families = set(m["families"])
    drills = m["drills"]
    assert len(drills) == 62  # distinct (drill_type, drill_name) pairs in combine_tracking.csv
    keys = Counter((d["drill_type"], d["drill_name"]) for d in drills)
    assert max(keys.values()) == 1, "duplicate (drill_type, drill_name)"
    for d in drills:
        assert d["family"] in families, d
        assert d["side"] in SIDES, d
        assert d["canonical"].isupper(), d


def test_canonical_drill_has_one_family():
    by_canon: dict[str, set] = {}
    for d in load_yaml("drill_mapping.yaml")["drills"]:
        by_canon.setdefault(d["canonical"], set()).add(d["family"])
    assert all(len(f) == 1 for f in by_canon.values()), by_canon


def test_positions_subgroups_point_to_groups():
    pos = load_yaml("positions.yaml")
    groups = set(pos["position_groups"])
    assert all(s["group"] in groups for s in pos["position_subgroups"].values())


def test_outcome_metrics_well_formed():
    o = load_yaml("outcome_definitions.yaml")
    groups = set(load_yaml("positions.yaml")["position_groups"])
    for name, m in o["metrics"].items():
        assert m["kind"] in {"count", "rate", "ratio", "mean"}, name
        assert set(m["groups"]) <= groups, name
        assert m["shrinkage"] in {"beta_binomial", "normal", "none"}, name
        assert m["strength"] in {"strong", "weak"}, name
        if m["kind"] in {"rate", "ratio"}:
            assert "numerator" in m, name
        if m["kind"] == "mean":
            assert "value" in m, name
        if m["kind"] == "rate":
            assert m["shrinkage"] == "beta_binomial", name


def test_settings_table_names():
    s = Settings(catalog="cat")
    assert s.table("silver", "dim_player") == "`cat`.`silver`.`dim_player`"
    assert s.raw_paths("game_tracking")[0].endswith("game_tracking_2023.csv")
    assert len(config_hash()) == 12


def test_every_cli_task_resolves():
    for task in TASKS:
        assert callable(resolve(task))
