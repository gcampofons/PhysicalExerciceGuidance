"""
MoveNet pose detection backend — TFLite version (fast CPU inference).

Supports two variants:
  - ``"movenet_lightning"``  — fastest, 30+ FPS on CPU (192×192)
  - ``"movenet_thunder"``    — more accurate, ~15 FPS on CPU (256×256)

The .tflite model is downloaded once via tf.keras.utils.get_file and cached
in assets/models/.  All subsequent runs load from disk instantly.

Both variants return 17 COCO keypoints mapped to the 33-slot MediaPipe layout.

Requires: pip install tensorflow
"""
from __future__ import annotations

import os
import numpy as np
import cv2

from core.config import MODELS_DIR
from detection.base_detector import BaseDetector
from detection.keypoint import Keypoint

# ── TFLite model info ─────────────────────────────────────────────────────────
# TF Hub lite-model URLs — keras.utils.get_file follows redirects correctly.
_MODELS: dict[str, dict] = {
    "movenet_lightning": {
        "filename":   "movenet_lightning_float16_4.tflite",
        "url":        (
            "https://tfhub.dev/google/lite-model/"
            "movenet/singlepose/lightning/tflite/float16/4"
            "?lite-format=tflite"
        ),
        "input_size": 192,
    },
    "movenet_thunder": {
        "filename":   "movenet_thunder_float16_4.tflite",
        "url":        (
            "https://tfhub.dev/google/lite-model/"
            "movenet/singlepose/thunder/tflite/float16/4"
            "?lite-format=tflite"
        ),
        "input_size": 256,
    },
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


def _download_tflite(filename: str, url: str) -> str:
    """Download the .tflite file if not cached; return local path."""
    try:
        import tensorflow as tf  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "tensorflow is required for MoveNet.\n"
            "Install with:  pip install tensorflow"
        ) from exc

    os.makedirs(MODELS_DIR, exist_ok=True)
    dest = os.path.join(MODELS_DIR, filename)
    if not os.path.exists(dest):
        print(f"[MoveNetDetector] Downloading {filename} …")
        # get_file follows HTTP redirects and handles TF Hub's download pages.
        tmp = tf.keras.utils.get_file(
            fname=filename,
            origin=url,
            cache_dir=MODELS_DIR,
            cache_subdir=".",
        )
        # get_file may place the file in a sub-dir; move to dest if needed.
        if os.path.abspath(tmp) != os.path.abspath(dest):
            import shutil
            shutil.move(tmp, dest)
        print("[MoveNetDetector] Download complete.")
    return dest


def _build_interpreter(model_path: str):
    """Return an allocated TFLite Interpreter."""
    try:
        import tensorflow as tf  # type: ignore[import]
        interp = tf.lite.Interpreter(
            model_path=model_path,
            num_threads=4,          # use up to 4 CPU threads
        )
        interp.allocate_tensors()
        return interp
    except ImportError:
        pass
    try:
        import tflite_runtime.interpreter as tflite  # type: ignore[import]
        interp = tflite.Interpreter(model_path=model_path, num_threads=4)
        interp.allocate_tensors()
        return interp
    except ImportError as exc:
        raise ImportError(
            "Neither 'tensorflow' nor 'tflite-runtime' is installed.\n"
            "Install with:  pip install tensorflow"
        ) from exc


class MoveNetDetector(BaseDetector):
    """
    MoveNet Single-Pose detector using the TFLite runtime.

    Args:
        variant: ``"movenet_lightning"`` (default) or ``"movenet_thunder"``.
    """

    def __init__(self, variant: str = "movenet_lightning") -> None:
        if variant not in _MODELS:
            raise ValueError(
                f"Unknown MoveNet variant {variant!r}. "
                f"Valid options: {list(_MODELS)}"
            )
        info       = _MODELS[variant]
        model_path = _download_tflite(info["filename"], info["url"])

        print(f"[MoveNetDetector] Loading {variant} (TFLite) …")
        self._interp     = _build_interpreter(model_path)
        self._input_size: int = info["input_size"]
        self._in_idx     = self._interp.get_input_details()[0]["index"]
        self._out_idx    = self._interp.get_output_details()[0]["index"]
        print("[MoveNetDetector] Ready.")

    # ── BaseDetector interface ────────────────────────────────────────────────
    def detect(self, bgr_frame: np.ndarray, timestamp_ms: int) -> list[Keypoint] | None:  # noqa: ARG002
        size = self._input_size

        img = cv2.resize(bgr_frame, (size, size))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        inp = img[np.newaxis].astype(np.uint8)  # (1, size, size, 3) uint8

        self._interp.set_tensor(self._in_idx, inp)
        self._interp.invoke()

        # Output: [1, 1, 17, 3]  — [y_norm, x_norm, confidence]
        raw = self._interp.get_tensor(self._out_idx)[0, 0]  # (17, 3)

        if float(raw[:, 2].max()) < 0.1:
            return None

        out: list[Keypoint] = [Keypoint(0.0, 0.0, 0.0)] * 33
        for coco_i, mp_i in _COCO_TO_MP.items():
            y_n, x_n, conf = raw[coco_i]
            out[mp_i] = Keypoint(
                x=float(np.clip(x_n, 0.0, 1.0)),
                y=float(np.clip(y_n, 0.0, 1.0)),
                visibility=float(conf),
            )
        return out


