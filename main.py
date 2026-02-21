"""
Entry point for the AI Exercise Trainer application.

Run:
    python main.py
"""
import sys

# ── Pre-load PyTorch DLLs before QApplication starts ─────────────────────────
# On Windows, native DLLs (including torch's c10.dll) must be loaded during
# normal process startup — before any GUI event loop is running.  Importing
# torch here (silently, if not installed) ensures the DLLs are resident before
# Qt takes over, preventing WinError 1114 when switching to the YOLOv8 backend.
try:
    import torch  # noqa: F401
except Exception:
    pass  # YOLOv8 backend simply won't be available

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow


def main() -> None:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
