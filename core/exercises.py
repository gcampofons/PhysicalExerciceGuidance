"""
Exercise registry.

Each Exercise is a dataclass that carries all the information needed to:
  - identify the three joints for angle measurement
  - decide when a rep has been completed (state machine thresholds)
  - provide real-time form feedback to the user

To add a new exercise, simply append an Exercise to REGISTRY — no other
file needs to be touched.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from core.landmarks import (
    LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST,
    RIGHT_SHOULDER, RIGHT_ELBOW, RIGHT_WRIST,
    LEFT_HIP, LEFT_KNEE, LEFT_ANKLE,
    RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE,
)


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


def _register(ex: Exercise) -> None:
    REGISTRY[ex.id] = ex


_register(Exercise(
    id=0, name="Squat",
    joint=(LEFT_HIP, LEFT_KNEE, LEFT_ANKLE),
    down_max=100, up_min=160,
    tip="Keep your back straight and knees over toes.",
    feedback=[
        FeedbackRule(0,   100, "✓ Good depth!",        "#22c55e"),
        FeedbackRule(100, 160, "↓ Go lower — aim 90°", "#f59e0b"),
        FeedbackRule(160, 180, "↑ Stand up fully",      "#94a3b8"),
    ],
))

_register(Exercise(
    id=1, name="Bicep Curl",
    joint=(LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST),
    down_max=60, up_min=140,
    tip="Keep your elbow close to your torso.",
    feedback=[
        FeedbackRule(0,   60,  "✓ Good curl!",           "#22c55e"),
        FeedbackRule(60,  140, "↕ Full range of motion",  "#f59e0b"),
        FeedbackRule(140, 180, "✓ Good extension!",       "#22c55e"),
    ],
))

_register(Exercise(
    id=2, name="Push-up",
    joint=(LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST),
    down_max=90, up_min=160,
    tip="Keep your core tight and body straight.",
    feedback=[
        FeedbackRule(0,   90,  "✓ Good depth!",           "#22c55e"),
        FeedbackRule(90,  160, "↓ Lower your chest more", "#f59e0b"),
        FeedbackRule(160, 180, "↑ Push up fully",         "#94a3b8"),
    ],
))

_register(Exercise(
    id=3, name="Lateral Raise",
    joint=(LEFT_HIP, LEFT_SHOULDER, LEFT_ELBOW),
    down_max=40, up_min=80,
    tip="Raise to shoulder height with slight elbow bend.",
    feedback=[
        FeedbackRule(0,   40,  "↑ Raise to shoulder level", "#f59e0b"),
        FeedbackRule(40,  80,  "↕ Keep going",               "#f59e0b"),
        FeedbackRule(80,  180, "✓ Good height!",              "#22c55e"),
    ],
))

_register(Exercise(
    id=4, name="Overhead Press",
    joint=(LEFT_ELBOW, LEFT_SHOULDER, LEFT_HIP),
    down_max=80, up_min=160,
    tip="Press directly overhead. Keep core braced.",
    feedback=[
        FeedbackRule(0,   80,  "↑ Press all the way up!", "#f59e0b"),
        FeedbackRule(80,  160, "↕ Keep pressing",          "#f59e0b"),
        FeedbackRule(160, 180, "✓ Full lockout!",          "#22c55e"),
    ],
))

_register(Exercise(
    id=5, name="Tricep Extension",
    joint=(LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST),
    down_max=70, up_min=155,
    tip="Keep upper arm vertical. Only the forearm should move.",
    feedback=[
        FeedbackRule(0,   70,  "✓ Good stretch!",         "#22c55e"),
        FeedbackRule(70,  155, "↕ Full range of motion",  "#f59e0b"),
        FeedbackRule(155, 180, "✓ Full extension!",       "#22c55e"),
    ],
))

_register(Exercise(
    id=6, name="Front Raise",
    joint=(LEFT_HIP, LEFT_SHOULDER, LEFT_ELBOW),
    down_max=50, up_min=85,
    tip="Raise arm to shoulder height. Avoid using momentum.",
    feedback=[
        FeedbackRule(0,   50,  "↑ Raise to shoulder level", "#f59e0b"),
        FeedbackRule(50,  85,  "↕ Almost there",             "#f59e0b"),
        FeedbackRule(85,  180, "✓ Good height!",             "#22c55e"),
    ],
))

_register(Exercise(
    id=7, name="Lunge",
    joint=(LEFT_HIP, LEFT_KNEE, LEFT_ANKLE),
    down_max=95, up_min=165,
    tip="Step forward so front knee stays above ankle.",
    feedback=[
        FeedbackRule(0,   95,  "✓ Good lunge depth!", "#22c55e"),
        FeedbackRule(95,  165, "↓ Lower your back knee", "#f59e0b"),
        FeedbackRule(165, 180, "↑ Stand up fully",     "#94a3b8"),
    ],
))

_register(Exercise(
    id=8, name="Shoulder Tap",
    joint=(LEFT_SHOULDER, LEFT_ELBOW, LEFT_WRIST),
    down_max=100, up_min=160,
    tip="From plank, tap opposite shoulder. Keep hips level.",
    feedback=[
        FeedbackRule(0,   100, "✓ Arm bent — tap!",       "#22c55e"),
        FeedbackRule(100, 160, "↕ Transition",             "#94a3b8"),
        FeedbackRule(160, 180, "✓ Arm extended — plank!", "#22c55e"),
    ],
))
