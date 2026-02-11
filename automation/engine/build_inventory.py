#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
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


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n")


def build_from_plan(plan_path: Path, out_path: Path, ssh_key: str = "") -> None:
    plan = yaml.safe_load(plan_path.read_text()) or {}
    default_user = _get(plan, "deployment.ssh.user", "ubuntu")
    hosts = _get(plan, "deployment.inventory.hosts", [])

    if not isinstance(hosts, list) or not hosts:
        raise SystemExit("deployment.inventory.hosts[] is required for saas mode")

    groups: dict[str, list[str]] = {}
    for i, h in enumerate(hosts, start=1):
        if not isinstance(h, dict):
            continue
        name = str(h.get("name") or f"host{i:02d}")
        ip = h.get("ip")
        if not ip:
            continue
        user = str(h.get("user") or default_user)
        gl = h.get("groups") if isinstance(h.get("groups"), list) and h.get("groups") else ["dynatrace_targets"]
        key_part = f" ansible_ssh_private_key_file={ssh_key}" if ssh_key else ""
        line = f"{name} ansible_host={ip} ansible_user={user}{key_part}"
        for g in gl:
            groups.setdefault(str(g), []).append(line)

    if not groups:
        raise SystemExit("no valid hosts found in plan")

    lines: list[str] = []
    for g in sorted(groups.keys()):
        lines.append(f"[{g}]")
        lines.extend(groups[g])
        lines.append("")
    write_text(out_path, "\n".join(lines))


def build_from_terraform(tf_dir: Path, out_path: Path, ssh_key: str = "") -> None:
    # Prefer ansible_inventory output for stability
    p = subprocess.run(["terraform", "output", "-json"], cwd=str(tf_dir), capture_output=True, text=True)
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        raise SystemExit(p.returncode)

    data = json.loads(p.stdout)
    inv = (data.get("ansible_inventory") or {}).get("value")
    if isinstance(inv, str) and inv.strip():
        write_text(out_path, inv)
        return

    hosts = (data.get("hosts") or {}).get("value")
    if not isinstance(hosts, dict) or not hosts:
        raise SystemExit("terraform must output ansible_inventory or hosts")

    groups: dict[str, list[str]] = {}
    for name, meta in hosts.items():
        if not isinstance(meta, dict):
            continue
        ip = meta.get("ip") or meta.get("public_ip") or meta.get("private_ip")
        if not ip:
            continue
        user = meta.get("user") or "azureuser"
        gl = meta.get("groups") if isinstance(meta.get("groups"), list) and meta.get("groups") else ["dynatrace_targets"]
        key_part = f" ansible_ssh_private_key_file={ssh_key}" if ssh_key else ""
        line = f"{name} ansible_host={ip} ansible_user={user}{key_part}"
        for g in gl:
            groups.setdefault(str(g), []).append(line)

    lines: list[str] = []
    for g in sorted(groups.keys()):
        lines.append(f"[{g}]")
        lines.extend(groups[g])
        lines.append("")
    write_text(out_path, "\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", required=True, help="deploy/deployment.plan.yml")
    ap.add_argument("--out", required=True, help="automation/ansible/inventory/generated.ini")
    ap.add_argument("--terraform-dir", default="infra/azure/managed", help="only used for managed mode")
    ap.add_argument("--ssh-key", default="", help="optional private key path for inventory")
    args = ap.parse_args()

    plan_path = Path(args.plan)
    if not plan_path.exists():
        print(f"plan not found: {plan_path}", file=sys.stderr)
        return 2

    plan = yaml.safe_load(plan_path.read_text()) or {}
    mode = (_get(plan, "deployment.mode", "saas") or "saas").strip().lower()
    out = Path(args.out)

    if mode == "managed":
        build_from_terraform(Path(args.terraform_dir), out, ssh_key=args.ssh_key)
    else:
        build_from_plan(plan_path, out, ssh_key=args.ssh_key)

    print(f"Wrote: {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
