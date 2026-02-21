# 🏋 AI Exercise Trainer

A real-time exercise guidance application that uses your webcam and AI pose estimation to count repetitions and provide live form feedback — no gym equipment or wearables required.

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10%2B-orange)
![PyQt6](https://img.shields.io/badge/PyQt6-6.6%2B-green)
![YOLOv8](https://img.shields.io/badge/YOLOv8-ultralytics-purple)

---

## Features

- **Dual pose-estimation backends** — switch live between ⚡ MediaPipe (33 keypoints) and 🎯 YOLOv8-Pose (17 COCO keypoints) with a single click; no restart needed
- **Backend label on frame** — the active backend (`[MEDIAPIPE]` or `[YOLO]`) is stamped directly onto the camera feed so there is never any doubt which engine is running
- **Automatic rep counting** — UP/DOWN state machine triggered by joint angle thresholds
- **Live form feedback** — colour-coded coaching tips per exercise (green = good, amber = needs improvement, red = warning)
- **Visibility guard** — rep counting is frozen when joints move out of frame to prevent phantom reps
- **33 exercises out of the box** — covering squats, curls, presses, rows, hinges, lunges, plyometrics and more (full list below)
- **Professional dark UI** — built with PyQt6; camera feed is a component inside the layout, not a raw OpenCV window
- **JSON-driven exercise registry** — add or edit exercises in `core/exercises_data.json` with no Python required

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

> **MediaPipe** — the pose landmarker model (~5 MB) is downloaded automatically on first launch and cached at `assets/models/pose_landmarker_lite.task`.
>
> **YOLOv8** (optional) — `ultralytics` and a CPU-only PyTorch build are required. Install them once:
> ```bash
> pip install ultralytics
> pip install --force-reinstall torch torchvision --index-url https://download.pytorch.org/whl/cpu
> ```
> The YOLOv8n-pose weights (~6 MB) are downloaded automatically by `ultralytics` on first use and cached in `%APPDATA%\Ultralytics\` (Windows).

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
6. Use the **⚡ MediaPipe** / **🎯 YOLOv8** buttons in the top bar to switch the pose-estimation engine live at any time.

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
│   ├── exercises.py               # Exercise dataclass + JSON loader → REGISTRY
│   ├── exercises_data.json        # All 33 exercise definitions (edit here to add/modify)
│   └── geometry.py                # angle_between(), landmark_xy()
│
├── detection/                     # ML / computer vision layer
│   ├── keypoint.py                # Keypoint(x, y, visibility) dataclass — shared by all backends
│   ├── base_detector.py           # BaseDetector ABC — context-manager + abstract detect()
│   ├── pose_detector.py           # MediaPipe backend (auto-downloads model, VIDEO mode)
│   ├── yolo_detector.py           # YOLOv8-Pose backend (COCO-17 → MP-33 slot mapping)
│   ├── detector_factory.py        # create_detector("mediapipe" | "yolo") factory
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

Edit `core/exercises_data.json` and append a new entry — no Python required:

```json
{
  "id": 33,
  "name": "My Exercise",
  "joint": ["LEFT_HIP", "LEFT_KNEE", "LEFT_ANKLE"],
  "down_max": 100,
  "up_min": 160,
  "tip": "Keep your front knee behind your toes.",
  "feedback": [
    { "angle_min": 0,   "angle_max": 100, "message": "✓ Good depth!",   "color": "#22c55e" },
    { "angle_min": 100, "angle_max": 160, "message": "↓ Go lower",       "color": "#f59e0b" },
    { "angle_min": 160, "angle_max": 180, "message": "↑ Stand up fully", "color": "#94a3b8" }
  ]
}
```

Joint names must match a constant in `core/landmarks.py` (e.g. `LEFT_HIP`, `RIGHT_ELBOW`). The button appears in the sidebar automatically.

---

## Exercise List

| # | Exercise | Category |
|---|----------|----------|
| 0 | Squat | Legs |
| 1 | Bicep Curl | Arms |
| 2 | Push-up | Push |
| 3 | Lateral Raise | Shoulders |
| 4 | Overhead Press | Shoulders |
| 5 | Tricep Extension | Arms |
| 6 | Front Raise | Shoulders |
| 7 | Lunge | Legs |
| 8 | Shoulder Tap | Core |
| 9 | Hammer Curl | Arms |
| 10 | Reverse Curl | Arms |
| 11 | Concentration Curl | Arms |
| 12 | Overhead Tricep Extension | Arms |
| 13 | Skull Crusher | Arms |
| 14 | Tricep Kickback | Arms |
| 15 | Incline Push-up | Push |
| 16 | Diamond Push-up | Push |
| 17 | Arnold Press | Shoulders |
| 18 | Upright Row | Shoulders |
| 19 | Romanian Deadlift | Hip Hinge |
| 20 | Good Morning | Hip Hinge |
| 21 | Hip Thrust | Glutes |
| 22 | Sumo Squat | Legs |
| 23 | Bulgarian Split Squat | Legs |
| 24 | Jump Squat | Plyometrics |
| 25 | Step Up | Legs |
| 26 | Mountain Climber | Cardio / Core |
| 27 | Glute Bridge | Glutes |
| 28 | Donkey Kick | Glutes |
| 29 | Bent Over Row | Pull |
| 30 | Pull-up | Pull |
| 31 | Lat Pulldown | Pull |
| 32 | Calf Raise | Legs |

---

## How It Works

```
Webcam frame
    │
    ▼
create_detector(backend)       ← factory returns MediaPipe or YOLOv8 instance
    │                             (backend toggled live from the top bar)
    ▼
BaseDetector.detect()          ← returns list[Keypoint] (33 slots, MP order)
    │                             YOLO maps COCO-17 → MP-33; missing slots = 0.0 vis
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
cv2.putText  ─────────────────► [MEDIAPIPE] or [YOLO] label stamped on frame
    │
    ▼
Qt signals ──────────────────► MainWindow slots (frame, stats, feedback)
```

> **YOLOv8 keypoint coverage**: YOLO provides 17 COCO keypoints (nose, eyes, ears, shoulders, elbows, wrists, hips, knees, ankles). Exercises that require face, finger, or toe landmarks (e.g. Calf Raise — `LEFT_FOOT_INDEX`) will show the visibility warning in YOLO mode. All 32 gym exercises work with both backends.

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
| `POSE_BACKEND` | `"mediapipe"` | Default backend at startup (`"mediapipe"` or `"yolo"`) |

---

## Dependencies

| Package | Purpose |
|---|---|
| `mediapipe` | MediaPipe Pose Landmarker backend (33 keypoints, VIDEO mode) |
| `ultralytics` | YOLOv8-Pose backend (17 COCO keypoints, auto-downloads weights) |
| `torch` / `torchvision` | PyTorch CPU runtime required by ultralytics |
| `opencv-python` | Webcam capture + frame drawing |
| `numpy` | Vector math for angle calculation |
| `PyQt6` | Desktop UI framework |

---

## License

MIT
