"""
AngleGauge — circular arc widget that displays a joint angle value.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QColor, QFont, QPainter, QPen
from PyQt6.QtWidgets import QWidget


class AngleGauge(QWidget):
    """
    Custom widget that renders a circular arc gauge for a joint angle.

    The arc colour transitions green → amber → red as the angle increases
    from 0° to 180°.
    """

    _ARC_START  = 210   # degrees, clock-position of arc start
    _ARC_SWEEP  = -240  # total sweep of the arc (negative = counter-clockwise)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self._angle: float = 0.0
        self.setMinimumSize(150, 150)

    # ── Public API ────────────────────────────────────────────────────────────
    def set_angle(self, angle: float) -> None:
        self._angle = angle
        self.update()

    # ── Painting ──────────────────────────────────────────────────────────────
    def paintEvent(self, _event) -> None:  # noqa: N802
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        W, H   = self.width(), self.height()
        cx, cy = W // 2, H // 2
        r      = min(W, H) // 2 - 18
        rect   = (cx - r, cy - r, r * 2, r * 2)

        # Background track
        track_pen = QPen(QColor("#1e293b"), 10, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
        painter.setPen(track_pen)
        painter.drawArc(*rect, self._ARC_START * 16, self._ARC_SWEEP * 16)

        # Value arc
        pct  = self._angle / 180.0
        span = int(self._ARC_SWEEP * pct * 16)
        value_pen = QPen(
            QColor(self._arc_color(pct)), 10,
            Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap,
        )
        painter.setPen(value_pen)
        painter.drawArc(*rect, self._ARC_START * 16, span)

        # Centre text — angle value
        painter.setPen(QColor("#f1f5f9"))
        painter.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        painter.drawText(
            QRectF(cx - 45, cy - 22, 90, 44),
            Qt.AlignmentFlag.AlignCenter,
            f"{int(self._angle)}°",
        )

        # Sub-label
        painter.setPen(QColor("#64748b"))
        painter.setFont(QFont("Segoe UI", 8))
        painter.drawText(
            QRectF(cx - 40, cy + 18, 80, 18),
            Qt.AlignmentFlag.AlignCenter,
            "joint angle",
        )

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _arc_color(pct: float) -> str:
        if pct < 0.33:
            return "#22c55e"   # green
        if pct < 0.66:
            return "#f59e0b"   # amber
        return "#ef4444"       # red
