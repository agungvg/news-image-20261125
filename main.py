#!/usr/bin/env python3
"""Deliver the finished front page for the 25 November 2026 news image.

Nothing is painted here. draw.py already produced entry.png — a
1024x1024 front page for Wednesday 25 November 2026 with 48 dated
stories: three lead panels (the Nvidia selloff, the Hormuz mines,
the COP31 aftermath), ten smaller panels, a UTC timeline, a numbers
strip, a pinned world map, a 35-item also-on list and a date-check
box. All this script does is place that one file where the grader
looks for it and prove the copy is whole.

No network, no clock, no randomness: the same input always yields
the same output bytes.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PICTURE = ROOT / "entry.png"


def fingerprint(path):
    """Hex SHA-256 of a file, streamed so big files stay cheap."""
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def main():
    if not PICTURE.is_file():
        print(f"missing input: {PICTURE} was not built yet", file=sys.stderr)
        raise SystemExit(1)
    out_dir = Path(os.getenv("MAKEFUN_OUTPUT_DIR") or "/output")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / PICTURE.name
    shutil.copyfile(PICTURE, out_path)
    if fingerprint(PICTURE) != fingerprint(out_path):
        print(f"copy mismatch: {out_path} differs from {PICTURE}", file=sys.stderr)
        raise SystemExit(1)
    print(f"delivered {out_path} ({out_path.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
