#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import os
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Path to write private key (e.g. build/id_ed25519)")
    ap.add_argument("--env", default="SSH_PRIVATE_KEY", help="Env var containing the key (raw or base64)")
    ap.add_argument("--base64", action="store_true", help="Treat env var as base64")
    args = ap.parse_args()

    val = os.environ.get(args.env, "").strip()
    if not val:
        # Not an error: caller may not need SSH (e.g. pure Terraform destroy)
        print("NO_KEY")
        return 0

    data: bytes
    if args.base64:
        data = base64.b64decode(val)
    else:
        # If it looks like base64 but user forgot flag, we still allow raw PEM/OPENSSH
        data = val.encode("utf-8")

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    try:
        os.chmod(out, 0o600)
    except Exception:
        pass

    print(str(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
