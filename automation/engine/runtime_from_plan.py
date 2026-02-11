#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    plan = yaml.safe_load(Path(args.plan).read_text()) or {}

    runtime = {
        "dt_network_zone": str(_get(plan, "dynatrace.network_zone", "")),
        "dt_host_group": str(_get(plan, "dynatrace.host_group", "")),
        "dt_monitoring_mode": str(_get(plan, "dynatrace.monitoring_mode", "fullstack")),
        "monaco_group": str(_get(plan, "monaco.group", "default")),
        "monaco_environment": str(_get(plan, "monaco.environment", "target")),
        "monaco_project": str(_get(plan, "monaco.project", "bootstrap")),
    }

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(runtime, indent=2, sort_keys=True) + "\n")
    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
