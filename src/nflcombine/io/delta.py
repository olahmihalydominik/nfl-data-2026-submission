"""The ONE way to write a table. Every pipeline task goes through `write_table`."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from nflcombine.config import Settings, config_hash

if TYPE_CHECKING:
    from pyspark.sql import DataFrame


def add_lineage(df: DataFrame, settings: Settings) -> DataFrame:
    from pyspark.sql import functions as F

    return (
        df.withColumn("_pipeline_version", F.lit(settings.pipeline_version))
        .withColumn("_built_at", F.lit(datetime.now(UTC)).cast("timestamp"))
        .withColumn("_config_hash", F.lit(config_hash()))
    )


def write_table(
    df: DataFrame,
    settings: Settings,
    layer: str,
    name: str,
    *,
    partition_by: list[str] | None = None,
    cluster_by: list[str] | None = None,
    comment: str | None = None,
) -> str:
    """Full overwrite of `<catalog>.<layer>.<name>` with lineage columns. Returns the table name.

    Use either `partition_by` (only for game_frames by season) or `cluster_by` (liquid clustering), not both.
    """
    if partition_by and cluster_by:
        raise ValueError("choose partition_by OR cluster_by")
    fqn = settings.table(layer, name)
    writer = (
        add_lineage(df, settings).write.format("delta").mode("overwrite").option("overwriteSchema", "true")
    )
    if partition_by:
        writer = writer.partitionBy(*partition_by)
    if cluster_by:
        writer = writer.clusterBy(*cluster_by)
    writer.saveAsTable(fqn)
    if comment:
        df.sparkSession.sql(f"COMMENT ON TABLE {fqn} IS '{comment.replace(chr(39), chr(39) * 2)}'")
    return fqn
