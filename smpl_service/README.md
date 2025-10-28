# SMPL Conversion Service

This minimal FastAPI service converts SMPL parameter `.pkl` files into frame-by-frame meshes, joints, and metadata that the web visualizer can consume.

## Running locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r smpl_service/requirements.txt
uvicorn smpl_service.main:app --host 0.0.0.0 --port 8001
```

Place your SMPL body model files inside `body_models/smpl` (they should include `SMPL_{GENDER}.pkl`).

## API

- `POST /api/smpl/sequence` — accepts a `.pkl` upload and returns base64-encoded vertices/joints, face indices, and metadata.
- `GET /api/healthz` — simple health probe.

The Vue client proxies `/api/smpl/*` requests to this service during development.
