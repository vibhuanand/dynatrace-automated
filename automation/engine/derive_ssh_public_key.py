#!/usr/bin/env python3
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--private-key", required=True, help="Path to private key file (e.g. build/id_ed25519)")
    ap.add_argument("--print-env", action="store_true", help="Print TF_VAR_ssh_public_key=... for GitHub env")
    args = ap.parse_args()

    key_path = Path(args.private_key)
    if not key_path.exists():
        print(f"missing private key: {key_path}", file=sys.stderr)
        return 2

    p = subprocess.run(
        ["ssh-keygen", "-y", "-f", str(key_path)],
        capture_output=True,
        text=True,
    )
    if p.returncode != 0:
        print(p.stderr, file=sys.stderr)
        return p.returncode

    pub = p.stdout.strip()
    if not pub:
        print("failed to derive public key", file=sys.stderr)
        return 2

    if args.print_env:
        print(f"TF_VAR_ssh_public_key={pub}")
    else:
        print(pub)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
