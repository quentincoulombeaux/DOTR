# DOTR — Drone Over The Ring

Computer-vision and control code for a **DJI Tello** drone whose goal is to fly through a course of gates ("rings"). The project is an ESEO engineering-school industrial project and is split into two independent parts:

1. **Keyboard tele-operation** of the Tello drone (French `ZQSD` layout), with an optional live first-person video view.
2. **Gate detection** based on [Ultralytics YOLO](https://docs.ultralytics.com/): two models detect circular gates (`hoop`) and hexagonal gates (`hexagon`) in a video file or a live camera stream.

> The two parts currently run separately: flight is fully manual, and detection runs on recorded or webcam video. Coupling detection to autonomous flight is a natural next step but is **not** implemented in the current scripts.

## Repository structure

```
DOTR/
├── zqsd_drone.py            # Keyboard control of the Tello (movement only)
├── zqsd_camera_drone.py     # Keyboard control + live video POV (Pygame) + battery overlay
├── hoop_detection/
│   ├── train.py             # Train a YOLOv8n model from scratch
│   ├── train2.py            # Train a YOLO11n model
│   ├── config.yaml          # Dataset config (1 class: "hoop")
│   ├── predict_hoop.py      # Detect gates in a video file → annotated output video
│   ├── predict_hoop_live.py # Detect gates on a live webcam feed
│   └── requirements.txt     # ultralytics==8.0.23
└── runs/detect/train*/      # YOLO training outputs (weights, curves, metrics)
```

## Requirements

Python 3.x. The bundled `hoop_detection/requirements.txt` only pins `ultralytics==8.0.23`; the drone-control scripts need extra packages. Full set:

```bash
pip install ultralytics==8.0.23 djitellopy pynput pygame opencv-python
```

| Feature | Packages used |
|---|---|
| Drone control (`zqsd_drone.py`) | `djitellopy`, `pynput` |
| Drone control + camera POV (`zqsd_camera_drone.py`) | `djitellopy`, `pynput`, `pygame`, `opencv-python` |
| Training & inference (`hoop_detection/`) | `ultralytics` (pulls in PyTorch, OpenCV) |

## Drone control

Connect your computer to the Tello's Wi-Fi network, then run one of:

```bash
python zqsd_drone.py          # movement only
python zqsd_camera_drone.py   # movement + live video window
```

Keyboard mapping:

| Key | Action | Key | Action |
|---|---|---|---|
| `Z` | Forward | `A` | Up |
| `S` | Backward | `E` | Down |
| `Q` | Left | `O` | Take off / land |
| `D` | Right | `T` | Print battery *(`zqsd_drone.py` only)* |

In `zqsd_camera_drone.py`, `DRONE_SPEED` (10–100) and `DRONE_MOVE` (step size, in cm) are set at the top of the file; the battery level is refreshed every 10 s and drawn on the video window.

## Gate detection

### Training

`config.yaml` defines a single class (`hoop`) and the dataset paths. **Edit the absolute paths** in `config.yaml` (and in `train.py`, which hard-codes the path to `config.yaml`) to match your machine, then:

```bash
python hoop_detection/train.py    # YOLOv8n, 50 epochs
python hoop_detection/train2.py   # YOLO11n, 50 epochs
```

Outputs (weights, PR/F1 curves, confusion matrix, `results.csv`) are written to `runs/detect/trainN/`.

### Inference

Both prediction scripts load two trained models and draw `HOOP` boxes in blue and `HEXAGON` boxes in red, suppressing a hoop when it overlaps a hexagon too closely (area difference < 30 % **and** IoU ≥ 0.7).

```bash
python hoop_detection/predict_hoop.py       # process a video file, write annotated .mp4
python hoop_detection/predict_hoop_live.py  # process the default webcam (press ESC to quit)
```

Default model paths used by both scripts:

- Hoop model: `runs/detect/train9/weights/last.pt`
- Hexagon model: `runs/detect/train5/weights/last.pt`

`predict_hoop.py` also expects an input video (default `videos/hexagon/video_test2.mp4`) that is **not** included in this repository — update `input_video_path` / `output_video_path` accordingly. Confidence threshold: `0.83` (file) / `0.8` (live).

### Reported performance

Final validation metrics after 50 epochs, as recorded in `results.csv`:

| Model | Run | mAP@50 | mAP@50-95 |
|---|---|---|---|
| Hoop | `train9` | 0.995 | 0.992 |
| Hexagon | `train5` | 0.995 | 0.992 |

> **Caveat:** in `config.yaml` the validation set points to the **same folder as the training set** (`val` = `train`). The metrics above are therefore measured on training data and are optimistic — evaluate on a held-out validation set for a realistic estimate.

## Notes & limitations

- Several paths are hard-coded absolute Windows paths (`config.yaml`, `train.py`) — change them for your environment.
- The dataset and the test videos used for inference are not part of this repository.
- Trained weights and full training artifacts (~196 MB) are committed under `runs/`.
- Requires a DJI Tello (or Tello EDU) drone for the control scripts.
