#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from local_env import REPOSITORY_ROOT, bootstrap_environment, require_python_314


def main() -> int:
    parser = argparse.ArgumentParser(description="Create and validate private CareerOS local environment files.")
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--files-only", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    try:
        require_python_314()
        created = bootstrap_environment(arguments.root, files_only=arguments.files_only)
    except (OSError, ValueError) as error:
        print(f"Local bootstrap failed: {error}", file=sys.stderr)
        return 1
    if created:
        print(f"Created private local environment files for: {', '.join(created)}.")
    else:
        print("Local environment files already exist; nothing was overwritten.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
