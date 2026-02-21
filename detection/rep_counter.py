"""
Rep counter — pure state machine, no UI or camera dependencies.

The counter tracks UP / DOWN transitions using the angle produced by
PoseDetector and the thresholds defined in an Exercise object.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from core.exercises import Exercise


@dataclass
class RepCounter:
    """
    Counts repetitions for a given exercise using a two-state machine.

    States:
        UP   — starting / top position (angle > up_min)
        DOWN — bottom position         (angle < down_max)

    A rep is counted when the state transitions DOWN → UP.

    Attributes:
        exercise: The Exercise this counter is tracking.
        reps:     Number of completed repetitions.
        state:    Current state string ("UP" | "DOWN").
    """
    exercise: Exercise
    reps:     int   = field(default=0,    init=False)
    state:    str   = field(default="UP", init=False)

    def update(self, angle: float) -> bool:
        """
        Feed the current joint angle and update the state machine.

        Returns:
            True if a new rep was just completed, False otherwise.
        """
        if angle < self.exercise.down_max and self.state == "UP":
            self.state = "DOWN"

        if angle > self.exercise.up_min and self.state == "DOWN":
            self.state = "UP"
            self.reps += 1
            return True

        return False

    def reset(self) -> None:
        """Reset rep count and state to initial values."""
        self.reps  = 0
        self.state = "UP"
