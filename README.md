# 🏋 AI Exercise Trainer

A real-time exercise guidance application that uses your webcam and AI pose estimation to count repetitions and provide live form feedback — no gym equipment or wearables required.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-orange)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green)

---

## Features

- **Real-time pose estimation** — 33 body landmarks tracked at webcam framerate using Google MediaPipe
- **Automatic rep counting** — UP/DOWN state machine triggered by joint angle thresholds
- **Live form feedback** — colour-coded coaching tips per exercise (green = good, amber = needs improvement, red = warning)
- **Visibility guard** — rep counting is frozen when joints move out of frame to prevent phantom reps
- **9 exercises out of the box** — Squat, Bicep Curl, Push-up, Lateral Raise, Overhead Press, Tricep Extension, Front Raise, Lunge, Shoulder Tap
- **Professional dark UI** — built with PyQt6; camera feed is a component inside the layout, not a raw OpenCV window
- **Easily extensible** — adding a new exercise is 10 lines in `core/exercises.py`, nothing else changes

---

## Screenshots

| Menu | Exercise in progress |
|---|---|
| Exercise list with tips | Skeleton overlay + angle gauge + rep counter |

---

## Requirements

- Python 3.11 or later
- Webcam
- Windows (tested), macOS / Linux should work with minor `CAP_DSHOW` changes

---

## Installation

```bash
# 1. Clone the repo
git clone https://github.com/your-username/PhysicalExerciceGuidance.git
cd PhysicalExerciceGuidance

# 2. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

> The MediaPipe pose model (~5 MB) is downloaded automatically on first launch and cached at `assets/models/pose_landmarker_lite.task`.

---

## Usage

```bash
python main.py
```

1. The app opens with a list of exercises in the left sidebar.
2. Click an exercise to select it — the sidebar shows a coaching tip.
3. Stand in front of your webcam so the relevant joints are visible.
4. Perform the movement — reps and form feedback update in real time.
5. Click **↺ Reset Reps** to restart the counter for a new set.

---

## Project Structure

```
PhysicalExerciceGuidance/
│
├── main.py                        # Entry point — starts the Qt application
├── requirements.txt
│
├── assets/
│   └── models/
│       └── pose_landmarker_lite.task   # Auto-downloaded on first run
│
├── core/                          # Pure domain logic — no UI, no OpenCV
│   ├── config.py                  # Paths, camera settings, thresholds
│   ├── landmarks.py               # 33 landmark index constants + skeleton connections
│   ├── exercises.py               # Exercise dataclass + REGISTRY
│   └── geometry.py                # angle_between(), landmark_xy()
│
├── detection/                     # ML / computer vision layer
│   ├── pose_detector.py           # MediaPipe wrapper (download + detect)
│   └── rep_counter.py             # UP/DOWN state machine
│
├── camera/
│   └── camera_thread.py           # QThread — orchestrates capture, detection, signals
│
└── ui/
    ├── main_window.py             # MainWindow — layout + slots, zero business logic
    └── widgets/
        ├── angle_gauge.py         # Custom circular arc gauge
        ├── exercise_button.py     # Checkable sidebar button
        └── stat_card.py           # Metric display card
```

---

## Adding a New Exercise

Open `core/exercises.py` and append a `_register()` call:

```python
from core.landmarks import RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE

_register(Exercise(
    id=9, name="Bulgarian Split Squat",
    joint=(RIGHT_HIP, RIGHT_KNEE, RIGHT_ANKLE),
    down_max=100, up_min=160,
    tip="Keep your front knee behind your toes.",
    feedback=[
        FeedbackRule(0,   100, "✓ Good depth!",        "#22c55e"),
        FeedbackRule(100, 160, "↓ Go lower",            "#f59e0b"),
        FeedbackRule(160, 180, "↑ Stand up fully",      "#94a3b8"),
    ],
))
```

The button appears in the sidebar automatically — no other file needs to be changed.

---

## How It Works

```
Webcam frame
    │
    ▼
PoseDetector.detect()          ← MediaPipe Pose Landmarker (VIDEO mode)
    │  33 landmarks (x, y, visibility)
    ▼
visibility check               ← all 3 joints must be > 0.6
    │  pass
    ▼
geometry.angle_between()       ← angle at the middle joint (A–B–C)
    │  angle °
    ▼
RepCounter.update()            ← UP/DOWN state machine
    │  reps, state
    ▼
Qt signals ──────────────────► MainWindow slots (frame, stats, feedback)
```

---

## Configuration

All tuneable constants live in `core/config.py`:

| Constant | Default | Description |
|---|---|---|
| `CAMERA_INDEX` | `0` | Webcam device index |
| `CAMERA_WIDTH` | `640` | Capture width (px) |
| `CAMERA_HEIGHT` | `480` | Capture height (px) |
| `MIN_DETECTION_CONFIDENCE` | `0.55` | MediaPipe detection threshold |
| `MIN_TRACKING_CONFIDENCE` | `0.55` | MediaPipe tracking threshold |
| `MIN_LANDMARK_VISIBILITY` | `0.6` | Below this, angle/rep logic is skipped |

---

## Dependencies

| Package | Purpose |
|---|---|
| `mediapipe` | Pose landmark detection |
| `opencv-python` | Webcam capture + frame drawing |
| `numpy` | Vector math for angle calculation |
| `PyQt6` | Desktop UI framework |

---

## License

MIT
