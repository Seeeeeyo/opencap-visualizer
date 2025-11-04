#!/usr/bin/env python3
"""
Debug script for inspecting pickle files.
Usage:
    python debug_pkl.py <path_to_pkl_file>
    python debug_pkl.py wham_output.pkl
    python debug_pkl.py STS1_optimized.pkl
"""

import argparse
import gzip
import io
import pickle
import sys
import zipfile
from pathlib import Path
from typing import Any, Dict

import joblib
import numpy as np


def _decode_pickle(contents: bytes) -> Any:
    """Decode pickle using multiple methods (plain, joblib, gzip, zip)."""
    buffer = io.BytesIO(contents)

    # 1) Plain pickle
    try:
        return pickle.load(buffer)
    except Exception as e:
        print(f"  Plain pickle failed: {e}")
        buffer.seek(0)

    # 2) Joblib (handles joblib/zlib wrapped pickles)
    try:
        return joblib.load(buffer)
    except Exception as e:
        print(f"  Joblib pickle failed: {e}")
        buffer.seek(0)

    # 3) gzip-compressed pickle
    try:
        with gzip.GzipFile(fileobj=buffer) as gz:
            return pickle.load(gz)
    except Exception as e:
        print(f"  Gzip pickle failed: {e}")
        buffer.seek(0)

    # 4) Zip archive containing a pickle
    try:
        with zipfile.ZipFile(buffer) as zf:
            for name in zf.namelist():
                with zf.open(name) as inner:
                    data = inner.read()
                    try:
                        return pickle.loads(data)
                    except Exception:
                        continue
    except Exception as e:
        print(f"  Zip pickle failed: {e}")

    raise ValueError("Unable to decode pickle: unknown format")


def _inspect_value(value: Any, indent: int = 0, max_depth: int = 3, current_depth: int = 0) -> None:
    """Recursively inspect a value and print its structure."""
    prefix = "  " * indent
    
    if current_depth >= max_depth:
        print(f"{prefix}... (max depth reached)")
        return
    
    if isinstance(value, dict):
        print(f"{prefix}Dict with {len(value)} keys:")
        for key in sorted(value.keys())[:20]:  # Show first 20 keys
            print(f"{prefix}  '{key}': ", end="")
            _inspect_value(value[key], indent + 1, max_depth, current_depth + 1)
        if len(value) > 20:
            print(f"{prefix}  ... ({len(value) - 20} more keys)")
    
    elif isinstance(value, (list, tuple)):
        print(f"{prefix}{type(value).__name__} with {len(value)} items")
        if len(value) > 0:
            print(f"{prefix}  First item: ", end="")
            _inspect_value(value[0], indent + 1, max_depth, current_depth + 1)
            if len(value) > 1:
                print(f"{prefix}  ... ({len(value) - 1} more items)")
    
    elif isinstance(value, np.ndarray):
        print(f"{prefix}np.ndarray: shape={value.shape}, dtype={value.dtype}")
        if value.size > 0 and value.size <= 10:
            print(f"{prefix}  Values: {value}")
        elif value.size > 0:
            print(f"{prefix}  Min: {np.min(value)}, Max: {np.max(value)}, Mean: {np.mean(value)}")
    
    elif isinstance(value, (str, int, float, bool, type(None))):
        if isinstance(value, str) and len(value) > 100:
            print(f"{prefix}{type(value).__name__}: '{value[:100]}...' (length: {len(value)})")
        else:
            print(f"{prefix}{type(value).__name__}: {value}")
    
    else:
        print(f"{prefix}{type(value).__name__}: {repr(value)[:100]}")


