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

from nflcombine.io.delta import write_table
from nflcombine.io.schemas import BRONZE_SCHEMAS

if TYPE_CHECKING:
    from pyspark.sql import DataFrame, SparkSession

    from nflcombine.config import Settings


def read_raw(spark: SparkSession, settings: Settings, table: str) -> DataFrame:
    """Read the raw CSVs for `table` with the explicit schema."""
    from pyspark.sql import functions as F

    df = (
        spark.read.format("csv")
        .schema(BRONZE_SCHEMAS[table])
        .option("header", "true")
        .option("nullValue", "NA")
        .option("multiLine", "true")
        .option("escape", '"')
        .option("timestampFormat", "yyyy-MM-dd'T'HH:mm:ss.SSS")
        .load(settings.raw_paths(table))
    )
    if table == "game_tracking":
        df = df.withColumn(
            "source_file",
            F.element_at(F.split(F.col("_metadata.file_path"), "/"), -1),
        )
    return df


def run(spark: SparkSession, settings: Settings) -> None:
    from pyspark.sql import functions as F

    for table in settings.pipeline["raw_files"]:
        df = read_raw(spark, settings, table)

        # Acceptance: a wrong timestampFormat parses silently to null, so
        # assert zero null `time` values explicitly instead of trusting the write.
        if "time" in df.columns:
            null_times = df.where(F.col("time").isNull()).count()
            if null_times:
                raise ValueError(
                    f"bronze.{table}: {null_times} null 'time' values (timestamp parse failures)"
                )

        fqn = write_table(df, settings, "bronze", table)

        actual = spark.table(fqn).count()
        expected = settings.pipeline["expected_row_counts"][table]
        if actual != expected:
            raise ValueError(f"bronze.{table}: expected {expected} rows, wrote {actual}")
