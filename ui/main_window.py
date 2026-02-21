"""
MainWindow — top-level application window.

Layout:
  ┌─ Top bar ──────────────────────────────────────────────────────┐
  │ 🏋  AI Exercise Trainer                                         │
  ├──────────────┬─────────────────────────────┬───────────────────┤
  │  Sidebar     │       Camera feed           │   Stats panel     │
  │  (exercises, │  (skeleton overlay, full    │  (reps, state,    │
  │   tip, reset)│   aspect-ratio preserved)   │   gauge, feedback)│
  └──────────────┴─────────────────────────────┴───────────────────┘
"""
from __future__ import annotations

import numpy as np
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QImage, QPixmap
from PyQt6.QtWidgets import (
    QFrame,
    QGraphicsDropShadowEffect,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from camera.camera_thread import CameraThread
from core.exercises import REGISTRY
from ui.widgets.angle_gauge import AngleGauge
from ui.widgets.exercise_button import ExerciseButton
from ui.widgets.stat_card import StatCard


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("AI Exercise Trainer")
        self.resize(1200, 720)
        self.setMinimumSize(900, 600)
        self.setStyleSheet("QMainWindow { background: #0f172a; }")

        self._thread: CameraThread | None = None
        self._ex_buttons: list[ExerciseButton] = []
        self._current_backend: str = "mediapipe"
        self._current_ex_idx:  int = 0

        self._build_ui()
        self._start_camera()

    # ══════════════════════════════════════════════════════════════
    #  UI CONSTRUCTION
    # ══════════════════════════════════════════════════════════════
    def _build_ui(self) -> None:
        root = QWidget()
        root.setStyleSheet("background: #0f172a;")
        self.setCentralWidget(root)

        outer = QVBoxLayout(root)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)
        outer.addWidget(self._build_topbar())

        body = QHBoxLayout()
        body.setContentsMargins(16, 16, 16, 16)
        body.setSpacing(16)
        body.addWidget(self._build_sidebar())
        body.addWidget(self._build_camera_panel(), stretch=1)
        body.addWidget(self._build_stats_panel())
        outer.addLayout(body, stretch=1)

    def _build_topbar(self) -> QWidget:
        bar = QWidget()
        bar.setFixedHeight(54)
        bar.setStyleSheet("background: #0f172a; border-bottom: 1px solid #1e293b;")
        lay = QHBoxLayout(bar)
        lay.setContentsMargins(20, 0, 20, 0)

        logo = QLabel("🏋  AI Exercise Trainer")
        logo.setStyleSheet("color: #f1f5f9; font: 700 16px 'Segoe UI';")
        lay.addWidget(logo)
        lay.addStretch()

        # ── Backend toggle ────────────────────────────────────────────────────
        toggle_wrap = QFrame()
        toggle_wrap.setStyleSheet(
            "QFrame { background: #1e293b; border-radius: 8px; "
            "border: 1px solid #334155; }"
        )
        toggle_lay = QHBoxLayout(toggle_wrap)
        toggle_lay.setContentsMargins(3, 3, 3, 3)
        toggle_lay.setSpacing(2)

        self._btn_mediapipe = QPushButton("⚡ MediaPipe")
        self._btn_yolo      = QPushButton("🎯 YOLOv8")
        for btn in (self._btn_mediapipe, self._btn_yolo):
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            toggle_lay.addWidget(btn)

        self._btn_mediapipe.clicked.connect(lambda: self._on_backend_changed("mediapipe"))
        self._btn_yolo.clicked.connect(lambda: self._on_backend_changed("yolo"))
        lay.addWidget(toggle_wrap)
        self._update_backend_buttons()
        return bar

    def _build_sidebar(self) -> QWidget:
        container = QFrame()
        container.setFixedWidth(210)
        container.setStyleSheet("background: #0f172a;")

        lay = QVBoxLayout(container)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(8)

        # Section header
        hdr = QLabel("EXERCISES")
        hdr.setStyleSheet("color: #475569; font: 700 10px 'Segoe UI'; padding: 0 4px 8px 4px;")
        lay.addWidget(hdr)

        # Scrollable exercise list
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        btn_container = QWidget()
        btn_container.setStyleSheet("background: transparent;")
        btn_lay = QVBoxLayout(btn_container)
        btn_lay.setContentsMargins(0, 0, 0, 0)
        btn_lay.setSpacing(6)

        for ex_id, ex in REGISTRY.items():
            btn = ExerciseButton(f"  {ex.name}")
            btn.clicked.connect(lambda _checked, idx=ex_id: self._on_exercise_selected(idx))
            self._ex_buttons.append(btn)
            btn_lay.addWidget(btn)

        btn_lay.addStretch()
        scroll.setWidget(btn_container)
        lay.addWidget(scroll, stretch=1)

        # Tip box
        self._tip_label = QLabel()
        self._tip_label.setWordWrap(True)
        self._tip_label.setStyleSheet("""
            color: #64748b;
            font: 400 11px 'Segoe UI';
            background: #1e293b;
            border-radius: 8px;
            padding: 10px;
            border: 1px solid #334155;
        """)
        lay.addWidget(self._tip_label)

        # Reset button
        reset_btn = QPushButton("↺  Reset Reps")
        reset_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_btn.setStyleSheet("""
            QPushButton {
                background: #1e293b;
                color: #94a3b8;
                border-radius: 10px;
                padding: 10px;
                font: 600 12px 'Segoe UI';
                border: 1px solid #334155;
            }
            QPushButton:hover { background: #273549; color: #f1f5f9; }
        """)
        reset_btn.clicked.connect(self._on_reset_reps)
        lay.addWidget(reset_btn)

        return container

    def _build_camera_panel(self) -> QWidget:
        frame = QFrame()
        frame.setStyleSheet("""
            QFrame {
                background: #0a0f1a;
                border-radius: 16px;
                border: 1px solid #1e293b;
            }
        """)
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setColor(QColor(0, 0, 0, 120))
        shadow.setOffset(0, 4)
        frame.setGraphicsEffect(shadow)

        lay = QVBoxLayout(frame)
        lay.setContentsMargins(8, 8, 8, 8)

        self._cam_label = QLabel("📷  Waiting for camera…")
        self._cam_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._cam_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._cam_label.setStyleSheet(
            "color: #334155; font: 400 14px 'Segoe UI'; background: transparent;"
        )
        lay.addWidget(self._cam_label)

        return frame

    def _build_stats_panel(self) -> QWidget:
        panel = QFrame()
        panel.setFixedWidth(210)
        panel.setStyleSheet("background: #0f172a;")

        lay = QVBoxLayout(panel)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(12)

        hdr = QLabel("STATS")
        hdr.setStyleSheet("color: #475569; font: 700 10px 'Segoe UI'; padding: 0 4px 8px 4px;")
        lay.addWidget(hdr)

        self._card_reps  = StatCard("Reps",  "0")
        self._card_state = StatCard("State", "UP")
        lay.addWidget(self._card_reps)
        lay.addWidget(self._card_state)

        # Angle gauge card
        gauge_card = QFrame()
        gauge_card.setStyleSheet("""
            QFrame {
                background: #1e293b;
                border-radius: 12px;
                border: 1px solid #334155;
            }
        """)
        g_lay = QVBoxLayout(gauge_card)
        g_lay.setContentsMargins(8, 8, 8, 8)
        g_hdr = QLabel("ANGLE")
        g_hdr.setStyleSheet("color: #64748b; font: 700 10px 'Segoe UI';")
        g_hdr.setAlignment(Qt.AlignmentFlag.AlignCenter)
        g_lay.addWidget(g_hdr)
        self._gauge = AngleGauge()
        g_lay.addWidget(self._gauge)
        lay.addWidget(gauge_card)

        # Feedback label
        self._feedback_label = QLabel("—")
        self._feedback_label.setWordWrap(True)
        self._feedback_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_feedback_style("#94a3b8")
        lay.addWidget(self._feedback_label)

        lay.addStretch()
        return panel

    # ══════════════════════════════════════════════════════════════
    #  CAMERA THREAD
    # ══════════════════════════════════════════════════════════════
    def _start_camera(self) -> None:
        self._thread = CameraThread(backend=self._current_backend, parent=self)
        self._thread.frame_ready.connect(self._on_frame_ready)
        self._thread.stats_updated.connect(self._on_stats_updated)
        self._thread.state_changed.connect(self._on_state_changed)
        self._thread.start()
        self._on_exercise_selected(self._current_ex_idx)

    # ══════════════════════════════════════════════════════════════
    #  SLOTS
    # ══════════════════════════════════════════════════════════════
    def _on_exercise_selected(self, idx: int) -> None:
        self._current_ex_idx = idx
        for i, btn in enumerate(self._ex_buttons):
            btn.setChecked(i == idx)
        self._tip_label.setText(REGISTRY[idx].tip)
        if self._thread:
            self._thread.set_exercise(idx)

    def _on_reset_reps(self) -> None:
        if self._thread:
            self._thread.reset_reps()

    # ── Backend switching ──────────────────────────────────────────────────────
    def _on_backend_changed(self, backend: str) -> None:
        if backend == self._current_backend:
            return
        self._current_backend = backend
        self._update_backend_buttons()
        if self._thread:
            self._thread.stop()
            self._thread.wait(3000)
            self._thread = None
        self._start_camera()

    def _update_backend_buttons(self) -> None:
        _ACTIVE   = ("background: #3b82f6; color: #ffffff; border-radius: 6px;"
                     " font: 600 11px 'Segoe UI'; padding: 0 12px; border: none;")
        _INACTIVE = ("background: transparent; color: #64748b; border-radius: 6px;"
                     " font: 600 11px 'Segoe UI'; padding: 0 12px; border: none;")
        self._btn_mediapipe.setStyleSheet(
            _ACTIVE if self._current_backend == "mediapipe" else _INACTIVE
        )
        self._btn_yolo.setStyleSheet(
            _ACTIVE if self._current_backend == "yolo" else _INACTIVE
        )

    def _on_frame_ready(self, frame: np.ndarray) -> None:
        h, w, ch  = frame.shape
        qimg      = QImage(frame.data, w, h, ch * w, QImage.Format.Format_BGR888)
        pixmap    = QPixmap.fromImage(qimg)
        self._cam_label.setPixmap(
            pixmap.scaled(
                self._cam_label.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        )

    def _on_stats_updated(
        self, angle: float, feedback_msg: str, feedback_color: str, reps: int
    ) -> None:
        self._card_reps.set_value(str(reps))
        self._gauge.set_angle(angle)
        if feedback_msg:
            self._feedback_label.setText(feedback_msg)
            self._set_feedback_style(feedback_color)

    def _on_state_changed(self, state: str) -> None:
        self._card_state.set_value(state)
        self._card_state.set_value_color("#22c55e" if state == "UP" else "#f59e0b")

    # ══════════════════════════════════════════════════════════════
    #  LIFECYCLE
    # ══════════════════════════════════════════════════════════════
    def closeEvent(self, event) -> None:  # noqa: N802
        if self._thread:
            self._thread.stop()
            self._thread.wait(3000)
        super().closeEvent(event)

    # ══════════════════════════════════════════════════════════════
    #  HELPERS
    # ══════════════════════════════════════════════════════════════
    def _set_feedback_style(self, color: str) -> None:
        self._feedback_label.setStyleSheet(f"""
            color: {color};
            font: 600 13px 'Segoe UI';
            background: #1e293b;
            border-radius: 10px;
            padding: 14px 10px;
            border: 1px solid #334155;
        """)
