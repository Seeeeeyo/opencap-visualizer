import asyncio
import copy
import json
import socket
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

Usage (single subject):
    python live_stream_from_json.py subject.json [speed]

Usage (two subjects):
    python live_stream_from_json.py subject1.json subject2.json [speed]

Coloring options:
    # Uniform color per subject
    --subject-colors "#d3d3d3,#4995e0"

    # Whole-model transparency per subject (0=invisible, 1=opaque)
    --subject-opacity 0.5,0.8

    # Same per-bone style applied to both subjects
    --body-style '{"pelvis": {"color": "#ff0000"}, "femur_r": {"color": "#00ff00"}}'

    # Different per-bone styles for each subject (JSON array, one dict per subject)
    --body-style '[{"pelvis": {"color": "#ff0000"}}, {"pelvis": {"color": "#0000ff"}}]'

Camera options:
    # Anatomical presets (recommended for OpenCap data):
    #   anterior       – facing the subject's front
    #   posterior      – behind the subject
    #   sagittal_right – subject's right side
    #   sagittal_left  – subject's left side
    #   superior       – looking down from above
    #   inferior       – looking up from below
    --camera anterior

    # Generic axis presets: front | back | left | right | top | bottom | isometric | default
    #   corner views:   frontTopRight | frontTopLeft | backTopRight | backTopLeft | ...
    --camera front

    # Exact position + look-at target (meters)
    --camera '{"position": [3, 2, -4], "target": [0, 1, 0]}'

Model options:
    # Single model for all subjects (folder_name from the visualizer model list)
    --model LaiArnold
    --model Hu_ISB_shoulder

    # Different model per subject (comma-separated, one per subject)
    --model "LaiArnold,Hu_ISB_shoulder"

Interactive commands (type while the server is running):
    notify Good job!                  → info banner on the visualizer
    notify success Great technique!   → colored banner (info/success/warning/error)
    scores 85 72 90 68 88 [label1 ...] → show trial scores (optional 5 labels after the 5 numbers)
    hidescores                        → hide the trial scores plot
    hide subject_0                    → hide a subject
    show subject_0                    → show a subject
    help                              → list all commands

Then in the browser connect to ws://localhost:8765 from the visualizer.

