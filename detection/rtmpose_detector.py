"""
RTMPose pose detection backend via ``rtmlib``.

RTMPose is a real-time multi-pose estimator from OpenMMLab that achieves
higher accuracy than YOLOv8-pose while remaining fast enough for live use.

Supports three speed/accuracy presets (``variant`` parameter):
  - ``"rtmpose_s"``  — lightweight, fastest (default)
  - ``"rtmpose_m"``  — balanced, good accuracy
  - ``"rtmpose_x"``  — performance, best accuracy (heaviest)

Models (ONNX) are **downloaded automatically** by rtmlib on the first run
and cached in ~/.cache/rtmlib/.

Requires: pip install rtmlib
(onnxruntime is installed as a dependency automatically.)
"""
from __future__ import annotations

import numpy as np

from detection.base_detector import BaseDetector
from detection.keypoint import Keypoint

# ── Variant → rtmlib Body mode ────────────────────────────────────────────────
# rtmlib.Body accepts mode='lightweight' | 'balanced' | 'performance'
# and downloads the right ONNX models automatically.
_VARIANT_TO_MODE: dict[str, str] = {
    "rtmpose_s": "lightweight",
    "rtmpose_m": "balanced",
    "rtmpose_x": "performance",
}

# ── COCO-17 → MediaPipe-33 mapping ────────────────────────────────────────────
_COCO_TO_MP: dict[int, int] = {
    0:  0,   # nose
    1:  2,   # left_eye
    2:  5,   # right_eye
    3:  7,   # left_ear
    4:  8,   # right_ear
    5:  11,  # left_shoulder
    6:  12,  # right_shoulder
    7:  13,  # left_elbow
    8:  14,  # right_elbow
    9:  15,  # left_wrist
    10: 16,  # right_wrist
    11: 23,  # left_hip
    12: 24,  # right_hip
    13: 25,  # left_knee
    14: 26,  # right_knee
    15: 27,  # left_ankle
    16: 28,  # right_ankle
}


class RTMPoseDetector(BaseDetector):
    """
    RTMPose backend using rtmlib.

    Detects the person with the highest mean keypoint confidence and maps
    the resulting 17 COCO keypoints to the 33-slot MediaPipe layout.

    Args:
        variant:  ``"rtmpose_s"`` (default), ``"rtmpose_m"``, or ``"rtmpose_x"``.
        device:   ``"cpu"`` (default) or ``"cuda"`` for GPU inference.
    """

    def __init__(
        self,
        variant: str = "rtmpose_s",
        device: str = "cpu",
    ) -> None:
        if variant not in _VARIANT_TO_MODE:
            raise ValueError(
                f"Unknown RTMPose variant {variant!r}. "
                f"Valid options: {list(_VARIANT_TO_MODE)}"
            )

        try:
            from rtmlib import Body  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "rtmlib is not installed.\n"
                "Install it with:  pip install rtmlib"
            ) from exc

        mode = _VARIANT_TO_MODE[variant]
        print(f"[RTMPoseDetector] Loading {variant} (mode={mode}, device={device}) …")
        # Pass det=None and pose=None so Body selects URLs from its MODE table.
        self._body = Body(
            mode=mode,
            backend="onnxruntime",
            device=device,
        )
        print("[RTMPoseDetector] Ready.")

    # ── BaseDetector interface ────────────────────────────────────────────────
    def detect(self, bgr_frame: np.ndarray, timestamp_ms: int) -> list[Keypoint] | None:  # noqa: ARG002
        # rtmlib returns BGR-ready frames directly
        keypoints, scores = self._body(bgr_frame)
        # keypoints: (N, 17, 2) pixel coords | scores: (N, 17) confidences

        if keypoints is None or len(keypoints) == 0:
            return None

        h, w = bgr_frame.shape[:2]

        # Pick the person with the highest mean keypoint confidence
        mean_scores = scores.mean(axis=1)          # (N,)
        best_idx    = int(mean_scores.argmax())

        kp_xy   = keypoints[best_idx]              # (17, 2)  pixel coords
        kp_conf = scores[best_idx]                 # (17,)

        out: list[Keypoint] = [Keypoint(0.0, 0.0, 0.0)] * 33
        for coco_i, mp_i in _COCO_TO_MP.items():
            x_px, y_px = kp_xy[coco_i]
            out[mp_i] = Keypoint(
                x=float(x_px) / max(w, 1),
                y=float(y_px) / max(h, 1),
                visibility=float(kp_conf[coco_i]),
            )
        return out
