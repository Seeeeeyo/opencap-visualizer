import base64
import gzip
import io
import pickle
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import joblib
import numpy as np
import torch
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from smplx import SMPLLayer
from smplx.lbs import batch_rodrigues


ROOT_DIR = Path(__file__).resolve().parents[1]
SMPL_MODEL_DIR = ROOT_DIR / "body_models" / "smpl"
SMPL_BATCH_SIZE = 128

SMPL_SKELETON_EDGES = [
    (0, 1),
    (1, 2),
    (2, 3),
    (0, 4),
    (4, 5),
    (5, 6),
    (0, 7),
    (7, 8),
    (8, 9),
    (9, 10),
    (8, 11),
    (11, 12),
    (12, 13),
    (8, 14),
    (14, 15),
    (15, 16),
    (0, 17),
    (17, 18),
    (18, 19),
    (19, 20),
    (20, 21),
    (21, 22),
    (19, 23),
]


class SMPLProcessor:
    """Utility wrapper that keeps SMPL layers cached per gender and runs batched FK."""

    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self._layers: Dict[str, SMPLLayer] = {}

    def _get_layer(self, gender: str) -> SMPLLayer:
        gender_key = (gender or "NEUTRAL").upper()
        if gender_key not in {"MALE", "FEMALE", "NEUTRAL"}:
            gender_key = "NEUTRAL"

        if gender_key not in self._layers:
            if not self.model_dir.exists():
                raise FileNotFoundError(f"SMPL model directory not found: {self.model_dir}")
            self._layers[gender_key] = SMPLLayer(model_path=str(self.model_dir), gender=gender_key, batch_size=1)
        return self._layers[gender_key]

    @torch.no_grad()
    def forward(
        self,
        poses: np.ndarray,
        betas: np.ndarray,
        trans: np.ndarray,
        gender: str,
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Evaluate SMPL in chunks and return (vertices, joints, faces)."""

        device = torch.device("cpu")
        layer = self._get_layer(gender).to(device)

        frames = poses.shape[0]
        vertices, joints = [], []

        for start in range(0, frames, SMPL_BATCH_SIZE):
            end = min(start + SMPL_BATCH_SIZE, frames)

            pose_chunk = torch.from_numpy(poses[start:end]).float().to(device)
            betas_chunk = torch.from_numpy(betas[start:end]).float().to(device)
            trans_chunk = torch.from_numpy(trans[start:end]).float().to(device)

            global_orient_aa = pose_chunk[:, :3]
            body_pose_aa = pose_chunk[:, 3:]

            global_orient_mat = batch_rodrigues(global_orient_aa).reshape(-1, 1, 3, 3)
            body_pose_mat = batch_rodrigues(body_pose_aa.reshape(-1, 3)).reshape(-1, body_pose_aa.shape[1] // 3, 3, 3)

            output = layer(
                global_orient=global_orient_mat,
                body_pose=body_pose_mat,
                betas=betas_chunk,
                transl=trans_chunk,
            )

            vertices.append(output.vertices.cpu().numpy())
            joints.append(output.joints.cpu().numpy())

        vertices_np = np.concatenate(vertices, axis=0).astype(np.float32)
        joints_np = np.concatenate(joints, axis=0).astype(np.float32)
        faces_np = layer.faces_tensor.cpu().numpy().astype(np.int32)
        return vertices_np, joints_np, faces_np


processor = SMPLProcessor(SMPL_MODEL_DIR)

app = FastAPI(title="SMPL Conversion Service", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def _decode_pickle(contents: bytes):
    buffer = io.BytesIO(contents)

    # 1) Plain pickle
    try:
        return pickle.load(buffer)
    except Exception:
        buffer.seek(0)

    # 2) Joblib (handles joblib/zlib wrapped pickles)
    try:
        return joblib.load(buffer)
    except Exception:
        buffer.seek(0)

    # 3) gzip-compressed pickle
    try:
        with gzip.GzipFile(fileobj=buffer) as gz:
            return pickle.load(gz)
    except Exception:
        buffer.seek(0)

    # 4) Zip archive containing a pickle (rare but easy to support)
    try:
        with zipfile.ZipFile(buffer) as zf:
            for name in zf.namelist():
                with zf.open(name) as inner:
                    data = inner.read()
                    try:
                        return pickle.loads(data)
                    except Exception:
                        continue
    except Exception as exc:
        raise ValueError(f"Unable to decode pickle: {exc}") from exc

    raise ValueError("Unable to decode pickle: unknown format")


def _to_float32(array, expected_last_dim=None):
    arr = np.asarray(array, dtype=np.float32)
    if expected_last_dim and arr.shape[-1] != expected_last_dim:
        raise ValueError(f"Expected last dimension {expected_last_dim}, got {arr.shape[-1]}")
    return arr


def _infer_fps_from_time(time: Optional[np.ndarray]) -> Optional[float]:
    """Infer a frames-per-second value from a monotonic time array."""
    if time is None or len(time) < 2:
        return None

    diffs = np.diff(time.astype(np.float64))
    diffs = diffs[diffs > 0]
    if diffs.size == 0:
        return None

    median_step = float(np.median(diffs))
    if median_step <= 0:
        return None

    inferred_fps = 1.0 / median_step
    if not np.isfinite(inferred_fps):
        return None

    # Clamp to a sensible mocap range to protect against bad data
    return float(np.clip(inferred_fps, 10.0, 240.0))


def _extract_sequence_dict(raw):
    """Some pickles wrap the sequence in a single-key dict (e.g. {'0': {...}})."""
    if isinstance(raw, dict) and len(raw) == 1:
        candidate = next(iter(raw.values()))
        if isinstance(candidate, dict):
            return candidate
    return raw


def _normalize_sequence(raw: dict) -> Dict[str, np.ndarray]:
    """Normalise different SMPL pickle layouts to a consistent dictionary."""

    raw = _extract_sequence_dict(raw)

    if not isinstance(raw, dict):
        raise ValueError("SMPL pickle must contain a dictionary.")

    def first_available(keys):
        for key in keys:
            value = raw.get(key)
            if value is not None:
                return value
        return None

    if "poses" in raw:
        poses = _to_float32(raw["poses"])
    else:
        body_pose = first_available(["pose", "body_pose"])
        if body_pose is None:
            raise ValueError("SMPL sequence missing body pose information.")
        body_pose = _to_float32(body_pose)

        # If pose already contains global orientation (e.g. (F, 72)), use it directly.
        if body_pose.ndim == 2 and body_pose.shape[1] in (69, 72):
            if body_pose.shape[1] == 72:
                poses = body_pose
            else:
                global_orient = first_available(["global_orient", "root_orient"])
                if global_orient is None:
                    raise ValueError("SMPL sequence missing global orientation.")
                global_orient = _to_float32(global_orient)
                if global_orient.ndim == 3:
                    global_orient = global_orient.reshape(global_orient.shape[0], -1)
                poses = np.concatenate([global_orient, body_pose], axis=1)
        else:
            raise ValueError("SMPL sequence pose format not supported.")

    frames = poses.shape[0]

    betas = raw.get("betas")
    if betas is None:
        betas = np.zeros((frames, 10), dtype=np.float32)
    else:
        betas = _to_float32(betas)
        if betas.ndim == 1:
            betas = np.repeat(betas[None, :], frames, axis=0)
        elif betas.shape[0] == 1:
            betas = np.repeat(betas, frames, axis=0)
        elif betas.shape[0] != frames:
            betas = np.repeat(betas[:1], frames, axis=0)

    # Get body translation - check if "trans" is actually camera translation first
    # If cam_R exists and "trans" matches its frame count, it might be camera translation
    body_trans_candidate = None
    potential_cam_T = None
    
    # Check if "trans" might be camera translation (if cam_R exists)
    cam_R_check = raw.get("cam_R")
    if cam_R_check is None:
        rotation_check = raw.get("rotation")
        if rotation_check is not None:
            rotation_check = _to_float32(rotation_check)
            if rotation_check.ndim == 4 and rotation_check.shape[0] == 1:
                cam_R_check = rotation_check
            elif rotation_check.ndim == 3 and rotation_check.shape[1] == 3 and rotation_check.shape[2] == 3:
                cam_R_check = rotation_check
    
    trans_raw = raw.get("trans")
    if trans_raw is not None and cam_R_check is not None:
        trans_raw_arr = _to_float32(trans_raw)
        # Check if frame counts match
        cam_R_frames = None
        if hasattr(cam_R_check, 'ndim'):
            if cam_R_check.ndim == 4 and cam_R_check.shape[0] == 1:
                cam_R_frames = cam_R_check.shape[1]
            elif cam_R_check.ndim == 3 and cam_R_check.shape[1] == 3 and cam_R_check.shape[2] == 3:
                cam_R_frames = cam_R_check.shape[0]
        
        # If trans matches cam_R frame count and is per-frame, it's likely camera translation
        if (cam_R_frames is not None and trans_raw_arr.ndim == 2 and 
            trans_raw_arr.shape[0] == cam_R_frames and trans_raw_arr.shape[1] == 3):
            # Check if there's an alternative body translation field
            if raw.get("trans_world") is None and raw.get("transl") is None:
                potential_cam_T = trans_raw_arr  # trans is camera translation
                body_trans_candidate = np.zeros((frames, 3), dtype=np.float32)  # Body trans is zero
    
    # Get body translation
    if body_trans_candidate is not None:
        trans = body_trans_candidate
    else:
        trans = first_available(["trans_world", "trans", "transl"])
        if trans is None:
            trans = np.zeros((frames, 3), dtype=np.float32)
        trans = _to_float32(trans, expected_last_dim=3)
        if trans.shape[0] == 1:
            trans = np.repeat(trans, frames, axis=0)

    fps = raw.get("fps") or raw.get("frame_rate")
    time = raw.get("time")
    if time is None or len(time) != frames:
        fps_value = float(fps) if fps is not None else 60.0
        time = np.arange(frames, dtype=np.float32) / float(fps_value)
    else:
        time = _to_float32(time)

    if fps is None:
        inferred = _infer_fps_from_time(time)
        fps = inferred if inferred is not None else 60.0
    else:
        fps = float(fps)

    # Handle camera extrinsics - check for cam_R/cam_T first, then rotation/translation
    # Note: cam_R can be per-frame (shape like (1, N, 3, 3) or (N, 3, 3))
    # Note: cam_T can be per-frame (shape like (N, 3))
    cam_R = raw.get("cam_R")
    if cam_R is None:
        # Try to get from rotation field
        rotation = raw.get("rotation")
        if rotation is not None:
            rotation = _to_float32(rotation)
            # Ensure it's 3x3
            if rotation.ndim == 2 and rotation.shape == (3, 3):
                cam_R = rotation
            elif rotation.size == 9:
                cam_R = rotation.reshape(3, 3)
            # Handle per-frame rotations: shape (1, N, 3, 3) or (N, 3, 3)
            elif rotation.ndim == 4 and rotation.shape[0] == 1:
                cam_R = rotation  # Keep as (1, N, 3, 3)
            elif rotation.ndim == 3 and rotation.shape[1] == 3 and rotation.shape[2] == 3:
                cam_R = rotation  # Keep as (N, 3, 3)
    else:
        cam_R = _to_float32(cam_R)
        # Handle per-frame rotations if shape is (1, N, 3, 3) or (N, 3, 3)
        if cam_R.ndim == 4 and cam_R.shape[0] == 1:
            pass  # Keep as (1, N, 3, 3)
        elif cam_R.ndim == 3 and cam_R.shape[1] == 3 and cam_R.shape[2] == 3:
            pass  # Keep as (N, 3, 3)

    cam_T = raw.get("cam_T")
    if cam_T is None:
        # Try to get from translation field (camera translation, not body translation)
        translation = raw.get("translation")
        if translation is not None:
            translation = _to_float32(translation)
            # Ensure it's shape (3,) for single frame or (N, 3) for per-frame
            if translation.ndim == 1:
                if translation.shape[0] == 3:
                    cam_T = translation
                elif translation.size >= 3:
                    cam_T = translation[:3]
            elif translation.ndim == 2 and translation.shape[1] == 3:
                cam_T = translation  # Per-frame: (N, 3)
            elif translation.size >= 3:
                cam_T = translation.flatten()[:3]
        # Use the potential_cam_T we identified earlier (if "trans" was camera translation)
        if potential_cam_T is not None:
            cam_T = potential_cam_T
    else:
        cam_T = _to_float32(cam_T)
        # Handle per-frame translations: shape (N, 3)
        if cam_T.ndim == 2 and cam_T.shape[1] == 3:
            pass  # Keep as (N, 3)

    intrinsic_mat = raw.get("intrinsicMat")
    if intrinsic_mat is not None:
        intrinsic_mat = _to_float32(intrinsic_mat)

    distortion = raw.get("distortion")
    if distortion is not None:
        distortion = _to_float32(distortion)

    image_size = raw.get("imageSize")
    if image_size is not None:
        image_size = _to_float32(image_size)

    gender = str(raw.get("gender", "neutral")).lower()
    if gender not in {"male", "female", "neutral"}:
        gender = "neutral"

    verts = raw.get("verts")
    if verts is not None:
        verts = _to_float32(verts)
    joints = raw.get("joints")
    if joints is not None:
        joints = _to_float32(joints)
    faces = raw.get("faces")
    if faces is not None and not isinstance(faces, np.ndarray):
        faces = np.asarray(faces, dtype=np.int32)

    return {
        "poses": poses,
        "betas": betas,
        "trans": trans,
        "fps": float(fps),
        "time": time,
        "gender": gender,
        "verts": verts,
        "joints": joints,
        "faces": faces,
        "cam_R": cam_R,
        "cam_T": cam_T,
        "intrinsicMat": intrinsic_mat,
        "distortion": distortion,
        "imageSize": image_size,
    }


def _broadcast_camera_sequence(array, target_frames, expected_shape):
    arr = np.asarray(array, dtype=np.float32)
    if arr.shape == expected_shape:
        return arr
    if arr.ndim == 2 and expected_shape == (target_frames, 3, 3):
        if arr.shape == (3, 3):
            return np.broadcast_to(arr, (target_frames, 3, 3)).astype(np.float32, copy=False)
    if arr.ndim == 1 and expected_shape == (target_frames, 3):
        if arr.shape == (3,):
            return np.broadcast_to(arr, (target_frames, 3)).astype(np.float32, copy=False)
    if arr.shape[0] != target_frames:
        first = np.asarray(arr[0], dtype=np.float32)
        return np.broadcast_to(first, expected_shape).astype(np.float32, copy=False)
    return arr.astype(np.float32, copy=False)


def _compute_projected_points(sequence: Dict[str, np.ndarray], joints: np.ndarray):
    cam_R = sequence.get("cam_R")
    cam_T = sequence.get("cam_T")
    intrinsic = sequence.get("intrinsicMat")
    if cam_R is None or cam_T is None or intrinsic is None:
        return None

    frames, joint_count, _ = joints.shape
    try:
        cam_R = _broadcast_camera_sequence(cam_R, frames, (frames, 3, 3))
        cam_T = _broadcast_camera_sequence(cam_T, frames, (frames, 3))
        intrinsic = np.asarray(intrinsic, dtype=np.float32)
    except Exception:
        return None

    if intrinsic.shape != (3, 3):
        return None

    distortion = sequence.get("distortion")
    distortion_vec = np.zeros(5, dtype=np.float32)
    if distortion is not None:
        dist_arr = np.asarray(distortion, dtype=np.float32).flatten()
        if dist_arr.size:
            count = min(5, dist_arr.size)
            distortion_vec[:count] = dist_arr[:count]
    k1, k2, p1, p2, k3 = distortion_vec.tolist()

    fx = float(intrinsic[0, 0])
    fy = float(intrinsic[1, 1])
    cx = float(intrinsic[0, 2])
    cy = float(intrinsic[1, 2])

    joints_world = joints.astype(np.float32, copy=False)
    joints_cam = np.einsum("fij,fnj->fni", cam_R, joints_world) + cam_T[:, None, :]

    x = joints_cam[..., 0]
    y = joints_cam[..., 1]
    z = joints_cam[..., 2]

    valid = z > 1e-4
    xn = np.zeros_like(x, dtype=np.float32)
    yn = np.zeros_like(y, dtype=np.float32)
    xn[valid] = x[valid] / z[valid]
    yn[valid] = y[valid] / z[valid]

    r2 = xn * xn + yn * yn
    radial = 1.0 + k1 * r2 + k2 * r2 * r2 + k3 * r2 * r2 * r2
    x_distorted = xn * radial + 2 * p1 * xn * yn + p2 * (r2 + 2 * xn * xn)
    y_distorted = yn * radial + p1 * (r2 + 2 * yn * yn) + 2 * p2 * xn * yn

    u = fx * x_distorted + cx
    v = fy * y_distorted + cy

    u[~valid] = np.nan
    v[~valid] = np.nan

    projected = np.stack([u, v], axis=-1).astype(np.float32, copy=False)
    return projected


def _encode_float32(array: np.ndarray) -> str:
    return base64.b64encode(np.ascontiguousarray(array, dtype=np.float32).tobytes()).decode("ascii")


@app.post("/api/smpl/sequence")
async def upload_smpl_sequence(
    file: UploadFile = File(...),
    intrinsics_file: Optional[UploadFile] = File(None)
):
    contents = await file.read()
    try:
        raw = _decode_pickle(contents)
        
        # If intrinsics file is provided separately, merge it into the raw data
        if intrinsics_file is not None:
            intrinsics_contents = await intrinsics_file.read()
            try:
                intrinsics_data = _decode_pickle(intrinsics_contents)
                
                # Handle both pickle format (dict with keys) and JSON-like format
                if isinstance(intrinsics_data, dict):
                    # Extract intrinsics from the pickle dict
                    # Handle both "intrinsicMat" and "intrinsic" key names
                    intrinsic_value = intrinsics_data.get("intrinsicMat") or intrinsics_data.get("intrinsic")
                    if intrinsic_value is not None:
                        # Convert to numpy array if it's a list
                        if isinstance(intrinsic_value, (list, tuple)):
                            raw["intrinsicMat"] = np.array(intrinsic_value, dtype=np.float32)
                        else:
                            raw["intrinsicMat"] = _to_float32(intrinsic_value)
                    
                    if "distortion" in intrinsics_data:
                        dist_value = intrinsics_data["distortion"]
                        if isinstance(dist_value, (list, tuple)):
                            raw["distortion"] = np.array(dist_value, dtype=np.float32)
                        else:
                            raw["distortion"] = _to_float32(dist_value)
                    
                    if "imageSize" in intrinsics_data:
                        size_value = intrinsics_data["imageSize"]
                        if isinstance(size_value, (list, tuple)):
                            raw["imageSize"] = np.array(size_value, dtype=np.float32)
                        else:
                            raw["imageSize"] = _to_float32(size_value)
                    
                    # Handle extrinsics: rotation -> cam_R, translation -> cam_T
                    # Only use if cam_R/cam_T are not already in the PKL file
                    if "rotation" in intrinsics_data and raw.get("cam_R") is None:
                        rotation_value = intrinsics_data["rotation"]
                        if isinstance(rotation_value, (list, tuple)):
                            rotation_array = np.array(rotation_value, dtype=np.float32)
                        else:
                            rotation_array = _to_float32(rotation_value)
                        # Ensure it's 3x3
                        if rotation_array.shape == (3, 3):
                            raw["cam_R"] = rotation_array
                        elif rotation_array.ndim == 2 and rotation_array.shape[1] == 3:
                            # If it's (1, 3, 3) or similar, squeeze it
                            raw["cam_R"] = rotation_array.reshape(3, 3) if rotation_array.size == 9 else rotation_array
                    
                    if "translation" in intrinsics_data and raw.get("cam_T") is None:
                        translation_value = intrinsics_data["translation"]
                        if isinstance(translation_value, (list, tuple)):
                            translation_array = np.array(translation_value, dtype=np.float32)
                        else:
                            translation_array = _to_float32(translation_value)
                        # Ensure it's shape (3,)
                        if translation_array.ndim == 1 and translation_array.shape[0] == 3:
                            raw["cam_T"] = translation_array
                        elif translation_array.size == 3:
                            raw["cam_T"] = translation_array.flatten()[:3]
                else:
                    # If it's a numpy array or list, try to interpret it
                    if isinstance(intrinsics_data, np.ndarray):
                        if intrinsics_data.shape == (3, 3):
                            raw["intrinsicMat"] = intrinsics_data
            except Exception as e:
                # If intrinsics file fails to load, continue without it
                print(f"Warning: Failed to load intrinsics file: {e}")
        
        sequence = _normalize_sequence(raw)
        verts = sequence.pop("verts", None)
        joints = sequence.pop("joints", None)
        faces = sequence.pop("faces", None)

        if verts is not None and joints is not None:
            vertices = verts.astype(np.float32)
            joints = joints.astype(np.float32)
            if faces is None:
                _, _, faces = processor.forward(sequence["poses"], sequence["betas"], sequence["trans"], sequence["gender"])
        else:
            vertices, joints, faces = processor.forward(sequence["poses"], sequence["betas"], sequence["trans"], sequence["gender"])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - protect against unexpected runtime errors
        raise HTTPException(status_code=500, detail=f"Failed to evaluate SMPL sequence: {exc}") from exc

    try:
        projected = _compute_projected_points(sequence, joints.reshape(vertices.shape[0], joints.shape[1], 3))
    except Exception:
        projected = None

    response = {
        "name": file.filename,
        "fps": sequence["fps"],
        "frame_count": int(vertices.shape[0]),
        "vertex_count": int(vertices.shape[1]),
        "joint_count": int(joints.shape[1]),
        "gender": sequence["gender"],
        "time": sequence["time"].astype(float).tolist(),
        "faces": faces.tolist(),
        "vertices": _encode_float32(vertices),
        "joints": _encode_float32(joints),
        "skeleton_edges": SMPL_SKELETON_EDGES,
    }
    if sequence.get("cam_R") is not None:
        response["cam_R"] = sequence["cam_R"].astype(float).tolist()
    if sequence.get("cam_T") is not None:
        response["cam_T"] = sequence["cam_T"].astype(float).tolist()
    if sequence.get("intrinsicMat") is not None:
        response["intrinsicMat"] = sequence["intrinsicMat"].astype(float).tolist()
    if sequence.get("distortion") is not None:
        response["distortion"] = sequence["distortion"].astype(float).tolist()
    if sequence.get("imageSize") is not None:
        response["imageSize"] = sequence["imageSize"].astype(float).tolist()
    if projected is not None:
        response["projected_joints"] = _encode_float32(projected)
        response["projected_shape"] = [int(projected.shape[0]), int(projected.shape[1]), int(projected.shape[2])]
        image_size = sequence.get("imageSize")
        if image_size is not None:
            response["projected_image_size"] = sequence["imageSize"].astype(float).tolist()
    return JSONResponse(response)


@app.post("/api/smpl/skeleton")
async def upload_skeleton_sequence(file: UploadFile = File(...), intrinsics_file: Optional[UploadFile] = File(None)):
    """Handle skeleton-only sequences (joints without mesh) from JSON or PKL files."""
    contents = await file.read()
    filename = file.filename.lower()
    
    try:
        if filename.endswith('.json'):
            import json
            raw_data = json.loads(contents.decode('utf-8'))
            
            # Extract joints from OpenCap JSON format
            if not isinstance(raw_data, dict) or 'bodies' not in raw_data:
                raise ValueError("JSON must contain a 'bodies' field")
            
            time = raw_data.get('time', [])
            if not time:
                raise ValueError("JSON must contain a 'time' field")
            
            frames = len(time)
            bodies = raw_data['bodies']
            
            # Extract body positions as joints (each body segment becomes a joint)
            body_names = sorted(bodies.keys())
            joint_count = len(body_names)
            
            if joint_count == 0:
                raise ValueError("No bodies found in JSON")
            
            # Build joints array: (frames, joints, 3)
            joints = np.zeros((frames, joint_count, 3), dtype=np.float32)
            
            for joint_idx, body_name in enumerate(body_names):
                body = bodies[body_name]
                if 'translation' in body and isinstance(body['translation'], list):
                    for frame_idx, translation in enumerate(body['translation']):
                        if frame_idx < frames and isinstance(translation, (list, tuple)) and len(translation) >= 3:
                            joints[frame_idx, joint_idx, :] = translation[:3]
            
            # Create skeleton edges from body hierarchy (simple chain for now)
            skeleton_edges = []
            # Simple parent-child relationships based on naming (can be improved)
            for i in range(len(body_names) - 1):
                skeleton_edges.append([i, i + 1])
            
            # Calculate FPS safely
            fps_value = raw_data.get('fps')
            if fps_value is not None:
                # Ensure fps is a number, not a dict or other type
                try:
                    fps = float(fps_value)
                except (TypeError, ValueError):
                    fps = None
            else:
                fps = None
            
            # If fps is not available, infer from time array
            if fps is None and len(time) > 1:
                try:
                    # Ensure time values are numbers
                    time_values = [float(t) for t in time[:2] if isinstance(t, (int, float, str))]
                    if len(time_values) >= 2 and time_values[1] > time_values[0]:
                        fps = 1.0 / (time_values[1] - time_values[0])
                    else:
                        fps = 60.0
                except (TypeError, ValueError, ZeroDivisionError):
                    fps = 60.0
            else:
                fps = fps if fps is not None else 60.0
            
            # Convert time array to float32, handling any non-numeric values
            try:
                time_array = np.array([float(t) for t in time if isinstance(t, (int, float, str))], dtype=np.float32)
                if len(time_array) != frames:
                    # If some time values couldn't be converted, use generated times
                    time_array = np.arange(frames, dtype=np.float32) / float(fps)
            except (TypeError, ValueError):
                time_array = np.arange(frames, dtype=np.float32) / float(fps)
            
        elif filename.endswith('.pkl') or filename.endswith('.pickle'):
            raw_data = _decode_pickle(contents)
            
            # Handle PKL as list of frames
            if isinstance(raw_data, list):
                frames = len(raw_data)
                if frames == 0:
                    raise ValueError("PKL file is empty")
                
                # Check if frames contain dicts (e.g., OpenPose format with pose_keypoints_2d)
                first_frame_with_data = None
                frame_format = None  # 'array', 'dict_2d', 'dict_3d'
                
                for frame_data in raw_data:
                    if frame_data:
                        # Handle case where frame_data is a list containing a dict
                        actual_frame = frame_data
                        if isinstance(frame_data, list) and len(frame_data) > 0 and isinstance(frame_data[0], dict):
                            actual_frame = frame_data[0]
                        
                        if isinstance(actual_frame, dict):
                            # Check for OpenPose-style dict with pose_keypoints_2d
                            if 'pose_keypoints_2d' in actual_frame:
                                keypoints = actual_frame['pose_keypoints_2d']
                                if isinstance(keypoints, list) and len(keypoints) > 0:
                                    # OpenPose format: [x1, y1, conf1, x2, y2, conf2, ...]
                                    joint_count = len(keypoints) // 3
                                    frame_format = 'dict_2d'
                                    first_frame_with_data = np.array(keypoints, dtype=np.float32).reshape(joint_count, 3)
                                    break
                            elif 'pose_keypoints_3d' in actual_frame:
                                keypoints = actual_frame['pose_keypoints_3d']
                                if isinstance(keypoints, list) and len(keypoints) > 0:
                                    # 3D keypoints: [x1, y1, z1, x2, y2, z2, ...]
                                    joint_count = len(keypoints) // 3
                                    frame_format = 'dict_3d'
                                    first_frame_with_data = np.array(keypoints, dtype=np.float32).reshape(joint_count, 3)
                                    break
                        elif isinstance(frame_data, (list, tuple)) and len(frame_data) > 0:
                            # Try to convert to array
                            try:
                                frame_array = np.array(frame_data, dtype=np.float32)
                                if frame_array.ndim == 2:
                                    joint_count = frame_array.shape[0]
                                    frame_format = 'array_2d'
                                    first_frame_with_data = frame_array
                                    break
                                elif frame_array.ndim == 1:
                                    joint_count = frame_array.shape[0] // 3
                                    frame_format = 'array_1d'
                                    first_frame_with_data = frame_array.reshape(joint_count, 3)
                                    break
                            except (TypeError, ValueError):
                                # Skip frames that can't be converted
                                continue
                
                if first_frame_with_data is None:
                    raise ValueError("No valid frame data found in PKL")
                
                # Build joints array
                joints = np.zeros((frames, joint_count, 3), dtype=np.float32)
                
                for frame_idx, frame_data in enumerate(raw_data):
                    if not frame_data:
                        continue
                    
                    try:
                        # Handle case where frame_data is a list containing a dict
                        actual_frame = frame_data
                        if isinstance(frame_data, list) and len(frame_data) > 0 and isinstance(frame_data[0], dict):
                            actual_frame = frame_data[0]
                        
                        if frame_format == 'dict_2d':
                            # Extract 2D keypoints and pad Z with 0
                            if isinstance(actual_frame, dict) and 'pose_keypoints_2d' in actual_frame:
                                keypoints = actual_frame['pose_keypoints_2d']
                                if isinstance(keypoints, list) and len(keypoints) >= joint_count * 3:
                                    keypoint_array = np.array(keypoints[:joint_count * 3], dtype=np.float32)
                                    # Reshape to (joint_count, 3) where 3rd is confidence
                                    keypoints_2d = keypoint_array.reshape(joint_count, 3)
                                    # Use x, y, and set z to 0 (or could use confidence as z)
                                    joints[frame_idx, :, 0] = keypoints_2d[:, 0]  # x
                                    joints[frame_idx, :, 1] = keypoints_2d[:, 1]  # y
                                    joints[frame_idx, :, 2] = 0.0  # z (2D keypoints)
                        elif frame_format == 'dict_3d':
                            # Extract 3D keypoints
                            if isinstance(actual_frame, dict) and 'pose_keypoints_3d' in actual_frame:
                                keypoints = actual_frame['pose_keypoints_3d']
                                if isinstance(keypoints, list) and len(keypoints) >= joint_count * 3:
                                    keypoint_array = np.array(keypoints[:joint_count * 3], dtype=np.float32)
                                    joints[frame_idx] = keypoint_array.reshape(joint_count, 3)
                        elif frame_format in ('array_2d', 'array_1d'):
                            # Original array format handling
                            if isinstance(frame_data, (list, tuple)) and len(frame_data) > 0:
                                frame_array = np.array(frame_data, dtype=np.float32)
                                if frame_array.ndim == 2:
                                    joints[frame_idx] = frame_array[:joint_count, :3]
                                elif frame_array.ndim == 1:
                                    joints[frame_idx] = frame_array[:joint_count * 3].reshape(joint_count, 3)
                    except (TypeError, ValueError) as e:
                        # Skip frames that can't be processed
                        continue
                
                # Default skeleton edges (simple chain)
                skeleton_edges = [[i, i + 1] for i in range(joint_count - 1)]
                
                fps = 60.0
                time_array = np.arange(frames, dtype=np.float32) / float(fps)
            else:
                raise ValueError("PKL file must contain a list of frames")
        else:
            raise ValueError(f"Unsupported file format: {filename}")
        
        # Handle intrinsics file if provided
        cam_R = None
        cam_T = None
        intrinsic_mat = None
        distortion = None
        image_size = None
        
        if intrinsics_file is not None:
            intrinsics_contents = await intrinsics_file.read()
            try:
                intrinsics_data = _decode_pickle(intrinsics_contents)
                if isinstance(intrinsics_data, dict):
                    intrinsic_value = intrinsics_data.get("intrinsicMat") or intrinsics_data.get("intrinsic")
                    if intrinsic_value is not None:
                        intrinsic_mat = np.array(intrinsic_value, dtype=np.float32) if isinstance(intrinsic_value, (list, tuple)) else _to_float32(intrinsic_value)
                    
                    if "distortion" in intrinsics_data:
                        dist_value = intrinsics_data["distortion"]
                        distortion = np.array(dist_value, dtype=np.float32) if isinstance(dist_value, (list, tuple)) else _to_float32(dist_value)
                    
                    if "imageSize" in intrinsics_data:
                        size_value = intrinsics_data["imageSize"]
                        image_size = np.array(size_value, dtype=np.float32) if isinstance(size_value, (list, tuple)) else _to_float32(size_value)
                    
                    if "rotation" in intrinsics_data:
                        rotation_value = intrinsics_data["rotation"]
                        rotation_array = np.array(rotation_value, dtype=np.float32) if isinstance(rotation_value, (list, tuple)) else _to_float32(rotation_value)
                        if rotation_array.shape == (3, 3):
                            cam_R = rotation_array
                    
                    if "translation" in intrinsics_data:
                        translation_value = intrinsics_data["translation"]
                        translation_array = np.array(translation_value, dtype=np.float32) if isinstance(translation_value, (list, tuple)) else _to_float32(translation_value)
                        if translation_array.ndim == 1 and translation_array.shape[0] == 3:
                            cam_T = translation_array
            except Exception as e:
                print(f"Warning: Failed to load intrinsics file: {e}")
        
        # Compute projected points if we have camera data
        projected = None
        if cam_R is not None and cam_T is not None and intrinsic_mat is not None:
            try:
                sequence_dict = {
                    "cam_R": cam_R,
                    "cam_T": cam_T,
                    "intrinsicMat": intrinsic_mat,
                    "distortion": distortion if distortion is not None else np.zeros(5, dtype=np.float32),
                    "imageSize": image_size
                }
                projected = _compute_projected_points(sequence_dict, joints)
            except Exception:
                projected = None
        
        # Flatten joints for response
        joints_flat = joints.reshape(-1, 3).astype(np.float32)
        
        response = {
            "name": file.filename,
            "fps": float(fps),
            "frame_count": int(frames),
            "joint_count": int(joint_count),
            "vertex_count": 0,  # Skeleton-only, no vertices
            "gender": "neutral",
            "time": time_array.astype(float).tolist(),
            "faces": [],  # No mesh faces
            "vertices": "",  # Empty - skeleton only
            "joints": _encode_float32(joints_flat),
            "skeleton_edges": skeleton_edges,
        }
        
        if cam_R is not None:
            response["cam_R"] = cam_R.astype(float).tolist()
        if cam_T is not None:
            response["cam_T"] = cam_T.astype(float).tolist()
        if intrinsic_mat is not None:
            response["intrinsicMat"] = intrinsic_mat.astype(float).tolist()
        if distortion is not None:
            response["distortion"] = distortion.astype(float).tolist()
        if image_size is not None:
            response["imageSize"] = image_size.astype(float).tolist()
        if projected is not None:
            response["projected_joints"] = _encode_float32(projected)
            response["projected_shape"] = [int(projected.shape[0]), int(projected.shape[1]), int(projected.shape[2])]
            if image_size is not None:
                response["projected_image_size"] = image_size.astype(float).tolist()
        
        return JSONResponse(response)
        
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to process skeleton sequence: {exc}") from exc


@app.post("/api/smpl/extract-intrinsics")
async def extract_intrinsics(intrinsics_file: UploadFile = File(...)):
    """Extract camera intrinsics and extrinsics from a pickle file."""
    contents = await intrinsics_file.read()
    
    try:
        raw_data = _decode_pickle(contents)
        
        if not isinstance(raw_data, dict):
            raise ValueError("Intrinsics file must contain a dictionary")
        
        # Debug: log available keys
        import logging
        logging.info(f"Intrinsics file keys: {list(raw_data.keys())}")
        
        # Ensure all numpy comparisons use Python native types
        def safe_int(x):
            """Safely convert numpy scalar to Python int"""
            return int(x) if hasattr(x, '__int__') else x
        
        def safe_tuple(x):
            """Safely convert numpy shape to Python tuple"""
            if hasattr(x, '__iter__') and not isinstance(x, (str, bytes)):
                return tuple(safe_int(i) for i in x)
            return x
        
        # Extract intrinsics - check each key separately to avoid NumPy array truthiness issues
        intrinsic_mat = None
        for key in ['intrinsicMat', 'intrinsic_matrix', 'intrinsic']:
            val = raw_data.get(key)
            if val is not None:
                intrinsic_mat = val
                break
        
        if intrinsic_mat is not None:
            intrinsic_mat = _to_float32(intrinsic_mat)
            intrinsic_ndim = int(intrinsic_mat.ndim)
            intrinsic_shape = tuple(intrinsic_mat.shape)
            if intrinsic_ndim == 2 and intrinsic_shape[0] == 3 and intrinsic_shape[1] == 3:
                intrinsic_mat = intrinsic_mat.tolist()
            else:
                raise ValueError(f"Invalid intrinsic matrix shape: {intrinsic_shape}")
        else:
            raise ValueError("No intrinsic matrix found in file")
        
        # Extract distortion
        distortion = raw_data.get('distortion')
        if distortion is not None:
            distortion = _to_float32(distortion).tolist()
        
        # Extract image size - check each key separately to avoid NumPy array truthiness issues
        image_size = None
        for key in ['imageSize', 'image_size']:
            val = raw_data.get(key)
            if val is not None:
                image_size = val
                break
        
        if image_size is not None:
            image_size = _to_float32(image_size)
            image_ndim = int(image_size.ndim)
            if image_ndim == 1:
                image_size = image_size.tolist()
            elif image_ndim == 2:
                image_shape = tuple(image_size.shape)
                if image_shape[0] == 1:
                    image_size = image_size[0].tolist()
                else:
                    image_size = image_size.flatten().tolist()
        
        # Extract extrinsics - check for cam_R/cam_T first, then rotation/translation
        cam_R = raw_data.get('cam_R')
        if cam_R is None:
            rotation = raw_data.get('rotation')
            if rotation is not None:
                rotation = _to_float32(rotation)
                rotation_ndim = safe_int(rotation.ndim)
                rotation_shape = safe_tuple(rotation.shape)
                if rotation_ndim == 2 and len(rotation_shape) == 2 and rotation_shape[0] == 3 and rotation_shape[1] == 3:
                    cam_R = rotation
                elif rotation_ndim == 1 and safe_int(rotation.size) == 9:
                    cam_R = rotation.reshape(3, 3)
        else:
            cam_R = _to_float32(cam_R)
            cam_R_ndim = safe_int(cam_R.ndim)
            cam_R_size = safe_int(cam_R.size)
            if cam_R_ndim == 1 and cam_R_size == 9:
                cam_R = cam_R.reshape(3, 3)
            elif cam_R_ndim == 2:
                cam_R_shape = safe_tuple(cam_R.shape)
                if len(cam_R_shape) == 2 and cam_R_shape[0] == 3 and cam_R_shape[1] == 3:
                    pass  # Already correct shape
                elif cam_R_size == 9:
                    cam_R = cam_R.flatten()[:9].reshape(3, 3)
        
        cam_T = raw_data.get('cam_T')
        if cam_T is None:
            translation = raw_data.get('translation')
            if translation is not None:
                translation = _to_float32(translation)
                translation_ndim = safe_int(translation.ndim)
                translation_size = safe_int(translation.size)
                if translation_ndim == 1 and translation_size >= 3:
                    cam_T = translation[:3]
                elif translation_ndim == 2:
                    cam_T = translation.flatten()[:3]
        else:
            cam_T = _to_float32(cam_T)
            cam_T_ndim = safe_int(cam_T.ndim)
            cam_T_size = safe_int(cam_T.size)
            if cam_T_ndim == 2:
                cam_T = cam_T.flatten()[:3]
            elif cam_T_ndim == 1:
                if cam_T_size > 3:
                    cam_T = cam_T[:3]
                elif cam_T_size < 3:
                    # Pad with zeros if needed
                    cam_T = np.pad(cam_T, (0, 3 - cam_T_size), 'constant')
        
        # Convert to lists for JSON response
        result = {
            'intrinsicMat': intrinsic_mat,
        }
        
        if distortion is not None:
            result['distortion'] = distortion
        
        if image_size is not None:
            result['imageSize'] = image_size
        
        if cam_R is not None:
            cam_R_ndim = int(cam_R.ndim)
            if cam_R_ndim == 2:
                result['cam_R'] = cam_R.tolist()
            else:
                result['cam_R'] = cam_R.flatten().tolist()
        
        if cam_T is not None:
            cam_T_ndim = int(cam_T.ndim)
            if cam_T_ndim == 1:
                result['cam_T'] = cam_T.tolist()
            else:
                result['cam_T'] = cam_T.flatten().tolist()
        
        return JSONResponse(content=result)
        
    except Exception as e:
        import traceback
        error_detail = f"Failed to extract intrinsics: {str(e)}\n{traceback.format_exc()}"
        logging.error(error_detail)
        raise HTTPException(status_code=400, detail=f"Failed to extract intrinsics: {str(e)}")


@app.get("/api/healthz")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("smpl_service.main:app", host="0.0.0.0", port=8001, reload=False)
