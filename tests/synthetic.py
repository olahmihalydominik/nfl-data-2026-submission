"""Synthetic 10 Hz tracks with analytically known kinematics, for testing the kinematics engine."""

import numpy as np
import pandas as pd

HZ = 10
DT = 1 / HZ


def _df(x, y):
    t = np.arange(len(x)) * DT
    return pd.DataFrame({"t": t, "x": x, "y": y})


def straight_line(speed=5.0, heading_deg=90.0, seconds=4.0):
    """Constant speed along a compass heading (90° = +x)."""
    n = int(seconds * HZ)
    t = np.arange(n) * DT
    h = np.radians(heading_deg)
    return _df(10 + speed * t * np.sin(h), 20 + speed * t * np.cos(h))


def circle(radius=10.0, speed=5.0, seconds=6.0, ccw=True):
    """Constant-speed circle. accel_norm = ±speed²/radius (+ for counter-clockwise = turning left)."""
    n = int(seconds * HZ)
    t = np.arange(n) * DT
    w = speed / radius * (1 if ccw else -1)
    return _df(50 + radius * np.cos(w * t), 25 + radius * np.sin(w * t))


def accelerate_then_brake(a=4.0, t_acc=2.0, t_brake=2.0):
    """Straight +x: constant +a for t_acc, then constant −a for t_brake (ends at rest)."""
    t1 = np.arange(int(t_acc * HZ)) * DT
    x1 = 0.5 * a * t1**2
    v_peak, x_peak = a * t_acc, 0.5 * a * t_acc**2
    t2 = np.arange(1, int(t_brake * HZ) + 1) * DT
    x2 = x_peak + v_peak * t2 - 0.5 * a * t2**2
    x = np.concatenate([x1, x2])
    return _df(x, np.full_like(x, 20.0))


def cut_90(speed=6.0, seconds_each=2.0):
    """Run +x then turn sharply to +y (a left 90° cut) at constant nominal speed."""
    n = int(seconds_each * HZ)
    leg = np.arange(1, n + 1) * DT * speed
    x = np.concatenate([leg, np.full(n, leg[-1])])
    y = np.concatenate([np.zeros(n), leg])
    return _df(x, y)


def with_teleport(track: pd.DataFrame, idx: int, jump_yd=5.0):
    """Corrupt one frame with a positional spike."""
    out = track.copy()
    out.loc[idx, "x"] += jump_yd
    return out
