"""
Pure geometry utilities — no UI or ML dependencies.
"""
from __future__ import annotations
import numpy as np


def angle_between(a: list[float], b: list[float], c: list[float]) -> float:
    """
    Return the angle in degrees at vertex B, formed by the triangle A-B-C.

    Args:
        a: [x, y] of point A
        b: [x, y] of point B (vertex)
        c: [x, y] of point C

    Returns:
        Angle in degrees [0, 180].
    """
    va = np.array(a) - np.array(b)
    vc = np.array(c) - np.array(b)
    cos_theta = np.dot(va, vc) / (np.linalg.norm(va) * np.linalg.norm(vc) + 1e-8)
    return float(np.degrees(np.arccos(np.clip(cos_theta, -1.0, 1.0))))


def landmark_xy(landmarks: list, idx: int) -> list[float]:
    """Extract normalised [x, y] from a MediaPipe landmark list."""
    lm = landmarks[idx]
    return [lm.x, lm.y]
