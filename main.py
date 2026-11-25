#!/usr/bin/env python3
"""Hand the finished front page to the grader.

The picture itself is painted by draw.py and sits next to this
file as entry.png. This script only moves a copy of it into the
directory the harness points at with MAKEFUN_OUTPUT_DIR (or
/output when that variable is unset), then checks the copy
byte for byte against the original before announcing it.

The copy is verified with SHA-256, so a truncated or altered
delivery fails loudly instead of passing silently. No network,
no clock, no randomness: the same input always yields the
same output bytes.
"""

import hashlib
import os
import shutil
import sys
from pathlib import Path

FOLDER = Path(__file__).resolve().parent
PICTURE = FOLDER / "entry.png"


def digest(path):
    """SHA-256 hex of a file, read in one-megabyte chunks."""
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def deliver():
    if not PICTURE.is_file():
        print("entry.png is missing — run draw.py first", file=sys.stderr)
        raise SystemExit(1)
    destination = Path(os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output")
    destination.mkdir(parents=True, exist_ok=True)
    target = destination / PICTURE.name
    shutil.copyfile(PICTURE, target)
    if digest(PICTURE) != digest(target):
        print(f"copy check failed: {target} is not identical to {PICTURE}",
              file=sys.stderr)
        raise SystemExit(1)
    print(f"placed {target} — {target.stat().st_size} bytes, checksum matches")


if __name__ == "__main__":
    deliver()