def debug_pickle(file_path: Path) -> None:
    """Debug a pickle file and print detailed information."""
    print(f"=" * 80)
    print(f"Debugging pickle file: {file_path}")
    print(f"=" * 80)
    
    if not file_path.exists():
        print(f"ERROR: File not found: {file_path}")
        sys.exit(1)
    
    file_size = file_path.stat().st_size
    print(f"File size: {file_size:,} bytes ({file_size / 1024 / 1024:.2f} MB)")
    print()
    
    # Read file
    print("Attempting to decode pickle...")
    try:
        with open(file_path, "rb") as f:
            contents = f.read()
        data = _decode_pickle(contents)
        print("✓ Successfully decoded pickle!")
    except Exception as e:
        print(f"✗ Failed to decode pickle: {e}")
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("STRUCTURE INSPECTION")
    print("=" * 80)
    print()
    
    # Inspect top-level structure
    print(f"Top-level type: {type(data).__name__}")
    print()
    
    if isinstance(data, dict):
        print(f"Dictionary with {len(data)} keys:")
        print()
        
        # Show all keys first
        keys = list(data.keys())
        print("Keys:")
        for i, key in enumerate(keys, 1):
            print(f"  {i}. {key!r} ({type(data[key]).__name__})")
        print()
        
        # Detailed inspection of each key
        print("Detailed information:")
        print()
        for key in keys:
            print(f"Key: {key!r}")
            value = data[key]
            
            if isinstance(value, np.ndarray):
                print(f"  Type: numpy.ndarray")
                print(f"  Shape: {value.shape}")
                print(f"  Dtype: {value.dtype}")
                print(f"  Size: {value.size:,} elements")
                if value.size > 0:
                    print(f"  Min: {np.min(value)}")
                    print(f"  Max: {np.max(value)}")
                    print(f"  Mean: {np.mean(value)}")
                    print(f"  Std: {np.std(value)}")
                    if value.size <= 10:
                        print(f"  Values:\n{value}")
                print()
            
            elif isinstance(value, dict):
                print(f"  Type: dict")
                print(f"  Number of keys: {len(value)}")
                if len(value) <= 10:
                    print(f"  Sub-keys: {list(value.keys())}")
                else:
                    print(f"  Sub-keys: {list(value.keys())[:10]} ... ({len(value) - 10} more)")
                print()
            
            elif isinstance(value, (list, tuple)):
                print(f"  Type: {type(value).__name__}")
                print(f"  Length: {len(value)}")
                if len(value) > 0:
                    print(f"  First item type: {type(value[0]).__name__}")
                    if isinstance(value[0], np.ndarray):
                        print(f"  First item shape: {value[0].shape}")
                print()
            
            else:
                print(f"  Type: {type(value).__name__}")
                if isinstance(value, (str, int, float, bool)):
                    print(f"  Value: {value}")
                elif isinstance(value, str) and len(value) > 100:
                    print(f"  Value: {value[:100]}... (truncated, length: {len(value)})")
                else:
                    print(f"  Value: {repr(value)[:200]}")
                print()
    
    elif isinstance(data, (list, tuple)):
        print(f"{type(data).__name__} with {len(data)} items")
        print()
        if len(data) > 0:
            print("First item:")
            _inspect_value(data[0], indent=1)
            print()
    
    elif isinstance(data, np.ndarray):
        print(f"numpy.ndarray")
        print(f"  Shape: {data.shape}")
        print(f"  Dtype: {data.dtype}")
        print(f"  Size: {data.size:,} elements")
        if data.size > 0:
            print(f"  Min: {np.min(data)}")
            print(f"  Max: {np.max(data)}")
            print(f"  Mean: {np.mean(data)}")
            print(f"  Std: {np.std(data)}")
        print()
    
    else:
        print(f"Type: {type(data).__name__}")
        print(f"Value: {repr(data)[:500]}")
        print()
    
    # Memory usage estimate
    print("=" * 80)
    print("MEMORY ESTIMATES")
    print("=" * 80)
    print()
    
    def estimate_size(obj):
        """Rough estimate of object size in bytes."""
        if isinstance(obj, np.ndarray):
            return obj.nbytes
        elif isinstance(obj, dict):
            return sum(estimate_size(v) for v in obj.values())
        elif isinstance(obj, (list, tuple)):
            return sum(estimate_size(item) for item in obj)
        elif isinstance(obj, (str, bytes)):
            return len(obj)
        else:
            return sys.getsizeof(obj)
    
    try:
        total_size = estimate_size(data)
        print(f"Estimated total size: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
    except Exception as e:
        print(f"Could not estimate size: {e}")
    
    print()
    print("=" * 80)
    print("Debugging complete!")
    print("=" * 80)


def main():
    parser = argparse.ArgumentParser(
        description="Debug and inspect pickle files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python debug_pkl.py                 # defaults to wham_output.pkl
  python debug_pkl.py STS1_optimized.pkl
  python debug_pkl.py path/to/file.pkl
        """
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        type=str,
        help="Path to the pickle file to debug (defaults to wham_output.pkl)"
    )

    args = parser.parse_args()

    # Default to wham_output.pkl in the project root when no argument is provided
    if args.file is None:
        project_root = Path(__file__).resolve().parent
        default_candidates = [
            # project_root / "test/test.pkl",
            project_root / "test/STS1_optimized.pkl",
            project_root / "wham_output.pkl",
        ]
        chosen = next((p for p in default_candidates if p.exists()), default_candidates[0])
        print(f"No file provided. Defaulting to: {chosen}")
        file_path = chosen
    else:
        file_path = Path(args.file)

    debug_pickle(file_path)


if __name__ == "__main__":
    main()

