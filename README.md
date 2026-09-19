# OpenCap Visualizer

OpenCap Visualizer is a Vue.js + Three.js web app for viewing biomechanics data in 3D. This repository contains the browser visualizer, sample data, and a repo-local WebSocket script for replaying an existing visualizer JSON in real time.

It supports OpenCap-style `.json`, markers `.trc`, ground-reaction-force `.mot`, OpenSim `.osim` + motion `.mot`, synced video, screenshots, browser recording, timelapse, sharing, and live WebSocket playback.

## Links

- Web app: [https://www.visualizer.opencap.ai/](https://www.visualizer.opencap.ai/)
- Paper: [paper/paper.md](paper/paper.md)
- PyPI package: [https://pypi.org/project/opencap-visualizer/](https://pypi.org/project/opencap-visualizer/)
- Python package source: [https://github.com/Seeeeeyo/opencap-visualizer-pip](https://github.com/Seeeeeyo/opencap-visualizer-pip)
- OpenSim converter: [https://github.com/Seeeeeyo/opensim-to-visualizer-api](https://github.com/Seeeeeyo/opensim-to-visualizer-api)
- Share backend: [share-backend/README.md](share-backend/README.md)

## What Is In This Repo

- The web visualizer in `src/`
- Sample datasets in `public/samples/`
- A repo-local live stream helper: [`live_stream_from_json.py`](live_stream_from_json.py)
- An embed demo: [`public/embed-demo.html`](public/embed-demo.html)

The packaged Python video renderer lives in a separate repository. To avoid drift, package CLI and API details should be taken from PyPI and the package repo rather than duplicated here.

## Quick Start

```bash
npm install
npm run serve
```

Then open `http://localhost:3001`.

## Supported Inputs

- `.json` visualizer motion files
- `.trc` marker trajectories
- `.mot` force files
- `.osim` + motion `.mot`
- `.mp4` and `.webm` reference videos
- `.pkl` / `.pickle` SMPL or skeleton sequences via drag-and-drop

## Example Workflows

The short version is:

- Motion + markers + GRF + recorded browser video: yes
- Real-time playback from an existing JSON: yes
- Continuous labeled video across multiple trials: not yet as a repo-local script

See [examples/README.md](examples/README.md) for concrete examples.

## Live Streaming From An Existing JSON

Install the one repo-local dependency:

```bash
python -m pip install websockets
```

Replay one subject:

```bash
python live_stream_from_json.py public/samples/walk/sample_mono.json
```

Replay two subjects:

```bash
python live_stream_from_json.py \
  public/samples/walk/sample_mono.json \
  public/samples/walk/sample_wham.json
```

Replay at a fixed low stream rate to test live-view smoothing:

```bash
python live_stream_from_json.py public/samples/walk/sample_mono.json --stream-hz 6
```

Show a repetition counter in the viewer (current/total, e.g. `3/10`):

```bash
python live_stream_from_json.py public/samples/walk/sample_mono.json --rep 3 --reps 10
```

Then open the visualizer, expand **Live IK Stream**, and connect to `ws://localhost:8765`.

### Live SMPL mesh (fixed shape, pose-only)

Local files you can use:

| File | Use |
|------|-----|
| `test/STS1_optimized.pkl` | Small SMPL sequence (~600 KB) — recommended for live mesh replay |
| `test/wham_output.pkl` | Full WHAM output (~100 MB) — slow to load |
| `public/samples/walk/sample_mono.json` | OpenSim bodies only (segment meshes, not SMPL) |

Protocol smoke test (no SMPL/torch; animated tetrahedron):

```bash
python live_stream_from_smpl.py --demo
```

Replay real SMPL mesh from the small local pickle (needs `smpl_service` deps: `pip install -r smpl_service/requirements.txt`):

```bash
python live_stream_from_smpl.py test/STS1_optimized.pkl
```

Or evaluate the pickle via a running SMPL API, then stream:

```bash
cd smpl_service && uvicorn main:app --port 8000
# other terminal:
python -m pip install requests
python live_stream_from_smpl.py test/STS1_optimized.pkl --api-url http://127.0.0.1:8000
```

Use the same **Live IK Stream** panel and `ws://localhost:8765`. Playback starts automatically after `init`.

### Live MHR mesh (Momentum Human Rig / SAM 3D Body)

[MHR](https://github.com/facebookresearch/MHR) is the parametric body model used by Meta [SAM 3D Body](https://huggingface.co/facebook/sam-3d-body-dinov3) and visualized in [sam3d-body-rerun](https://github.com/rerun-io/sam3d-body-rerun). This path is separate from SMPL.

Protocol smoke test (no MHR/torch; animated icosahedron):

```bash
python live_stream_from_mhr.py --demo
```

Replay from an `.npz` with `model_parameters` / `mhr_params` (204,) and `shape_params` / `identity_coeffs` (45,), or precomputed `pred_vertices`:

```bash
export MHR_ASSETS=/path/to/mhr/assets   # mhr_model.pt from MHR release
pip install -r mhr_service/requirements.txt
python live_stream_from_mhr.py path/to/mhr_motion.npz
```

Or evaluate via running MHR API:

```bash
uvicorn main:app --app-dir mhr_service --port 8001
python live_stream_from_mhr.py path/to/mhr_motion.npz --api-url http://127.0.0.1:8001
```

WebSocket protocol uses `mhrSubjects` on `init` and `mhrStreams` on each `frame` (template vertices + faces, then per-frame vertices).

Notes:

- By default, the helper follows the JSON timestamps and caps playback near 30 Hz.
- `--stream-hz <value>` down-samples the source JSON and emits frames at a fixed wall-clock cadence, which is useful for testing sparse live streams such as `6 Hz`.
- `--rep <current> --reps <total>` shows a repetition counter overlay in the viewer as `current/total` (e.g. `3/10`). Both flags are required together; also supported by `live_stream_from_smpl.py` and `live_stream_from_mhr.py`.
- In live mode, **Low-latency motion smoothing** is enabled by default. The viewer eases motion at display refresh rate and predicts at most half of one observed stream interval beyond the newest pose, avoiding a delayed frame buffer while smoothing 20–30 Hz input.
- Disable **Low-latency motion smoothing** in the Live IK Stream panel to render each received pose directly.
- The **Live IK Stream** panel shows the observed stream rate in Hz, and when available also shows the nominal rate reported by the sender.

### Live Repetition Counter

Optional overlay in the top-right of the live viewer showing the current and total repetitions as `#/#`.

CLI (include both flags):

```bash
python live_stream_from_json.py subject.json --rep 3 --reps 10
```

On `init`, the streamer can include:

```json
{
  "type": "init",
  "repetition": { "current": 3, "total": 10 }
}
```

Update or hide while streaming:

```json
{ "type": "repetition", "current": 4, "total": 10 }
```

```json
{ "type": "hideRepetition" }
```

Interactive stdin commands with the JSON helper:

```bash
reps 4 10
hidereps
```

### Live 3D Target

The live viewer can show a scene-fixed target object. In the **Live IK Stream** panel, the user can manually enable the target and set its object type, size, position, and rotation.

Programmatic updates can be sent on `init`, on any `frame`, inside a subject stream, or as a standalone WebSocket message:

```json
{
  "type": "target",
  "target": {
    "objectType": "sphere",
    "size": 0.15,
    "position": [0.5, 1.0, 0],
    "rotation": [0, 0, 0],
    "color": "#ff3b30",
    "opacity": 0.9
  }
}
```

Supported object types are `sphere`, `box`, `cylinder`, and `ring`. `size` is in meters, `position` is `[x, y, z]` from the scene origin, and `rotation` is in degrees. The target stays at that world position while the body moves. To change the target color during a trial, send another target update with a new `color` value, for example:

```json
{ "type": "target", "target": { "color": "#2ecc71" } }
```

The target keeps its previous size, shape, position, and rotation unless those fields are included in the update. Hide it with:

```json
{ "type": "target", "target": { "visible": false } }
```

With `live_stream_from_json.py`, you can use the helpers directly:

```python
from live_stream_from_json import send_target, send_target_update, hide_target

await send_target(object_type="box", size=0.2, position=[0.5, 1.0, 0], color="#2ecc71")
await send_target_update(color="#ffcc00")
await hide_target()
```

### Live Notification Messages

The live WebSocket notification message accepts:

- `message`: single banner text; `\n` renders as a line break within one banner
- `messages`: array of strings, each shown as a separate stacked banner
- `level`: `info`, `success`, `warning`, or `error`
- `duration`: milliseconds, with `0` meaning until dismissed
- `fontSize`: optional font size for the banner text, such as `32`, `"32px"`, or `"1.8rem"`
- `append`: when `true`, add banners without clearing existing ones

Single banner with line breaks:

```json
{
  "type": "notification",
  "message": "1. Extend your elbow\n2. Don't shrug your shoulder",
  "level": "info",
  "duration": 0
}
```

Stacked banners:

```json
{
  "type": "notification",
  "messages": ["1. Extend your elbow", "2. Don't shrug your shoulder"],
  "level": "info",
  "duration": 0
}
```

Raw WebSocket example:

```json
{
  "type": "notification",
  "message": "Great job!",
  "level": "success",
  "duration": 5000,
  "fontSize": "32px"
}
```

If you are using the repo-local helper script interactively, you can also send:

```bash
notify info 1. Extend your elbow\n2. Don't shrug your shoulder
notify-stack info 1. Extend your elbow || 2. Don't shrug your shoulder
notify success size=32 Great technique!
target {"objectType":"box","size":0.2,"position":[0.5,1.0,0],"color":"#2ecc71"}
target {"color":"#ffcc00"}
target off
panels 2 anterior sagittal_right
panels 4 anterior sagittal_right superior posterior
```

### Live Camera Controls

The visualizer supports **1–4 simultaneous camera panels** (split view). In the UI, use the **Views** picker in **Scene Settings** or **Live IK Stream** to choose 1, 2, 3, or 4 panels. Each panel has its own orbit controls and cube gizmo.

Over WebSocket you can set the **primary camera only** (legacy) or **each panel independently**.

#### Single camera (panel 0)

Preset:

```json
{ "type": "camera", "camera": "anterior" }
```

Or with a `view` field:

```json
{ "type": "camera", "camera": { "view": "sagittal_right" } }
```

Exact position + look-at target:

```json
{
  "type": "camera",
  "camera": {
    "position": [3, 2, -4],
    "target": [0, 1, 0]
  }
}
```

#### Camera `up` vector (screen orientation / rotation)

Any camera spec can include an optional `"up"` field — a world-space vector that controls which direction faces the **top of the screen**. This is especially useful for top-down (`superior`) and bottom-up (`inferior`) views, where there is no single natural "up" and the default orientation may not match your data.

| `"up"` value | Screen-top points toward |
|---|---|
| `[1, 0, 0]` | Subject's anterior / front (+X) |
| `[-1, 0, 0]` | Subject's posterior / back (−X) |
| `[0, 0, 1]` | Subject's right side (+Z) |
| `[0, 0, -1]` | Subject's left side (−Z) |

Named preset with `up` override:

```json
{ "type": "camera", "camera": { "view": "superior", "up": [1, 0, 0] } }
```

Full position + target + up control:

```json
{
  "type": "camera",
  "camera": {
    "position": [0, 5, 0],
    "target": [0, 1, 0],
    "up": [1, 0, 0]
  }
}
```

On stream start, pass `--camera` to `live_stream_from_json.py`:

```bash
python live_stream_from_json.py subject.json --camera anterior
python live_stream_from_json.py subject.json --camera '{"position": [3, 2, -4], "target": [0, 1, 0]}'
# Top-down view with the subject's front (+X) facing screen-top:
python live_stream_from_json.py subject.json --camera '{"view": "superior", "up": [1, 0, 0]}'
```

#### Multi-panel split view (1–4 panels)

Send `splitViewCount` (optional; defaults to `panels.length`) and a `panels` array. Each entry is either:

- a **preset string** (e.g. `"anterior"`), or
- `{ "view": "..." }` for a named preset, or
- `{ "position": [x, y, z], "target": [x, y, z] }` for an exact camera pose (`target` defaults to `[0, 1, 0]`)

Any entry can also include `"up": [x, y, z]` to set the screen-top orientation for that panel.

Two panels side by side:

```json
{
  "type": "camera",
  "splitViewCount": 2,
  "panels": ["anterior", "sagittal_right"]
}
```

Four panels (2×2 grid) with mixed preset types:

```json
{
  "type": "camera",
  "splitViewCount": 4,
  "panels": [
    "anterior",
    { "view": "sagittal_right" },
    "superior",
    {
      "position": [3, 2, -4],
      "target": [0, 1, 0]
    }
  ]
}
```

Set panels on **`init`** (applied when the stream starts):

```json
{
  "type": "init",
  "frameRate": 30,
  "subjects": [...],
  "splitViewCount": 2,
  "panels": ["anterior", "sagittal_left"]
}
```

Update panels mid-stream with a standalone `camera` message (same `panels` / `splitViewCount` fields).

#### Preset names

| Category | Names |
|----------|--------|
| Anatomical (OpenCap) | `anterior`, `posterior`, `sagittal_right`, `sagittal_left`, `superior`, `inferior` |
| Axis-aligned | `front`, `back`, `left`, `right`, `top`, `bottom` |
| Corner / isometric | `frontTopRight`, `frontTopLeft`, `frontBottomRight`, `frontBottomLeft`, `backTopRight`, `backTopLeft`, `backBottomRight`, `backBottomLeft`, `isometric`, `default` |

#### Python helpers (`live_stream_from_json.py`)

```python
from live_stream_from_json import send_camera, send_camera_panels

# Primary camera only
await send_camera("anterior")
await send_camera({"position": [3, 2, -4], "target": [0, 1, 0]})
# Top-down with subject's front facing screen-top:
await send_camera({"view": "superior", "up": [1, 0, 0]})

# Multi-panel
await send_camera_panels(["anterior", "sagittal_right"], split_view_count=2)
await send_camera_panels(
    ["anterior", "sagittal_right", "superior", "posterior"],
    split_view_count=4,
)
# Panel with up override:
await send_camera_panels(
    [{"view": "superior", "up": [1, 0, 0]}, "anterior"],
    split_view_count=2,
)
```

While the stream server is running, type interactive commands in its terminal:

```bash
camera anterior
camera {"position":[3,2,-4],"target":[0,1,0]}
camera {"view":"superior","up":[1,0,0]}
panels 2 anterior sagittal_right
panels 4 anterior sagittal_right superior posterior
panels [{"view":"anterior"},{"view":"sagittal_right"}]
panels [{"view":"superior","up":[1,0,0]},{"view":"anterior"}]
```

## Browser Features Confirmed In This Repo

- Multi-subject overlays with editable trial names
- Marker visualization
- Ground reaction force visualization
- Synced reference video overlay
- Screenshot export
- Browser recording to WebM or MP4 when supported by the browser
- Timelapse mode
- Shared visualization files/URLs
- Live WebSocket controls for camera (including per-panel split view), visibility, notifications, trial scores, repetition counts, and 3D targets
- Split-view camera layout (1, 2, 3, or 4 panels) in the UI and over WebSocket

## Notes On The Python Package

The paper discusses a separate pip package for automated rendering. That package is real, but it is not implemented in this repository.

Current package docs:

- PyPI: [https://pypi.org/project/opencap-visualizer/](https://pypi.org/project/opencap-visualizer/)
- Source: [https://github.com/Seeeeeyo/opencap-visualizer-pip](https://github.com/Seeeeeyo/opencap-visualizer-pip)

## Development

```bash
npm install
npm run serve
npm run build
```

<!-- ## License

MIT. See [LICENSE.md](LICENSE.md). -->

### Livestream capture camera

Enable **Capture camera (iPhone)** in the livestream panel to place a physical
phone in the scene. Position uses world coordinates in meters, independently of
the pelvis. Rotation is XYZ Euler angles in degrees. At zero rotation the phone
is upright (+Y), its rear lens points toward +Z, and its round lens is at the
upper left when looking at the back. The phone is sized like an iPhone 12
(71.5 × 146.7 × 7.4 mm).

Stream its pose together with existing bodies by adding `captureCamera` to an
`init` or `frame` message (the `streams`/`bodies` payload stays the same):

```json
{"type":"frame","captureCamera":{"position":[0,1.5,2],"rotation":[0,180,0]},"streams":{}}
```

A standalone update is also supported:

```json
{"type":"captureCamera","captureCamera":{"position":[1,1.5,2],"rotation":[0,180,0]}}
```

Unspecified pose fields retain their values. `rotationRadians` is supported as
an alternative to `rotation`; `captureCamera: null` or `{"visible":false}` hides
the phone. The viewer-side **Capture camera (iPhone)** toggle can also hide the
phone locally; incoming stream messages keep updating the saved pose but do not
force the phone visible again until the toggle is turned back on. Existing
`camera` messages still control the viewer viewpoint.

For the JSON streamer, pass a fixed pose:

```sh
python live_stream_from_json.py motion.json --capture-camera '{"position":[0,1.5,2],"rotation":[0,180,0]}'
```

Alternatively, add `captureCamera` to the first motion JSON as either one pose
object or an array of pose objects aligned to the original body frames. The
streamer sends the corresponding poses alongside the bodies, including when
frames are downsampled. The CLI pose overrides poses in the file. Python callers
can use `await send_capture_camera(position=[0,1.5,2], rotation=[0,180,0])`.
