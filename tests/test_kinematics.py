"""Contract tests for nflcombine.features.kinematics (ticket DE-04).

Marked `todo`: run them with `pytest --run-todo` while implementing; remove the marker when they pass.
Edge frames (first/last 5) are excluded from assertions: SG smoothing is less accurate there.
"""

import numpy as np
import pytest

import synthetic as syn
from nflcombine.features.kinematics import (
    KINEMATIC_COLUMNS,
    derive_kinematics,
    flag_bad_frames,
    motion_onset_idx,
)

pytestmark = pytest.mark.todo
INNER = slice(5, -5)


def test_adds_all_columns(kin_cfg):
    out = derive_kinematics(syn.straight_line(), kin_cfg)
    assert list(out.columns[-len(KINEMATIC_COLUMNS) :]) == KINEMATIC_COLUMNS


@pytest.mark.parametrize("heading", [0.0, 90.0, 180.0, 270.0, 45.0])
def test_straight_line(kin_cfg, heading):
    out = derive_kinematics(syn.straight_line(speed=5.0, heading_deg=heading), kin_cfg).iloc[INNER]
    np.testing.assert_allclose(out.speed_yds, 5.0, atol=0.05)
    dh = (out.heading_deg - heading + 180) % 360 - 180
    np.testing.assert_allclose(dh, 0.0, atol=1.0)
    np.testing.assert_allclose(out.accel_tan_yds2, 0.0, atol=0.1)
    assert (out.turn_radius_yd >= 99).all()  # capped at max_turn_radius_yd


@pytest.mark.parametrize("ccw", [True, False])
def test_circle(kin_cfg, ccw):
    out = derive_kinematics(syn.circle(radius=10.0, speed=5.0, ccw=ccw), kin_cfg).iloc[INNER]
    np.testing.assert_allclose(out.speed_yds, 5.0, rtol=0.03)
    np.testing.assert_allclose(out.turn_radius_yd, 10.0, rtol=0.05)
    expected_an = 2.5 if ccw else -2.5  # v²/r, + = turning left
    np.testing.assert_allclose(out.accel_norm_yds2, expected_an, rtol=0.08)


def test_accel_sign(kin_cfg):
    out = derive_kinematics(syn.accelerate_then_brake(a=4.0), kin_cfg)
    np.testing.assert_allclose(out.accel_tan_yds2.iloc[5:15], 4.0, atol=0.4)
    np.testing.assert_allclose(out.accel_tan_yds2.iloc[25:35], -4.0, atol=0.4)


def test_cumulative_distance(kin_cfg):
    out = derive_kinematics(syn.straight_line(speed=5.0, seconds=4.0), kin_cfg)
    assert out.cum_dist_yd.iloc[0] == pytest.approx(0.0)
    assert out.cum_dist_yd.iloc[-1] == pytest.approx(5.0 * 3.9, rel=0.02)


def test_teleport_flagged_and_interpolated(kin_cfg):
    track = syn.with_teleport(syn.straight_line(speed=5.0), idx=20, jump_yd=5.0)
    bad = flag_bad_frames(track.x.to_numpy(), track.y.to_numpy(), kin_cfg)
    assert bad[20]
    out = derive_kinematics(track, kin_cfg)
    assert out.is_interpolated.iloc[20]
    assert abs(out.speed_yds.iloc[20] - 5.0) < 0.3


def test_heading_null_when_still(kin_cfg):
    track = syn.straight_line(speed=0.0)
    out = derive_kinematics(track, kin_cfg)
    assert out.heading_deg.isna().all()


def test_motion_onset():
    speed = np.array([0.1, 0.2, 0.3, 0.6, 0.7, 0.9, 2.0, 3.0])
    assert motion_onset_idx(speed, threshold=0.5, consecutive=3) == 2
    assert motion_onset_idx(np.zeros(10), threshold=0.5, consecutive=3) is None
