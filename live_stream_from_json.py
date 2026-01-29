import asyncio
import json
import sys
import time
from pathlib import Path

import websockets


"""
Simple WebSocket server that streams frames from an existing visualizer JSON
file one-by-one so we can test real-time visualization without running IK.

Playback is paced using the actual timestamps in the JSON so that, on
average, wall-clock time matches recorded time (optionally scaled by a
speed factor).

Usage:
    python live_stream_from_json.py public/samples/STS/sample_mono.json [speed]
    # then in the browser, connect to ws://localhost:8765 from the visualizer
"""


def _estimate_fps(time_array):
    if not isinstance(time_array, list) or len(time_array) < 2:
        return 60.0
    duration = time_array[-1] - time_array[0]
    if duration <= 0:
        return 60.0
    fps = (len(time_array) - 1) / duration
    # Clamp to a reasonable range
    fps = max(10.0, min(120.0, fps))
    return fps


async def stream_from_json(websocket, json_paths, speed: float = 1.0, body_style: dict | None = None):
    """
    Stream one or two visualizer JSON files over WebSocket in (optionally downsampled)
    real time.

    body_style: optional dict mapping body name -> { "visible": bool, "color": "#RRGGBB" }
    for per-body visibility and color overrides in the visualizer.

    Protocol:
      init:
        {
          "type": "init",
          "frameRate": <fps_after_downsample_and_speed>,
          "subjects": [
            { "id": "subj1", "label": "Subject 1", "bodies": { ... } },
            { "id": "subj2", "label": "Subject 2", "bodies": { ... } }
          ],
          "bodies": { ... },   // flat, first subject only (single-subject frontend compat)
          "bodyStyle": { ... } // optional per-body visibility/color
        }

      frame:
        {
          "type": "frame",
          "streams": {
            "subj1": { "time": t, "bodies": { ... } },
            "subj2": { "time": t, "bodies": { ... } }
          }
        }
    """
    if speed <= 0:
        speed = 1.0

    # Load all JSON files
    data_list = []
    for path in json_paths:
        with path.open("r", encoding="utf-8") as f:
            data_list.append(json.load(f))

    if not data_list:
        raise ValueError("No JSON data loaded")

    # Use first JSON's time as master
    master_time = data_list[0].get("time", [])
    if not isinstance(master_time, list) or not master_time:
        raise ValueError("Master JSON must contain a non-empty 'time' array")

    fps = _estimate_fps(master_time)
    print(f"Estimated FPS from master JSON: {fps:.2f}, speed factor: {speed:.2f}")

    # Basic consistency check for other subjects
    for i, data in enumerate(data_list[1:], start=2):
        t = data.get("time", [])
        if not isinstance(t, list) or not t:
            print(f"Warning: subject {i} has invalid or empty 'time' array; using master timing.")
            continue
        if len(t) != len(master_time) or abs(t[0] - master_time[0]) > 1e-3 or abs(t[-1] - master_time[-1]) > 1e-3:
            print(
                f"Warning: subject {i} time array differs from master; "
                "assuming roughly aligned and sampling by index."
            )

    # Decide downsampling to target ~30 Hz based on master timeline
    target_fps = 30.0
    num_frames = len(master_time)
    start_time = master_time[0]

    if fps <= target_fps:
        kept_indices = list(range(num_frames))
        effective_base_fps = fps
    else:
        period = 1.0 / target_fps
        kept_indices = []
        next_t = start_time
        tol = period * 0.25
        for idx, t_val in enumerate(master_time):
            if t_val + tol >= next_t:
                kept_indices.append(idx)
                next_t += period
        if kept_indices and kept_indices[-1] != num_frames - 1:
            kept_indices.append(num_frames - 1)
        duration = master_time[kept_indices[-1]] - master_time[kept_indices[0]]
        effective_base_fps = (len(kept_indices) - 1) / duration if duration > 0 else target_fps

    print(
        f"Downsampling from ~{fps:.2f} Hz to ~{effective_base_fps:.2f} Hz "
        f"({len(kept_indices)}/{num_frames} frames)"
    )

    # Build subjects metadata for init
    subjects_meta = []
    subject_ids = []
    for idx, (path, data) in enumerate(zip(json_paths, data_list), start=1):
        bodies = data.get("bodies", {})
        if not isinstance(bodies, dict) or not bodies:
            raise ValueError(f"JSON {path} must contain a non-empty 'bodies' dict")
        bodies_meta = {}
        for name, bd in bodies.items():
            bodies_meta[name] = {
                "attachedGeometries": bd.get("attachedGeometries", []),
                "scaleFactors": bd.get("scaleFactors", [1.0, 1.0, 1.0]),
            }
        # Construct a unique and stable subject id
        base_id = f"{path.parent.name}_{path.stem}" if path.parent.name else path.stem
        subject_id = base_id
        # Ensure uniqueness in case of duplicate filenames
        suffix = 2
        while subject_id in subject_ids:
            subject_id = f"{base_id}_{suffix}"
            suffix += 1
        subject_ids.append(subject_id)

        subjects_meta.append(
            {
                "id": subject_id,
                "label": path.stem,
                "bodies": bodies_meta,
            }
        )

    init_msg = {
        "type": "init",
        # Inform client about nominal frame rate (after speed scaling)
        "frameRate": effective_base_fps * speed,
        "subjects": subjects_meta,
    }
    # Single-subject frontend compatibility: send flat bodies (and bodyStyle) at top level
    if len(subjects_meta) == 1:
        init_msg["bodies"] = subjects_meta[0]["bodies"]
    if body_style:
        init_msg["bodyStyle"] = body_style
    await websocket.send(json.dumps(init_msg))

    # Give the client a brief moment to load meshes
    await asyncio.sleep(1.0)

    # Stream frames in a loop; when we reach the end, loop again.
    # We use the master timeline to pace playback against wall-clock time.
    while True:
        loop_start_wall = time.perf_counter()
        for frame_idx in kept_indices:
            # Target elapsed time (recorded) scaled by speed factor
            recorded_t = master_time[frame_idx] - start_time
            target_elapsed = recorded_t / speed

            # How much time has passed in wall-clock since this loop started
            now_elapsed = time.perf_counter() - loop_start_wall
            delay = target_elapsed - now_elapsed
            if delay > 0:
                await asyncio.sleep(delay)

            t_val = master_time[frame_idx]

            # Build per-subject streams using the same subject ids as in init
            streams = {}
            for subject_id, data in zip(subject_ids, data_list):
                bodies = data.get("bodies", {})
                frame_bodies = {}
                for name, bd in bodies.items():
                    rotations = bd.get("rotation", [])
                    translations = bd.get("translation", [])
                    if frame_idx >= len(rotations) or frame_idx >= len(translations):
                        continue
                    frame_bodies[name] = {
                        "rotation": rotations[frame_idx],
                        "translation": translations[frame_idx],
                    }
                streams[subject_id] = {
                    "time": t_val,
                    "bodies": frame_bodies,
                }

            frame_msg = {
                "type": "frame",
                "streams": streams,
            }
            await websocket.send(json.dumps(frame_msg))


