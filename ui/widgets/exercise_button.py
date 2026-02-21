"""
ExerciseButton — a checkable QPushButton styled for the exercise sidebar.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QPushButton

_ACTIVE_STYLE = """
    QPushButton {
        background: #3b82f6;
        color: #fff;
        border-radius: 10px;
        padding: 12px 16px;
        font: 600 13px 'Segoe UI';
        text-align: left;
        border: none;
    }
"""

_INACTIVE_STYLE = """
    QPushButton {
        background: #1e293b;
        color: #94a3b8;
        border-radius: 10px;
        padding: 12px 16px;
        font: 600 13px 'Segoe UI';
        text-align: left;
        border: 1px solid #334155;
    }
    QPushButton:hover {
        background: #273549;
        color: #e2e8f0;
    }
"""


class ExerciseButton(QPushButton):
    """
    A checkable button that visually switches between an active (blue)
    and inactive (dark) state when exercises are selected.
    """

    def __init__(self, text: str, parent=None) -> None:
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self._apply_style(False)

    # Override to keep style in sync whenever the checked state changes.
    def setChecked(self, checked: bool) -> None:  # noqa: N802
        super().setChecked(checked)
        self._apply_style(checked)

    # ── Private ───────────────────────────────────────────────────────────────
    def _apply_style(self, active: bool) -> None:
        self.setStyleSheet(_ACTIVE_STYLE if active else _INACTIVE_STYLE)
