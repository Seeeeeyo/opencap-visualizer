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

Then open the visualizer, expand **Live IK Stream**, and connect to `ws://localhost:8765`.

## Browser Features Confirmed In This Repo

- Multi-subject overlays with editable trial names
- Marker visualization
- Ground reaction force visualization
- Synced reference video overlay
- Screenshot export
- Browser recording to WebM or MP4 when supported by the browser
- Timelapse mode
- Shared visualization files/URLs
- Live WebSocket controls for camera, visibility, notifications, and trial scores

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
