"""Unit conversions. Tracking stays in yards/seconds; mass-based quantities go to SI."""

YD_TO_M = 0.9144
LB_TO_KG = 0.45359237
IN_TO_M = 0.0254
IN_TO_CM = 2.54
FORTY_YD_M = 40 * YD_TO_M  # 36.576


def yds_to_ms(v):
    return v * YD_TO_M


def lb_to_kg(w):
    return w * LB_TO_KG


def in_to_m(h):
    return h * IN_TO_M
