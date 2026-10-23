"""Silver game tables. Spec: SILVER_GOLD_PLAN.md §3.8-3.11

run_player_play (DE-06): silver.player_play, silver.play_events, silver.play_timeline
run_frames      (DE-07): silver.game_frames, silver.game_player_play_index
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pyspark.sql import SparkSession

    from nflcombine.config import Settings


def run_player_play(spark: SparkSession, settings: Settings) -> None:
    raise NotImplementedError("DE-06")


def run_frames(spark: SparkSession, settings: Settings) -> None:
    raise NotImplementedError("DE-07")
