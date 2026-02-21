"""
YOLOv8-Pose backend.

Requires: pip install ultralytics
The model (yolov8n-pose.pt, ~6 MB) is downloaded automatically by
ultralytics on the first call if not already cached locally.

YOLO outputs 17 COCO keypoints; this class maps them to the 33-slot
MediaPipe layout so the rest of the pipeline is backend-agnostic.
"""
from __future__ import annotations

import numpy as np

from detection.base_detector import BaseDetector
from detection.keypoint import Keypoint

# ── COCO-17 → MediaPipe-33 slot mapping ──────────────────────────────────────
#
#   COCO idx  │  Body part        │  MediaPipe idx
#   ----------┼───────────────────┼───────────────
#       0     │  nose             │   0
#       1     │  left_eye         │   2
#       2     │  right_eye        │   5
#       3     │  left_ear         │   7
#       4     │  right_ear        │   8
#       5     │  left_shoulder    │  11
#       6     │  right_shoulder   │  12
#       7     │  left_elbow       │  13
#       8     │  right_elbow      │  14
#       9     │  left_wrist       │  15
#      10     │  right_wrist      │  16
#      11     │  left_hip         │  23
#      12     │  right_hip        │  24
#      13     │  left_knee        │  25
#      14     │  right_knee       │  26
#      15     │  left_ankle       │  27
#      16     │  right_ankle      │  28
#
_COCO_TO_MP: dict[int, int] = {
    0:  0,
    1:  2,
    2:  5,
    3:  7,
    4:  8,
    5:  11,
    6:  12,
    7:  13,
    8:  14,
    9:  15,
    10: 16,
    11: 23,
    12: 24,
    13: 25,
    14: 26,
    15: 27,
    16: 28,
}

_MODEL_NAME = "yolov8n-pose.pt"  # smallest / fastest pose model


class YOLODetector(BaseDetector):
    """
    YOLOv8-Pose backend.

    Detects the highest-confidence person in each frame and returns 33
    Keypoints mapped to MediaPipe slot indices. COCO keypoints that have no
    MediaPipe equivalent (fingers, toes) are left as Keypoint(0, 0, 0).
    """

    def __init__(self) -> None:
        try:
            from ultralytics import YOLO  # type: ignore[import]
        except ImportError as exc:
            raise ImportError(
                "ultralytics is not installed.\n"
                "Install it with:  pip install ultralytics"
            ) from exc

        print(f"[YOLODetector] Loading {_MODEL_NAME} …")
        self._model = YOLO(_MODEL_NAME)
        print("[YOLODetector] Ready.")

    # ── BaseDetector interface ─────────────────────────────────────────────────
    def detect(self, bgr_frame: np.ndarray, timestamp_ms: int) -> list[Keypoint] | None:  # noqa: ARG002
        results = self._model(bgr_frame, verbose=False)
        res     = results[0]

        if res.keypoints is None or len(res.keypoints.xy) == 0:
            return None

        # Pick the person with the highest mean keypoint confidence
        best_idx = int(res.keypoints.conf.mean(dim=1).argmax().item())
        kp_xy    = res.keypoints.xy[best_idx].cpu().numpy()    # (17, 2) pixels
        kp_conf  = res.keypoints.conf[best_idx].cpu().numpy()  # (17,)
        h, w     = bgr_frame.shape[:2]

        # Build 33-slot list; unmapped slots keep visibility=0
        out: list[Keypoint] = [Keypoint(0.0, 0.0, 0.0)] * 33
        for coco_i, mp_i in _COCO_TO_MP.items():
            x_px, y_px = kp_xy[coco_i]
            out[mp_i] = Keypoint(
                x=float(x_px) / max(w, 1),
                y=float(y_px) / max(h, 1),
                visibility=float(kp_conf[coco_i]),
            )
        return out
