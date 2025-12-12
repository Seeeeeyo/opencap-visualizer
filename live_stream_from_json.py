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


async def stream_from_json(websocket, json_path: Path, speed: float = 1.0):
    # Load JSON once
    with json_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    time_array = data.get("time", [])
    bodies = data.get("bodies", {})

    if not isinstance(time_array, list) or not time_array:
        raise ValueError("JSON must contain a non-empty 'time' array")
    if not isinstance(bodies, dict) or not bodies:
        raise ValueError("JSON must contain a non-empty 'bodies' dict")

    fps = _estimate_fps(time_array)
    if speed <= 0:
        speed = 1.0
    print(f"Estimated FPS from JSON: {fps:.2f}, speed factor: {speed:.2f}")

    # Decide downsampling to target ~30 Hz
    target_fps = 30.0
    num_frames = len(time_array)
    start_time = time_array[0]

    if fps <= target_fps:
        kept_indices = list(range(num_frames))
        effective_base_fps = fps
    else:
        period = 1.0 / target_fps
        kept_indices = []
        next_t = start_time
        tol = period * 0.25
        for idx, t in enumerate(time_array):
            if t + tol >= next_t:
                kept_indices.append(idx)
                next_t += period
        if kept_indices and kept_indices[-1] != num_frames - 1:
            kept_indices.append(num_frames - 1)
        duration = time_array[kept_indices[-1]] - time_array[kept_indices[0]]
        effective_base_fps = (len(kept_indices) - 1) / duration if duration > 0 else target_fps

    print(
        f"Downsampling from ~{fps:.2f} Hz to ~{effective_base_fps:.2f} Hz "
        f"({len(kept_indices)}/{num_frames} frames)"
    )

    # Build init message: geometry + scale factors only
    init_bodies = {}
    for name, bd in bodies.items():
        init_bodies[name] = {
            "attachedGeometries": bd.get("attachedGeometries", []),
            "scaleFactors": bd.get("scaleFactors", [1.0, 1.0, 1.0]),
        }

    init_msg = {
        "type": "init",
        # Inform client about nominal frame rate (after speed scaling)
        "frameRate": effective_base_fps * speed,
        "bodies": init_bodies,
    }
    await websocket.send(json.dumps(init_msg))

    # Give the client a brief moment to load meshes
    await asyncio.sleep(1.0)

    # Stream frames in a loop; when we reach the end, loop again.
    # We use the recorded timestamps to pace playback against wall-clock time.
    while True:
        loop_start_wall = time.perf_counter()
        for frame_idx in kept_indices:
            # Target elapsed time (recorded) scaled by speed factor
            recorded_t = time_array[frame_idx] - start_time
            target_elapsed = recorded_t / speed

            # How much time has passed in wall-clock since this loop started
            now_elapsed = time.perf_counter() - loop_start_wall
            delay = target_elapsed - now_elapsed
            if delay > 0:
                await asyncio.sleep(delay)

            t = time_array[frame_idx]

            frame_bodies = {}
            for name, bd in bodies.items():
                rotations = bd.get("rotation", [])
                translations = bd.get("translation", [])

                # Guard against badly-formed data
                if frame_idx >= len(rotations) or frame_idx >= len(translations):
                    continue

                frame_bodies[name] = {
                    "rotation": rotations[frame_idx],
                    "translation": translations[frame_idx],
                }

            frame_msg = {
                "type": "frame",
                "time": t,
                "bodies": frame_bodies,
            }
            await websocket.send(json.dumps(frame_msg))


async def main():
    if len(sys.argv) < 2:
        print("Usage: python live_stream_from_json.py path/to/sample.json [speed]")
        sys.exit(1)

    json_path = Path(sys.argv[1]).resolve()
    if not json_path.is_file():
        print(f"JSON file not found: {json_path}")
        sys.exit(1)

    # Optional speed multiplier: >1.0 = faster than recorded, <1.0 = slower
    speed = 1.0
    if len(sys.argv) >= 3:
        try:
            speed = float(sys.argv[2])
        except ValueError:
            print(f"Invalid speed '{sys.argv[2]}', using 1.0")
            speed = 1.0

    async def handler(websocket):
        print(f"Client connected from {websocket.remote_address}")
        try:
            await stream_from_json(websocket, json_path, speed)
        except Exception as e:
            print(f"Error during streaming: {e}")
        finally:
            print("Client disconnected")

    print(f"Streaming from {json_path}")
    print("WebSocket server listening on ws://localhost:8765")
    async with websockets.serve(handler, "localhost", 8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    asyncio.run(main())
