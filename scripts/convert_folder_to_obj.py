#!/usr/bin/env python3
"""Convert mesh files in a folder to OBJ files in a new folder.

Supported input extensions:
- .vtp (VTK XML PolyData)
- .vtk (legacy VTK PolyData)
- .stl
- .ply
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import vtk


def build_reader(path: Path):
    ext = path.suffix.lower()
    if ext == ".vtp":
        reader = vtk.vtkXMLPolyDataReader()
    elif ext == ".vtk":
        reader = vtk.vtkPolyDataReader()
    elif ext == ".stl":
        reader = vtk.vtkSTLReader()
    elif ext == ".ply":
        reader = vtk.vtkPLYReader()
    else:
        return None
    reader.SetFileName(str(path))
    return reader


def convert_file(src: Path, dst: Path) -> None:
    reader = build_reader(src)
    if reader is None:
        raise ValueError(f"Unsupported extension: {src.suffix}")

    reader.Update()
    poly = reader.GetOutput()
    if poly is None or poly.GetNumberOfPoints() == 0:
        raise RuntimeError("No polydata points found")

    tri = vtk.vtkTriangleFilter()
    tri.SetInputData(poly)
    tri.Update()

    dst.parent.mkdir(parents=True, exist_ok=True)
    writer = vtk.vtkOBJWriter()
    writer.SetFileName(str(dst))
    writer.SetInputData(tri.GetOutput())
    ok = writer.Write()
    if ok != 1:
        raise RuntimeError(f"vtkOBJWriter failed with status: {ok}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Convert supported mesh files from one folder to OBJ in another folder."
    )
    parser.add_argument("input_folder", help="Folder containing source mesh files")
    parser.add_argument("output_folder", help="Folder to write OBJ files into")
    parser.add_argument(
        "--recursive",
        action="store_true",
        help="Walk subfolders recursively (keeps relative structure in output).",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing OBJ files in output folder.",
    )
    args = parser.parse_args()

    in_dir = Path(args.input_folder).expanduser().resolve()
    out_dir = Path(args.output_folder).expanduser().resolve()
    if not in_dir.is_dir():
        print(f"Input folder does not exist: {in_dir}", file=sys.stderr)
        return 2

    exts = {".vtp", ".vtk", ".stl", ".ply"}
    pattern = "**/*" if args.recursive else "*"
    sources = [
        p for p in in_dir.glob(pattern) if p.is_file() and p.suffix.lower() in exts
    ]

    converted = 0
    skipped_existing = 0
    failed = 0

    for src in sources:
        rel = src.relative_to(in_dir)
        dst = (out_dir / rel).with_suffix(".obj")
        if dst.exists() and not args.overwrite:
            skipped_existing += 1
            continue
        try:
            convert_file(src, dst)
            converted += 1
        except Exception as exc:
            failed += 1
            print(f"Failed: {src} -> {dst} ({exc})", file=sys.stderr)

    print("Conversion complete")
    print(f"Input folder: {in_dir}")
    print(f"Output folder: {out_dir}")
    print(f"Supported source files found: {len(sources)}")
    print(f"Converted: {converted}")
    print(f"Skipped (exists): {skipped_existing}")
    print(f"Failed: {failed}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
