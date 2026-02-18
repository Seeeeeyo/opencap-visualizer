#!/usr/bin/env python3
"""Download geometry assets from the public OpenCap S3 bucket.

Behavior:
1. Try to list all objects under geometries/ via S3 ListObjectsV2.
2. If listing is denied, fall back to candidate discovery from this repo:
   - filenames in public/dataForVisualizer/geometry-obj
   - <mesh_file> entries in any .osim file
   - attachedGeometries values in JSON files
3. Download available objects to public/s3/.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterable, List, Set

import requests

S3_BUCKET_ROOT = "https://mc-opencap-public.s3.us-west-2.amazonaws.com"
LIST_URL = f"{S3_BUCKET_ROOT}/"
PREFIX = "geometries/"


def list_s3_objects(session: requests.Session, prefix: str = PREFIX) -> List[str]:
    """Return keys from S3 list API. Raises on access denial or parse errors."""
    keys: List[str] = []
    continuation_token = None
    ns = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}

    while True:
        params = {"list-type": "2", "prefix": prefix, "max-keys": "1000"}
        if continuation_token:
            params["continuation-token"] = continuation_token
        resp = session.get(LIST_URL, params=params, timeout=30)
        resp.raise_for_status()
        root = ET.fromstring(resp.text)

        error_code = root.findtext("Code")
        if error_code == "AccessDenied":
            raise PermissionError("S3 list denied (AccessDenied).")

        for contents in root.findall("s3:Contents", ns):
            key = contents.findtext("s3:Key", default="", namespaces=ns)
            if key:
                keys.append(key)

        is_truncated = root.findtext("s3:IsTruncated", default="false", namespaces=ns)
        if is_truncated.lower() != "true":
            break
        continuation_token = root.findtext(
            "s3:NextContinuationToken", default=None, namespaces=ns
        )
        if not continuation_token:
            break

    return keys


def discover_candidate_names(repo_root: Path) -> Set[str]:
    """Discover plausible geometry object names from local repo files."""
    names: Set[str] = set()

    geom_dir = repo_root / "public" / "dataForVisualizer" / "geometry-obj"
    if geom_dir.exists():
        for f in geom_dir.iterdir():
            if f.is_file():
                names.add(f.name)

    mesh_file_pattern = re.compile(r"<mesh_file>([^<]+)</mesh_file>", re.IGNORECASE)
    for osim_path in repo_root.rglob("*.osim"):
        try:
            text = osim_path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for m in mesh_file_pattern.findall(text):
            names.add(Path(m).name)

    # Pull attachedGeometries from JSON if present; commonly *.vtp in visualizer JSON.
    for json_path in repo_root.rglob("*.json"):
        try:
            obj = json.loads(json_path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if isinstance(obj, dict) and isinstance(obj.get("bodies"), dict):
            for body in obj["bodies"].values():
                if not isinstance(body, dict):
                    continue
                geoms = body.get("attachedGeometries")
                if isinstance(geoms, list):
                    for g in geoms:
                        if isinstance(g, str):
                            names.add(Path(g).name)

    normalized: Set[str] = set()
    for name in names:
        base = Path(name).name
        if not base:
            continue
        normalized.add(base)
        stem, dot, ext = base.rpartition(".")
        if dot and ext.lower() in {"vtp", "vtk", "stl"}:
            normalized.add(f"{stem}.obj")

    return normalized


def download_key(session: requests.Session, key: str, out_dir: Path) -> str:
    """Download one key. Returns status string."""
    out_path = out_dir / Path(key).name
    url = f"{S3_BUCKET_ROOT}/{key}"
    if out_path.exists():
        return "skipped_exists"

    resp = session.get(url, stream=True, timeout=60)
    if resp.status_code == 200:
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with out_path.open("wb") as f:
            for chunk in resp.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        return "downloaded"
    if resp.status_code in {403, 404}:
        return "missing_or_forbidden"
    return f"http_{resp.status_code}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default="public/s3", help="Directory to save files")
    args = parser.parse_args()

    repo_root = Path.cwd()
    out_dir = (repo_root / args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update({"User-Agent": "opencap-visualizer-s3-downloader/1.0"})

    keys: List[str] = []
    used_fallback = False
    try:
        keys = list_s3_objects(session, prefix=PREFIX)
        print(f"Listed {len(keys)} keys from S3.")
    except Exception as e:
        used_fallback = True
        print(f"S3 listing unavailable: {e}")
        names = discover_candidate_names(repo_root)
        keys = [f"{PREFIX}{n}" for n in sorted(names)]
        print(f"Fallback candidate keys: {len(keys)}")

    downloaded = 0
    skipped_exists = 0
    missing_or_forbidden = 0
    other_errors = 0

    for key in keys:
        status = download_key(session, key, out_dir)
        if status == "downloaded":
            downloaded += 1
        elif status == "skipped_exists":
            skipped_exists += 1
        elif status == "missing_or_forbidden":
            missing_or_forbidden += 1
        else:
            other_errors += 1
            print(f"Error for {key}: {status}")

    print("\nSummary")
    print(f"Used fallback discovery: {used_fallback}")
    print(f"Target dir: {out_dir}")
    print(f"Total attempted keys: {len(keys)}")
    print(f"Downloaded: {downloaded}")
    print(f"Skipped (already exists): {skipped_exists}")
    print(f"Missing/forbidden: {missing_or_forbidden}")
    print(f"Other errors: {other_errors}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
