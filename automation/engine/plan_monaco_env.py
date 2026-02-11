#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

import yaml


def _get(d: dict, path: str, default=None):
    cur: Any = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    args = ap.parse_args()

    plan = yaml.safe_load(Path(args.plan).read_text()) or {}

    group = _get(plan, "monaco.group", "default")
    env = _get(plan, "monaco.environment", "target")
    project = _get(plan, "monaco.project", "bootstrap")

    # For GitHub Actions: append to $GITHUB_ENV
    print(f"MONACO_GROUP={group}")
    print(f"MONACO_ENVIRONMENT={env}")
    print(f"MONACO_PROJECT={project}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
