"""Shared kinematics engine — the SAME code for combine attempts and game player-plays.
Ticket DE-04. Spec: SILVER_GOLD_PLAN.md §3.4. Contract tests: tests/test_kinematics.py.

Pure numpy/pandas, no Spark: it runs inside applyInPandas on one entity (attempt or player-play).

Conventions
- Input frames are ordered, 10 Hz, positions in yards.
- Angles use the source convention: 0° = +y, clockwise, [0, 360). So moving +x = 90°.
- accel_tan is SIGNED (+ speeding up, − braking); accel_norm is signed (+ = turning left / counter-clockwise).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Columns added by derive_kinematics, in this order.
KINEMATIC_COLUMNS = [
    "is_bad_frame",
    "is_interpolated",
    "x_s",  # smoothed x
    "y_s",  # smoothed y
    "vx",
    "vy",
    "speed_yds",
    "heading_deg",
    "accel_tan_yds2",
    "accel_norm_yds2",
    "accel_mag_yds2",
    "jerk_yds3",
    "ang_vel_dps",
    "turn_radius_yd",
    "cum_dist_yd",
]


def flag_bad_frames(x: np.ndarray, y: np.ndarray, cfg: dict) -> np.ndarray:
    """Boolean mask of teleport frames: implied speed > cfg['max_speed_yds'] or implied
    |Δv| per frame > cfg['max_accel_yds2']. First frame is never bad."""
    raise NotImplementedError("DE-04")


def interpolate_short_gaps(
    x: np.ndarray, y: np.ndarray, bad: np.ndarray, max_gap: int
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Linearly interpolate runs of bad frames of length <= max_gap.
    Returns (x, y, interpolated_mask). Longer runs are left untouched (caller decides validity)."""
    raise NotImplementedError("DE-04")


def smooth_and_differentiate(x: np.ndarray, y: np.ndarray, cfg: dict) -> dict[str, np.ndarray]:
    """Savitzky–Golay (window cfg['window_frames'], poly cfg['polyorder'], mode='interp').
    Returns dict with x_s, y_s, vx, vy, ax, ay (derivatives from the SG fit, dt = 1/frame_hz)."""
    raise NotImplementedError("DE-04")


def derive_kinematics(track: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Main entry. `track` has columns x, y (ordered, 10 Hz). Returns a copy with KINEMATIC_COLUMNS added.

    `cfg` is conf/pipeline.yaml['kinematics'].
    Entities shorter than window_frames: return KINEMATIC_COLUMNS as NaN (and is_bad_frame False).
    """
    raise NotImplementedError("DE-04")


def bad_frame_fraction(track: pd.DataFrame) -> float:
    """Share of frames flagged bad and NOT interpolated (used for the is_valid decision)."""
    raise NotImplementedError("DE-04")


def motion_onset_idx(speed: np.ndarray, threshold: float, consecutive: int) -> int | None:
    """Index of motion onset: first i where speed[i : i+consecutive] are all > threshold, minus 1
    (floored at 0). None if the entity never moves."""
    raise NotImplementedError("DE-04")
