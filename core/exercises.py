"""
Exercise registry.

Exercise data lives in exercises_data.json — add or edit entries there.
This module loads that file, resolves landmark name strings to their
integer indices, and populates REGISTRY.  No Python edits needed to
add new exercises.
"""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import core.landmarks as _lm


@dataclass(frozen=True)
class FeedbackRule:
    """A single feedback message triggered within an angle range."""
    angle_min: float
    angle_max: float
    message:   str
    color:     str  # hex colour, e.g. "#22c55e"

    def matches(self, angle: float) -> bool:
        return self.angle_min <= angle < self.angle_max


@dataclass(frozen=True)
class Exercise:
    """
    Immutable description of one exercise.

    Attributes:
        id:         Unique integer key used as dict key.
        name:       Display name.
        joint:      Tuple of three landmark indices (A, B, C).
                    The angle is measured at B.
        down_max:   Angle threshold below which the state becomes "DOWN".
        up_min:     Angle threshold above which the state returns to "UP"
                    (and a rep is counted).
        tip:        Short coaching tip shown in the sidebar.
        feedback:   Ordered list of FeedbackRule; first match wins.
    """
    id:       int
    name:     str
    joint:    tuple[int, int, int]
    down_max: float
    up_min:   float
    tip:      str
    feedback: list[FeedbackRule] = field(default_factory=list)

    def get_feedback(self, angle: float) -> FeedbackRule | None:
        for rule in self.feedback:
            if rule.matches(angle):
                return rule
        return None


# ── Registry ──────────────────────────────────────────────────────────────────
REGISTRY: dict[int, Exercise] = {}

_DATA_FILE = Path(__file__).with_name("exercises_data.json")


def _load() -> None:
    """Populate REGISTRY from exercises_data.json."""
    raw: list[dict] = json.loads(_DATA_FILE.read_text(encoding="utf-8"))
    for entry in raw:
        joint = tuple(getattr(_lm, name) for name in entry["joint"])
        feedback = [FeedbackRule(**r) for r in entry["feedback"]]
        REGISTRY[entry["id"]] = Exercise(
            id=entry["id"],
            name=entry["name"],
            joint=joint,          # type: ignore[arg-type]
            down_max=entry["down_max"],
            up_min=entry["up_min"],
            tip=entry["tip"],
            feedback=feedback,
        )


_load()
