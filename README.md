# nfl-data-2026-submission

NFL Big Data Bowl 2027: linking 10 Hz combine tracking to later NFL performance.
Pipeline: Databricks (Unity Catalog + Delta) medallion layers bronze → silver → gold, built by one Asset Bundle job.

## Layout

```
conf/                  pipeline parameters, drill mapping, positions, outcome definitions (all tunables live here)
src/nflcombine/
  config.py            Settings + YAML loading
  io/schemas.py        explicit bronze schemas
  io/delta.py          write_table(): the only way tables get written (adds lineage columns)
  features/            kinematics engine shared by combine + game data (pure pandas/numpy)
  pipeline/            one module per job task, each exposes run(spark, settings)
  cli.py               `nflcombine --task <name>` entry point used by the job
resources/             Databricks job definition
tests/                 unit tests (synthetic tracks) + raw-data checks
```

## Local setup (Windows, Python 3.12 to match Databricks)

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
pytest                                  # config + unit tests
$env:NFL_RAW_DIR = "F:\dev\codes\kaggle_nfl\nfl-big-data-bowl-2027\nfl-big-data-bowl-2027"
pytest                                  # now also checks schemas/mapping against the raw CSVs
pytest --run-todo                       # include contract tests for not-yet-implemented code
ruff check . ; ruff format .
```

## Databricks

```powershell
databricks auth login --host <workspace-url>
databricks bundle validate
databricks bundle deploy -t dev
databricks bundle run -t dev pipeline
```

Raw CSVs go to the UC volume `/Volumes/kaggle-nfl/bronze/raw_data/`. They are never committed.
