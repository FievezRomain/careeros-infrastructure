#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from local_env import REPOSITORY_ROOT, require_python_314, validate_environment_files, validate_tools_and_compose


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate CareerOS local environment files and Compose configuration.")
    parser.add_argument("--root", type=Path, default=REPOSITORY_ROOT, help=argparse.SUPPRESS)
    parser.add_argument("--files-only", action="store_true", help=argparse.SUPPRESS)
    arguments = parser.parse_args()
    try:
        require_python_314()
        validate_environment_files(arguments.root)
        if not arguments.files_only:
            validate_tools_and_compose(arguments.root)
    except (OSError, ValueError) as error:
        print(f"Local environment validation failed: {error}", file=sys.stderr)
        return 1
    print("Local environment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
