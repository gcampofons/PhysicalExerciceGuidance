"""
Abstract base class for pose detector backends.

Any new backend must implement detect() and optionally close().
The context-manager protocol is handled here so subclasses don't repeat it.
"""
from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np
from detection.keypoint import Keypoint


class BaseDetector(ABC):
    """Common interface for all pose detection backends."""

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
