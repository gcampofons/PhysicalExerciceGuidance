"""
CameraThread — runs in a background QThread.

Responsibilities:
  - Capture frames from webcam / video file / screen capture (mss).
  - Pass frames through the active pose detector.
  - Delegate rep counting to RepCounter.
  - Draw the skeleton overlay via draw_skeleton().
  - Emit Qt signals consumed by the UI.

The thread owns no UI knowledge; it only emits typed signals.

Source constants
----------------
SOURCE_CAMERA  — live webcam (default)
SOURCE_SCREEN  — primary-monitor screen capture (requires: pip install mss)
<file path>    — any video file readable by OpenCV
"""
from __future__ import annotations

import time

import cv2
import numpy as np
from PyQt6.QtCore import QThread, pyqtSignal

from core.config import CAMERA_INDEX, CAMERA_WIDTH, CAMERA_HEIGHT, MIN_LANDMARK_VISIBILITY
from core.exercises import REGISTRY, Exercise
from core.geometry import angle_between, landmark_xy
from core.landmarks import POSE_CONNECTIONS
from detection.detector_factory import create_detector
from detection.rep_counter import RepCounter

# ── Source identifiers ────────────────────────────────────────────────────────
SOURCE_CAMERA = "camera"
SOURCE_SCREEN = "screen"


def list_monitors() -> list[dict]:
    """
    Return a list of monitor descriptors from mss.

    Each item is a dict with keys: index, left, top, width, height.
    index=1 is the primary monitor (mss.monitors[0] is the virtual all-in-one).
    Returns an empty list if mss is not installed.
    """
    try:
        import mss  # type: ignore
        with mss.mss() as sct:
            # sct.monitors[0] = combined virtual desktop — skip it
            return [
                {"index": i + 1, **{k: m[k] for k in ("left", "top", "width", "height")}}
                for i, m in enumerate(sct.monitors[1:])
            ]
    except Exception:
        return []


def draw_skeleton(frame: np.ndarray, landmarks: list, vis_threshold: float = 0.4) -> None:
    """Draw the pose skeleton onto a BGR frame in-place, skipping invisible joints."""
    h, w = frame.shape[:2]
    pts  = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    vis  = [lm.visibility for lm in landmarks]
    for a, b in POSE_CONNECTIONS:
        if a < len(pts) and b < len(pts):
            if vis[a] >= vis_threshold and vis[b] >= vis_threshold:
                cv2.line(frame, pts[a], pts[b], (200, 200, 200), 1, cv2.LINE_AA)
    for i, pt in enumerate(pts):
        if vis[i] >= vis_threshold:
            cv2.circle(frame, pt, 4, (0, 220, 180), -1, cv2.LINE_AA)


