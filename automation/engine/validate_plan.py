#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Dict

import yaml


def _get(d: dict, path: str, default=None):
    cur: Any = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def validate_rules(plan: Dict[str, Any]) -> None:
    mode = _get(plan, "deployment.mode")
    if mode not in ("saas", "managed"):
        raise ValueError("deployment.mode must be saas|managed")

    mm = _get(plan, "dynatrace.monitoring_mode", "fullstack")
    if mm not in ("fullstack", "infra-only", "discovery"):
        raise ValueError("dynatrace.monitoring_mode must be fullstack|infra-only|discovery")

    if mode == "saas":
        hosts = _get(plan, "deployment.inventory.hosts") or []
        if not isinstance(hosts, list) or not hosts:
            raise ValueError("saas mode requires deployment.inventory.hosts[]")

        for i, h in enumerate(hosts, start=1):
            if not isinstance(h, dict) or not h.get("name") or not h.get("ip"):
                raise ValueError(f"host #{i} must have name and ip")


def validate_schema(plan: Dict[str, Any], schema_path: Path) -> None:
    try:
        import json
        import jsonschema  # type: ignore
    except Exception:
        return
    schema = json.loads(schema_path.read_text())
    jsonschema.validate(instance=plan, schema=schema)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--schema", default="deploy/schema/deployment.plan.schema.json")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"plan not found: {plan_path}", file=sys.stderr)
        return 2

    plan = yaml.safe_load(plan_path.read_text()) or {}
    schema_path = Path(args.schema)
    if schema_path.exists():
        validate_schema(plan, schema_path)

    validate_rules(plan)
    print("OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
