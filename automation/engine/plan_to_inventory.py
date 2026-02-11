#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Dict, List, Any

import yaml


def _get(d: dict, path: str, default=None):
    cur: Any = d
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return default
        cur = cur[key]
    return cur


def _as_list(v) -> List[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ssh-key", default="", help="optional ansible_ssh_private_key_file")
    args = ap.parse_args()

    plan = yaml.safe_load(Path(args.plan).read_text()) or {}
    default_user = _get(plan, "deployment.ssh.user", "ubuntu")

    hosts = _get(plan, "deployment.inventory.hosts", [])
    if not isinstance(hosts, list) or not hosts:
        raise SystemExit("deployment.inventory.hosts[] is required for saas mode")

    groups: Dict[str, List[str]] = {}
    for i, h in enumerate(hosts, start=1):
        name = str(h.get("name") or f"host{i:02d}")
        ip = h.get("ip")
        if not ip:
            continue
        user = str(h.get("user") or default_user)
        g_list = _as_list(h.get("groups")) or ["dynatrace_targets"]

        key_part = f" ansible_ssh_private_key_file={args.ssh_key}" if args.ssh_key else ""
        line = f"{name} ansible_host={ip} ansible_user={user}{key_part}"
        for g in g_list:
            groups.setdefault(g, []).append(line)

    out_lines: List[str] = []
    for g in sorted(groups.keys()):
        out_lines.append(f"[{g}]")
        out_lines.extend(groups[g])
        out_lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(out_lines).rstrip() + "\n")
    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