class CameraThread(QThread):
    """
    Background thread that captures video, runs pose detection and emits
    signals to drive the UI.

    Signals:
        frame_ready(np.ndarray):             BGR frame with skeleton overlay.
        stats_updated(float, str, str, int): angle, feedback_msg,
                                             feedback_color, reps.
        state_changed(str):                  "UP" or "DOWN".
    """

    frame_ready   = pyqtSignal(np.ndarray)
    stats_updated = pyqtSignal(float, str, str, int)   # angle, msg, color, reps
    state_changed = pyqtSignal(str)

    def __init__(
        self,
        backend:       str = "mediapipe",
        source:        str = SOURCE_CAMERA,
        monitor_index: int = 1,
        parent=None,
    ) -> None:
        super().__init__(parent)
        self._running       = True
        self._exercise      = REGISTRY[0]
        self._counter       = RepCounter(exercise=self._exercise)
        self._source        = source          # SOURCE_CAMERA | SOURCE_SCREEN | file path
        self._monitor_index = monitor_index   # 1-based mss monitor index

        # Detector is created HERE (main thread) because on Windows, PyTorch
        # and other native libraries must load their DLLs on the main thread.
        self._detector      = create_detector(backend)
        self._backend_label = backend.upper()

    # ── Public API (thread-safe via Python GIL for simple assignments) ────────
    def set_exercise(self, exercise_id: int) -> None:
        self._exercise = REGISTRY[exercise_id]
        self._counter  = RepCounter(exercise=self._exercise)

    def reset_reps(self) -> None:
        self._counter.reset()

    def stop(self) -> None:
        self._running = False
        self._detector.close()

    @property
    def current_exercise(self) -> Exercise:
        return self._exercise

    # ── Thread main loop ──────────────────────────────────────────────────────
    def run(self) -> None:
        if self._source == SOURCE_SCREEN:
            self._run_screen()
        elif self._source == SOURCE_CAMERA:
            cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
            cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self._run_capture(cap, flip=True, is_file=False)
        else:
            # Assume it's a video file path
            cap = cv2.VideoCapture(self._source)
            self._run_capture(cap, flip=False, is_file=True)

    # ── Capture loop (webcam or file) ─────────────────────────────────────────
    def _run_capture(
        self, cap: cv2.VideoCapture, flip: bool, is_file: bool
    ) -> None:
        src_label  = "CAM" if not is_file else "FILE"
        start_time = time.time()
        detector   = self._detector

        while self._running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                if is_file:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)   # loop video
                    continue
                continue

            if flip:
                frame = cv2.flip(frame, 1)
            frame = cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))
            ts_ms = int((time.time() - start_time) * 1000)
            self._process_frame(frame, detector, ts_ms, src_label)

        cap.release()

    # ── Screen-capture loop (mss) ─────────────────────────────────────────────
    def _run_screen(self) -> None:
        try:
            import mss  # type: ignore
        except ImportError:
            blank = np.zeros((CAMERA_HEIGHT, CAMERA_WIDTH, 3), dtype=np.uint8)
            cv2.putText(
                blank, "Run: pip install mss",
                (30, CAMERA_HEIGHT // 2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 80, 220), 2, cv2.LINE_AA,
            )
            self.frame_ready.emit(blank)
            return

        start_time = time.time()
        detector   = self._detector

        with mss.mss() as sct:
            # monitors[0] is the combined virtual desktop; real monitors start at 1
            idx     = max(1, min(self._monitor_index, len(sct.monitors) - 1))
            monitor = sct.monitors[idx]
            scr_label = f"SCR{idx}"
            while self._running:
                img   = np.array(sct.grab(monitor))              # BGRA
                frame = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
                frame = cv2.resize(frame, (CAMERA_WIDTH, CAMERA_HEIGHT))
                ts_ms = int((time.time() - start_time) * 1000)
                self._process_frame(frame, detector, ts_ms, scr_label)

    # ── Shared detection + overlay + emit pipeline ────────────────────────────
    def _process_frame(
        self,
        frame:     np.ndarray,
        detector,
        ts_ms:     int,
        src_label: str,
    ) -> None:
        h, w = frame.shape[:2]
        landmarks = detector.detect(frame, ts_ms)

        angle          = 0.0
        feedback_msg   = ""
        feedback_color = "#94a3b8"

        if landmarks:
            draw_skeleton(frame, landmarks)
            ex = self._exercise
            j0, j1, j2 = ex.joint

            try:
                # ── Visibility guard ──────────────────────────────────────
                # Skip angle computation when any of the three joints is
                # occluded or out of frame to prevent erratic rep counts.
                vis = [landmarks[j].visibility for j in (j0, j1, j2)]
                if min(vis) < MIN_LANDMARK_VISIBILITY:
                    feedback_msg   = "⚠ Keep full body in frame"
                    feedback_color = "#ef4444"
                else:
                    A = landmark_xy(landmarks, j0)
                    B = landmark_xy(landmarks, j1)
                    C = landmark_xy(landmarks, j2)
                    angle = angle_between(A, B, C)

                    # Annotate joint angle on frame
                    bx = int(B[0] * w)
                    by = int(B[1] * h)
                    cv2.putText(
                        frame, f"{int(angle)}",
                        (bx + 8, by - 8),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.55, (0, 220, 180), 1, cv2.LINE_AA,
                    )

                    # Rep counting
                    self._counter.update(angle)

                    # Feedback
                    rule = ex.get_feedback(angle)
                    if rule:
                        feedback_msg   = rule.message
                        feedback_color = rule.color

            except Exception:
                feedback_msg = "Move into frame"

        # ── HUD overlay: [BACKEND|SOURCE] ─────────────────────────────────────
        label = f"[{self._backend_label}|{src_label}]"
        cv2.putText(
            frame, label,
            (8, 22),
            cv2.FONT_HERSHEY_SIMPLEX, 0.58,
            (0, 255, 128) if "YOLO" in self._backend_label else (255, 180, 0),
            2, cv2.LINE_AA,
        )
        # ─────────────────────────────────────────────────────────────────────
        self.frame_ready.emit(frame.copy())
        self.stats_updated.emit(angle, feedback_msg, feedback_color, self._counter.reps)
        self.state_changed.emit(self._counter.state)
