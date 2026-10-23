"""Bronze: raw CSV -> Delta, 1:1. Ticket DE-02 (.ignored_plans/DE_TASKS.md).

Rules
- One bronze table per entry in conf/pipeline.yaml `raw_files`; game_tracking unions the 3 season files
  and adds `source_file` (file name only, not the full path).
- Explicit schema from nflcombine.io.schemas.BRONZE_SCHEMAS, never inferSchema.
- No cleaning, no renaming, no filtering. Bronze is a faithful copy.
- After writing, assert row count == conf/pipeline.yaml `expected_row_counts` (raise -> job fails).
- Write through nflcombine.io.delta.write_table.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

    from nflcombine.config import Settings


def read_raw(spark: SparkSession, settings: Settings, table: str) -> DataFrame:
    """Read the raw CSV(s) for `table` with the explicit schema."""
    raise NotImplementedError("DE-02")


def run(spark: SparkSession, settings: Settings) -> None:
    raise NotImplementedError("DE-02")
