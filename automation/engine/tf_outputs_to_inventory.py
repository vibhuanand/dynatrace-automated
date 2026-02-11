#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


def _tf_value(tf: dict, key: str):
    if key not in tf or not isinstance(tf[key], dict):
        return None
    return tf[key].get("value")


def _as_list(v) -> List[str]:
    if v is None:
        return []
    if isinstance(v, list):
        return [str(x) for x in v]
    return [str(v)]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tf-outputs", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--ssh-key", default="", help="optional ansible_ssh_private_key_file")
    args = ap.parse_args()

    tf = json.loads(Path(args.tf_outputs).read_text())

    inv_text = _tf_value(tf, "ansible_inventory")
    if isinstance(inv_text, str) and inv_text.strip():
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(inv_text.strip() + "\n")
        return 0

    hosts = _tf_value(tf, "hosts")
    if not isinstance(hosts, dict) or not hosts:
        raise SystemExit("terraform outputs must include ansible_inventory or hosts")

    groups: Dict[str, List[str]] = {}
    for name, meta in hosts.items():
        if not isinstance(meta, dict):
            continue
        ip = meta.get("ip") or meta.get("public_ip") or meta.get("private_ip")
        if not ip:
            continue
        user = meta.get("user") or "azureuser"
        g_list = meta.get("groups") if isinstance(meta.get("groups"), list) else ["dynatrace_targets"]

        key_part = f" ansible_ssh_private_key_file={args.ssh_key}" if args.ssh_key else ""
        line = f"{name} ansible_host={ip} ansible_user={user}{key_part}"
        for g in g_list:
            groups.setdefault(str(g), []).append(line)

    out_lines: List[str] = []
    for g in sorted(groups.keys()):
        out_lines.append(f"[{g}]")
        out_lines.extend(groups[g])
        out_lines.append("")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(out_lines).rstrip() + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
