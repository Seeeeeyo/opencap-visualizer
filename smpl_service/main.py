import base64
import gzip
import io
import pickle
import zipfile
from pathlib import Path
from typing import Dict, Tuple

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

    trans = first_available(["trans_world", "trans", "transl"])
    if trans is None:
        trans = np.zeros((frames, 3), dtype=np.float32)
    trans = _to_float32(trans, expected_last_dim=3)
    if trans.shape[0] == 1:
        trans = np.repeat(trans, frames, axis=0)

    fps = raw.get("fps") or raw.get("frame_rate") or 60.0
    time = raw.get("time")
    if time is None or len(time) != frames:
        time = np.arange(frames, dtype=np.float32) / float(fps)
    else:
        time = _to_float32(time)

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
    }


def _encode_float32(array: np.ndarray) -> str:
    return base64.b64encode(np.ascontiguousarray(array, dtype=np.float32).tobytes()).decode("ascii")


@app.post("/api/smpl/sequence")
async def upload_smpl_sequence(file: UploadFile = File(...)):
    contents = await file.read()
    try:
        raw = _decode_pickle(contents)
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
    return JSONResponse(response)


@app.get("/api/healthz")
def health_check():
    return {"status": "ok"}


if __name__ == "__main__":  # pragma: no cover
    import uvicorn

    uvicorn.run("smpl_service.main:app", host="0.0.0.0", port=8001, reload=False)
