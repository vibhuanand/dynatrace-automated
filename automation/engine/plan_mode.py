#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml


def _get(d: dict, path: str, default=None):
    cur = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    args = ap.parse_args()

    p = Path(args.plan)
    if not p.exists():
        print(f"plan not found: {p}", file=sys.stderr)
        return 2

    plan = yaml.safe_load(p.read_text()) or {}
    mode = (_get(plan, "deployment.mode") or "saas").strip().lower()
    if mode not in {"saas", "managed"}:
        mode = "saas"

    print(f"mode={mode}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
