"""Entry point for every pipeline task: `nflcombine --task <name>`.

Databricks runs this via python_wheel_task (resources/pipeline.job.yml). Locally it needs pyspark
(`pip install -e ".[spark]"`) or Databricks Connect.
"""

from __future__ import annotations

import argparse
import importlib
import logging
import os

from nflcombine.config import Settings

# task name -> "module:function". Each function has the signature run(spark, settings) -> None.
TASKS: dict[str, str] = {
    "bronze": "nflcombine.pipeline.bronze:run",
    "silver_reference": "nflcombine.pipeline.silver_reference:run",
    "silver_combine": "nflcombine.pipeline.silver_combine:run",
    "silver_game_pp": "nflcombine.pipeline.silver_game:run_player_play",
    "silver_game_frames": "nflcombine.pipeline.silver_game:run_frames",
}


def resolve(task: str):
    module, func = TASKS[task].split(":")
    return getattr(importlib.import_module(module), func)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="nflcombine")
    parser.add_argument("--task", required=True, choices=sorted(TASKS))
    parser.add_argument("--catalog")
    parser.add_argument("--raw-dir")
    args = parser.parse_args(argv)

    # CLI flags override env vars; Settings reads env vars as defaults.
    if args.catalog:
        os.environ["NFL_CATALOG"] = args.catalog
    if args.raw_dir:
        os.environ["NFL_RAW_DIR"] = args.raw_dir
    settings = Settings()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    logging.getLogger(__name__).info("task=%s catalog=%s", args.task, settings.catalog)

    from pyspark.sql import SparkSession

    spark = SparkSession.builder.getOrCreate()
    resolve(args.task)(spark, settings)


if __name__ == "__main__":
    main()
