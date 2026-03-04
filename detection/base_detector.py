"""
Abstract base class for the pose detector.

It defines detect() and optional close(), and centralizes context-manager
behavior.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
from detection.keypoint import Keypoint


class BaseDetector(ABC):
    """Common interface for pose detection."""

    @abstractmethod
    def detect(self, bgr_frame: np.ndarray, timestamp_ms: int) -> list[Keypoint] | None:
        """
        Run pose detection on a single BGR frame.

        Returns:
            A list of exactly 33 Keypoints in MediaPipe slot order, or None if
            no person was detected.  Slots that the backend cannot populate are
            filled with Keypoint(0.0, 0.0, 0.0).
        """
        ...

    def close(self) -> None:
        """Release any held resources (override as needed)."""

    def __enter__(self) -> "BaseDetector":
        return self

    def __exit__(self, *_) -> None:
        self.close()