Same WiFi (stream on one computer, view on another):
  The server binds to all interfaces (0.0.0.0). On the streaming machine, run this script;
  on the viewing machine open the visualizer and set WebSocket URL to ws://<streaming-IP>:8765
  (e.g. ws://192.168.1.50:8765). If you use https://visualizer.opencap.ai, browsers block
  ws:// (mixed content); run the visualizer locally (npm run serve) on the viewing machine
  and use the ws:// URL there, or use a tunnel (e.g. ngrok) for wss://.
"""

DEFAULT_JSON_PATH = Path(__file__).parent / "mono.json"

# ---------------------------------------------------------------------------
# Connected clients registry – lets helper functions reach all open sockets
# ---------------------------------------------------------------------------
_CONNECTED_CLIENTS: set = set()


async def send_notification(message: str, level: str = "info", duration: int = 5000):
    """
    Show a notification banner on every connected visualizer client.

    level    : "info" | "success" | "warning" | "error"
    duration : how long (ms) the banner stays visible (0 = until dismissed)

    Can also be called programmatically when embedding this script:
        asyncio.run(send_notification("Great job!", level="success"))
    """
    msg = json.dumps({"type": "notification", "message": message, "level": level, "duration": duration})
    for ws in list(_CONNECTED_CLIENTS):
        try:
            await ws.send(msg)
        except Exception:
            pass


async def send_subject_visibility(subject_id: str, visible: bool):
    """
    Hide or show a subject on every connected visualizer client.

    subject_id : the subject ID used in the init message (e.g. "subject_0")
    visible    : True to show, False to hide
    """
    msg = json.dumps({"type": "subjectVisibility", "subjectId": subject_id, "visible": visible})
    for ws in list(_CONNECTED_CLIENTS):
        try:
            await ws.send(msg)
        except Exception:
            pass


async def send_trial_scores(scores: list, labels: list | None = None):
    """
    Show the trial scores plot on every connected visualizer client.

    scores : list of 5 numbers (0–100, percentages)
    labels : optional list of 5 strings for bar labels
    """
    msg = {"type": "trialScores", "scores": scores[:5]}
    if labels:
        msg["labels"] = labels[:5]
    for ws in list(_CONNECTED_CLIENTS):
        try:
            await ws.send(json.dumps(msg))
        except Exception:
            pass


async def send_hide_scores():
    """Hide the trial scores plot on every connected visualizer client."""
    msg = json.dumps({"type": "hideScores"})
    for ws in list(_CONNECTED_CLIENTS):
        try:
            await ws.send(msg)
        except Exception:
            pass


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


async def stream_from_json(
    websocket,
    json_paths,
    speed: float = 1.0,
    body_style: dict | None = None,
    subject_colors: list[str] | None = None,
    subject_opacity: list[float] | None = None,
    camera: "dict | str | None" = None,
    models: "list[str] | None" = None,
):
    """
    Stream one or two visualizer JSON files over WebSocket in (optionally downsampled)
    real time.

    body_style: flat dict  { bodyName: { "visible": bool, "color": "#RRGGBB" } } applied to every
                subject, OR a JSON array [ {subject1 styles}, {subject2 styles} ] for per-subject
                per-bone control.
    subject_colors: list of hex color strings, one per subject (e.g. ["#d3d3d3", "#4995e0"]).
                    Colors every bone of that subject uniformly. Takes priority over body_style.
    subject_opacity: list of floats 0-1, one per subject (e.g. [0.5, 0.8]). Whole-model transparency.

    Protocol:
      init:
        {
          "type": "init",
          "frameRate": <fps_after_downsample_and_speed>,
          "subjects": [
            { "id": "subj1", "label": "Subject 1", "bodies": { ... }, "bodyStyle": { ... } },
            { "id": "subj2", "label": "Subject 2", "bodies": { ... }, "bodyStyle": { ... } }
          ],
          "bodies": { ... },   // flat, first subject only (single-subject frontend compat)
          "bodyStyle": { ... } // optional global per-body visibility/color
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
        # Construct a unique and stable subject id from the file stem
        base_id = path.stem
        subject_id = base_id
        # Ensure uniqueness in case of duplicate filenames
        suffix = 2
        while subject_id in subject_ids:
            subject_id = f"{base_id}_{suffix}"
            suffix += 1
        subject_ids.append(subject_id)

        # Resolve model for this subject:
        # models list is indexed by subject position (0-based); a single entry applies to all.
        model: str | None = None
        if models:
            model = models[idx - 1] if idx - 1 < len(models) else models[0]

        subject_entry: dict = {
            "id": subject_id,
            "label": path.stem,
            "bodies": bodies_meta,
        }
        if model:
            subject_entry["model"] = model

        # Per-subject bodyStyle resolution (highest to lowest priority):
        #   1. --subject-colors entry for this subject (single hex color → all bodies)
        #   2. --body-style entry for this subject when body_style is a list
        #   3. --body-style as a flat dict (applied to every subject)
        color = subject_colors[idx - 1] if subject_colors and idx - 1 < len(subject_colors) else None
        if color:
            subject_entry["bodyStyle"] = {name: {"color": color} for name in bodies_meta}
        elif isinstance(body_style, list):
            if idx - 1 < len(body_style) and isinstance(body_style[idx - 1], dict):
                subject_entry["bodyStyle"] = body_style[idx - 1]
        elif body_style:
            subject_entry["bodyStyle"] = body_style

        # Whole-model transparency (--subject-opacity): apply to all bodies
        if subject_opacity and idx - 1 < len(subject_opacity):
            opacity_val = subject_opacity[idx - 1]
            opacity_val = max(0.0, min(1.0, float(opacity_val)))
            if subject_entry.get("bodyStyle") is not None:
                subject_entry["bodyStyle"] = copy.deepcopy(subject_entry["bodyStyle"])
            else:
                subject_entry["bodyStyle"] = {}
            for name in bodies_meta:
                subject_entry["bodyStyle"].setdefault(name, {})["opacity"] = opacity_val

        subjects_meta.append(subject_entry)

    init_msg = {
        "type": "init",
        # Inform client about nominal frame rate (after speed scaling)
        "frameRate": effective_base_fps * speed,
        "subjects": subjects_meta,
    }
    # Single-subject frontend compatibility: send flat bodies (and bodyStyle) at top level
    if len(subjects_meta) == 1:
        init_msg["bodies"] = subjects_meta[0]["bodies"]
    if body_style and not isinstance(body_style, list):
        init_msg["bodyStyle"] = body_style
    if camera is not None:
        init_msg["camera"] = camera if isinstance(camera, dict) else {"view": camera}
    await websocket.send(json.dumps(init_msg))
    print(f"  Subject IDs: {subject_ids}  (use these with hide/show commands)")

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


_CAMERA_PRESETS = {
    # Generic axis-aligned presets (visualizer coordinate names)
    "front", "back", "left", "right", "top", "bottom",
    "isometric", "default",
    "frontTopRight", "frontTopLeft", "frontBottomRight", "frontBottomLeft",
    "backTopRight", "backTopLeft", "backBottomRight", "backBottomLeft",
    # OpenCap anatomical aliases (map to the correct axis for a standing subject)
    "anterior",      # frontal plane, facing subject  (+X in OpenCap) = same as 'right'
    "posterior",     # behind subject                 (-X in OpenCap) = same as 'left'
    "sagittal_right", # subject's right side          (+Z in OpenCap) = same as 'front'
    "sagittal_left",  # subject's left side           (-Z in OpenCap) = same as 'back'
    "superior",      # looking down                   (+Y)            = same as 'top'
    "inferior",      # looking up                     (-Y)            = same as 'bottom'
}


def _parse_camera(arg: str) -> "dict | str | None":
    """Parse --camera: a named preset string or inline JSON with position/target.

    Named presets: front | back | left | right | top | bottom | isometric | default
                   frontTopRight | frontTopLeft | backTopRight | backTopLeft | ...

    JSON format:  {"position": [x, y, z], "target": [x, y, z]}
                  (target defaults to [0, 1, 0] if omitted)
    """
    if not arg or not arg.strip():
        return None
    arg = arg.strip()
    if arg in _CAMERA_PRESETS:
        return arg  # plain preset name
    # Try JSON
    try:
        data = json.loads(arg)
        if isinstance(data, dict) and "position" in data:
            return data
        print(f"--camera JSON must contain a 'position' key; got: {arg[:60]}")
        return None
    except json.JSONDecodeError:
        print(f"Unknown --camera value '{arg}'. Valid presets: {sorted(_CAMERA_PRESETS)}")
        return None


def _parse_body_style(arg: str) -> "dict | list | None":
    """Parse --body-style: either a path to a JSON file or inline JSON string.

    Accepts:
      - A flat dict:  {"pelvis": {"color": "#ff0000"}, ...}   → same style for every subject
      - A JSON array: [{"pelvis": {"color": "#ff0000"}}, {"pelvis": {"color": "#0000ff"}}]
                       → per-subject styles indexed by position
    """
    if not arg or not arg.strip():
        return None
    arg = arg.strip()
    # Inline JSON: try parse first to avoid path.is_file() on long strings (OS "file name too long")
    if arg.startswith("{") or arg.startswith("["):
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

    # Extract --subject-colors if present (comma-separated hex colors, one per subject)
    # e.g. --subject-colors "#d3d3d3,#4995e0"
    subject_colors: list[str] | None = None
    if "--subject-colors" in args:
        idx = args.index("--subject-colors")
        if idx + 1 < len(args):
            subject_colors = [c.strip() for c in args[idx + 1].split(",")]
            args = args[:idx] + args[idx + 2 :]
        else:
            args = args[:idx] + args[idx + 1 :]

    # Extract --subject-opacity if present (comma-separated floats 0-1, one per subject)
    # e.g. --subject-opacity 0.5,0.8
    subject_opacity: list[float] | None = None
    if "--subject-opacity" in args:
        idx = args.index("--subject-opacity")
        if idx + 1 < len(args):
            raw = [x.strip() for x in args[idx + 1].split(",")]
            subject_opacity = []
            for v in raw:
                try:
                    f = float(v)
                    subject_opacity.append(max(0.0, min(1.0, f)))
                except ValueError:
                    print(f"Invalid opacity '{v}' in --subject-opacity, skipping")
            args = args[:idx] + args[idx + 2 :]
        else:
            args = args[:idx] + args[idx + 1 :]

    # Extract --camera if present
    # Accepts a named preset (e.g. "front") or inline JSON {"position":[x,y,z],"target":[x,y,z]}
    camera: "dict | str | None" = None
    if "--camera" in args:
        idx = args.index("--camera")
        if idx + 1 < len(args):
            camera = _parse_camera(args[idx + 1])
            args = args[:idx] + args[idx + 2 :]
        else:
            args = args[:idx] + args[idx + 1 :]

    # Extract --model if present
    # Single value ("LaiArnold") or comma-separated per-subject ("LaiArnold,Hu_ISB_shoulder")
    models: "list[str] | None" = None
    if "--model" in args:
        idx = args.index("--model")
        if idx + 1 < len(args):
            models = [m.strip() for m in args[idx + 1].split(",")]
            args = args[:idx] + args[idx + 2 :]
        else:
            args = args[:idx] + args[idx + 1 :]

    json_args = [a for a in args if a.lower().endswith(".json")]
    other_args = [a for a in args if not a.lower().endswith(".json")]

    if not json_args:
        if DEFAULT_JSON_PATH.is_file():
            json_paths = [DEFAULT_JSON_PATH.resolve()]
            print(f"No JSON file arguments provided; using default mono.json at {json_paths[0]}")
        else:
            print("Error: at least one JSON file path is required (mono.json not found)")
            sys.exit(1)
    else:
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
        _CONNECTED_CLIENTS.add(websocket)
        print(f"Client connected from {websocket.remote_address}")
        try:
            await stream_from_json(
                websocket, json_paths, speed,
                body_style=body_style,
                subject_colors=subject_colors,
                subject_opacity=subject_opacity,
                camera=camera,
                models=models,
            )
        except Exception as e:
            print(f"Error during streaming: {e}")
        finally:
            _CONNECTED_CLIENTS.discard(websocket)
            print("Client disconnected")

    async def stdin_command_loop():
        """
        Read commands from stdin while the server is running.

        Commands
        --------
        notify <message>                    – info banner
        notify <level> <message>            – banner with level (info/success/warning/error)
        scores <n1> <n2> <n3> <n4> <n5> [label1 ... label5]  – show trial scores (optional labels)
        hidescores                          – hide the trial scores plot
        hide <subject_id>                   – hide a subject
        show <subject_id>                   – show a subject
        help                                – print this list
        """
        loop = asyncio.get_event_loop()
        reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(reader)
        try:
            await loop.connect_read_pipe(lambda: protocol, sys.stdin)
        except Exception:
            return  # stdin not a pipe (e.g. IDE terminal) — skip gracefully

        print("Interactive commands ready (type 'help' for usage).")
        while True:
            try:
                line = await reader.readline()
                if not line:
                    break
                cmd = line.decode().strip()
                if not cmd:
                    continue
                parts = cmd.split(" ", 2)
                verb = parts[0].lower()
                if verb == "help":
                    print(
                        "Commands:\n"
                        "  notify <message>              – info notification\n"
                        "  notify <level> <message>      – notification with level (info/success/warning/error)\n"
                        "  scores <n1> <n2> <n3> <n4> <n5> [label1 ... label5]  – show trial scores (optional labels)\n"
                        "  hidescores                   – hide trial scores plot\n"
                        "  hide <subject_id>             – hide subject\n"
                        "  show <subject_id>             – show subject\n"
                    )
                elif verb == "notify":
                    if len(parts) >= 3 and parts[1] in ("info", "success", "warning", "error"):
                        await send_notification(parts[2], level=parts[1])
                        print(f"[notify:{parts[1]}] {parts[2]}")
                    elif len(parts) >= 2:
                        msg_text = " ".join(parts[1:])
                        await send_notification(msg_text)
                        print(f"[notify:info] {msg_text}")
                    else:
                        print("Usage: notify [level] <message>")
                elif verb == "scores" and len(parts) >= 2:
                    tokens = " ".join(parts[1:]).split()
                    if len(tokens) >= 5:
                        try:
                            scores = [float(x) for x in tokens[:5]]
                            labels = tokens[5:10] if len(tokens) >= 10 else None
                            await send_trial_scores(scores, labels=labels)
                            print(f"[scores] {scores}" + (f" labels={labels}" if labels else ""))
                        except ValueError as e:
                            print(f"Usage: scores <n1> <n2> <n3> <n4> <n5> [label1 ... label5]. Error: {e}")
                    else:
                        print("Usage: scores <n1> <n2> <n3> <n4> <n5>  [label1 label2 label3 label4 label5]")
                elif verb == "hidescores":
                    await send_hide_scores()
                    print("[hidescores]")
                elif verb == "hide" and len(parts) >= 2:
                    await send_subject_visibility(parts[1], False)
                    print(f"[hide] {parts[1]}")
                elif verb == "show" and len(parts) >= 2:
                    await send_subject_visibility(parts[1], True)
                    print(f"[show] {parts[1]}")
                else:
                    print(f"Unknown command '{cmd}'. Type 'help' for usage.")
            except Exception as e:
                print(f"[stdin] Error: {e}")

    print(f"Streaming from {[str(p) for p in json_paths]}")
    port = 8765
    host = "0.0.0.0"
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            lan_ip = s.getsockname()[0]
    except Exception:
        lan_ip = "127.0.0.1"
    print(f"WebSocket server listening on ws://localhost:{port} (this machine)")
    if lan_ip != "127.0.0.1":
        print(f"  On same WiFi, use ws://{lan_ip}:{port} from another computer")
    async with websockets.serve(handler, host, port):
        await asyncio.gather(
            asyncio.Future(),   # keep server alive forever
            stdin_command_loop(),
        )


if __name__ == "__main__":
    asyncio.run(main())
