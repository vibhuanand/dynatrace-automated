#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runtime", required=True, help="Path to build/runtime.json")
    ap.add_argument("--format", choices=["github", "bash"], default="github")
    args = ap.parse_args()

    rt = json.loads(Path(args.runtime).read_text())

    group = rt.get("monaco_group", "default")
    env = rt.get("monaco_environment", "target")
    project = rt.get("monaco_project", "bootstrap")

    if args.format == "bash":
        print(f'export MONACO_GROUP="{group}"')
        print(f'export MONACO_ENVIRONMENT="{env}"')
        print(f'export MONACO_PROJECT="{project}"')
    else:
        # github env file lines
        print(f"MONACO_GROUP={group}")
        print(f"MONACO_ENVIRONMENT={env}")
        print(f"MONACO_PROJECT={project}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