def _parse_body_style(arg: str) -> dict | None:
    """Parse --body-style: either a path to a JSON file or inline JSON string."""
    if not arg or not arg.strip():
        return None
    arg = arg.strip()
    # Inline JSON: try parse first to avoid path.is_file() on long strings (OS "file name too long")
    if arg.startswith("{"):
        try:
            return json.loads(arg)
        except json.JSONDecodeError:
            print(f"Invalid body-style JSON: {arg[:60]}...")
            return None
    path = Path(arg)
    if path.is_file():
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    try:
        return json.loads(arg)
    except json.JSONDecodeError:
        print(f"Invalid body-style (not a file or JSON): {arg[:60]}...")
        return None


async def main():
    if len(sys.argv) < 2:
        print(
            "Usage: python live_stream_from_json.py path/to/sample1.json [path/to/sample2.json] [speed] [--body-style PATH|JSON]"
        )
        sys.exit(1)

    args = sys.argv[1:]
    # Extract --body-style if present
    body_style = None
    if "--body-style" in args:
        idx = args.index("--body-style")
        if idx + 1 < len(args):
            body_style = _parse_body_style(args[idx + 1])
            args = args[:idx] + args[idx + 2 :]
        else:
            args = args[:idx] + args[idx + 1 :]

    json_args = [a for a in args if a.lower().endswith(".json")]
    other_args = [a for a in args if not a.lower().endswith(".json")]

    if not json_args:
        print("Error: at least one JSON file path is required")
        sys.exit(1)

    # Support up to two subjects
    json_paths = [Path(p).resolve() for p in json_args[:2]]
    for p in json_paths:
        if not p.is_file():
            print(f"JSON file not found: {p}")
            sys.exit(1)

    # Optional speed multiplier: >1.0 = faster than recorded, <1.0 = slower
    speed = 1.0
    if other_args:
        try:
            speed = float(other_args[-1])
        except ValueError:
            print(f"Invalid speed '{other_args[-1]}', using 1.0")
            speed = 1.0

    async def handler(websocket):
        print(f"Client connected from {websocket.remote_address}")
        try:
            await stream_from_json(websocket, json_paths, speed, body_style=body_style)
        except Exception as e:
            print(f"Error during streaming: {e}")
        finally:
            print("Client disconnected")

    print(f"Streaming from {[str(p) for p in json_paths]}")
    print("WebSocket server listening on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
