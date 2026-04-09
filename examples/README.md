# Example Workflows

This file lists the concrete example workflows that are currently available from this repository.

## 1. Motion + Markers + GRF + Browser Video

Status: supported in the web app

Start the app:

```bash
npm install
npm run serve
```

Open `http://localhost:3001`, then load these files together:

- `public/samples/default/sample.json`
- `public/samples/default/sample_markers.trc`
- `public/samples/default/sample_forces.mot`

What this gives you:

- motion from the JSON
- marker spheres from the TRC
- force arrows from the MOT

To export a video, use the **Record** button in the right sidebar.

## 2. Real-Time Playback By Parsing An Existing JSON

Status: supported by the repo-local script

Install the dependency:

```bash
python -m pip install websockets
```

Replay one JSON file in real time:

```bash
python live_stream_from_json.py public/samples/walk/sample_mono.json
```

Replay two JSON files at once:

```bash
python live_stream_from_json.py \
  public/samples/walk/sample_mono.json \
  public/samples/walk/sample_wham.json
```

Then in the browser:

1. Open the visualizer.
2. Expand **Live IK Stream**.
3. Connect to `ws://localhost:8765`.

Labels come from the JSON filename stem. For example, `sample_mono.json` appears as `sample_mono`.

## 3. Continuous Video Of Multiple Trials With Labels

Status: not yet included as a repo-local script

What exists today:

- You can load multiple trials together in the browser.
- You can rename each loaded trial in the sidebar.
- You can record the current browser scene.
- Live-stream subject labels come from the input filenames.

What is missing today:

- a repo-local script that concatenates many trials into one continuous labeled output video

Recommended current workaround:

1. Render trials individually with the separate PyPI package.
2. Concatenate the output videos afterward with your video tool of choice.

Or, if you only need an interactive comparison:

1. Load multiple JSON files into the browser.
2. Rename the trials in the sidebar.
3. Record the scene from the browser.
