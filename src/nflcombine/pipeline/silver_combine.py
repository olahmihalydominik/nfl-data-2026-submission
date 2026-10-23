"""Silver combine tables. Ticket DE-05. Spec: SILVER_GOLD_PLAN.md §3.5-3.6

Tables: silver.combine_attempts, silver.combine_frames
Per-attempt maths runs as pandas via groupBy("event_id").applyInPandas(...) and calls
nflcombine.features.kinematics — no kinematics logic in this module.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

    from nflcombine.config import Settings


def run(spark: SparkSession, settings: Settings) -> None:
    raise NotImplementedError("DE-05")
