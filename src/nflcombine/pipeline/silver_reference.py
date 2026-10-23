"""Silver reference tables. Ticket DE-03. Spec: SILVER_GOLD_PLAN.md §3.1-3.3, §3.7

Tables: silver.dim_player, silver.combine_measurables, silver.drill_catalog, silver.games
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

    from nflcombine.config import Settings


def run(spark: SparkSession, settings: Settings) -> None:
    raise NotImplementedError("DE-03")
