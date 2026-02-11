#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

import yaml


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out-dir", required=True)
    args = ap.parse_args()

    plan = yaml.safe_load(Path(args.plan).read_text()) or {}

    # minimal defaults
    plan.setdefault("dynatrace", {})
    plan["dynatrace"].setdefault("monitoring_mode", "fullstack")
    plan["dynatrace"].setdefault("network_zone", "")
    plan["dynatrace"].setdefault("host_group", "")

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "plan.rendered.yml").write_text(yaml.safe_dump(plan, sort_keys=False))
    print(f"Wrote: {out_dir / \"plan.rendered.yml\"}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
