#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--terraform-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    tf_dir = Path(args.terraform_dir)
    if not tf_dir.exists():
        print(f"terraform dir not found: {tf_dir}", file=sys.stderr)
        return 2

    p = subprocess.run(["terraform", "output", "-json"], cwd=str(tf_dir), capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        return p.returncode

    data = json.loads(p.stdout)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n")
    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
