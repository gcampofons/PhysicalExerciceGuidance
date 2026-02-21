"""
StatCard — compact card widget for displaying a labelled metric value.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFrame, QLabel, QVBoxLayout


class StatCard(QFrame):
    """
    A rounded card that shows a large primary value and a small label.

    Example:
        card = StatCard("Reps", "0")
        card.set_value("12")
        card.set_value_color("#22c55e")
    """

    _BASE_STYLE = """
        QFrame#StatCard {{
            background: #1e293b;
            border-radius: 12px;
            border: 1px solid #334155;
        }}
    """
    _LABEL_STYLE = "color: #64748b; font: 700 10px 'Segoe UI';"
    _VALUE_STYLE = "color: {color}; font: 700 36px 'Segoe UI';"

    def __init__(self, label: str, value: str = "—", parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("StatCard")
        self.setStyleSheet(self._BASE_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(2)

        self._lbl_label = QLabel(label.upper())
        self._lbl_label.setStyleSheet(self._LABEL_STYLE)
        self._lbl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._lbl_value = QLabel(value)
        self._lbl_value.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_value_style("#f1f5f9")

        layout.addWidget(self._lbl_label)
        layout.addWidget(self._lbl_value)

    # ── Public API ────────────────────────────────────────────────────────────
    def set_value(self, value: str) -> None:
        self._lbl_value.setText(value)

    def set_value_color(self, color: str) -> None:
        self._set_value_style(color)

    # ── Private ───────────────────────────────────────────────────────────────
    def _set_value_style(self, color: str) -> None:
        self._lbl_value.setStyleSheet(self._VALUE_STYLE.format(color=color))
