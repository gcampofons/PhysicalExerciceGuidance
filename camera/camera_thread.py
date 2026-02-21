"""
CameraThread — runs in a background QThread.

Responsibilities:
  - Capture frames from the webcam (OpenCV).
  - Pass frames through PoseDetector.
  - Delegate rep counting to RepCounter.
  - Draw the skeleton overlay via draw_skeleton().
  - Emit Qt signals consumed by the UI.

The thread owns no UI knowledge; it only emits typed signals.
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
        frame_ready(np.ndarray):            BGR frame with skeleton overlay.
        stats_updated(float, str, str, int): angle, feedback_msg,
                                             feedback_color, reps.
        state_changed(str):                 "UP" or "DOWN".
    """

    frame_ready   = pyqtSignal(np.ndarray)
    stats_updated = pyqtSignal(float, str, str, int)   # angle, msg, color, reps
    state_changed = pyqtSignal(str)

    def __init__(self, backend: str = "mediapipe", parent=None) -> None:
        super().__init__(parent)
        self._running  = True
        self._exercise = REGISTRY[0]
        self._counter  = RepCounter(exercise=self._exercise)

        # Detector is created HERE (main thread) because on Windows, PyTorch
        # and other native libraries must load their DLLs on the main thread.
        self._detector       = create_detector(backend)
        self._backend_label  = f"[{backend.upper()}]"

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
        cap = cv2.VideoCapture(CAMERA_INDEX, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAMERA_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)

        start_time = time.time()
        detector   = self._detector

        while self._running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                continue

            frame     = cv2.flip(frame, 1)
            h, w      = frame.shape[:2]
            ts_ms     = int((time.time() - start_time) * 1000)
            landmarks = detector.detect(frame, ts_ms)

            angle          = 0.0
            feedback_msg   = ""
            feedback_color = "#94a3b8"

            if landmarks:
                draw_skeleton(frame, landmarks)
                ex = self._exercise
                j0, j1, j2 = ex.joint

                try:
                    # ── Visibility guard ──────────────────────────────────
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

            # ── backend label overlay ─────────────────────────────────
            cv2.putText(
                frame, self._backend_label,
                (8, 22),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65,
                (0, 255, 128) if "YOLO" in self._backend_label else (255, 180, 0),
                2, cv2.LINE_AA,
            )
            # ──────────────────────────────────────────────────────────
            self.frame_ready.emit(frame.copy())
            self.stats_updated.emit(
                angle, feedback_msg, feedback_color, self._counter.reps
            )
            self.state_changed.emit(self._counter.state)

        cap.release()
