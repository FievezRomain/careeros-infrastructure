from __future__ import annotations

import os
import re
import secrets
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parent.parent
Generator = Callable[[], str]


def _secret() -> str:
    return secrets.token_hex(32)


SPECIFICATIONS: tuple[tuple[str, str, str, dict[str, Generator]], ...] = (
    (
        "dependencies",
        "infra/dependencies/.env",
        "infra/dependencies/.env.example",
        {
            "POSTGRES_ADMIN_PASSWORD": _secret,
            "IDENTITY_DB_PASSWORD": _secret,
            "PROFILE_DB_PASSWORD": _secret,
            "JOB_DB_PASSWORD": _secret,
            "MATCHING_DB_PASSWORD": _secret,
            "RESUME_DB_PASSWORD": _secret,
            "ATS_DB_PASSWORD": _secret,
            "APPLICATION_DB_PASSWORD": _secret,
            "COMMUNICATION_DB_PASSWORD": _secret,
            "ANALYTICS_DB_PASSWORD": _secret,
            "AI_GATEWAY_DB_PASSWORD": _secret,
            "RABBITMQ_USERNAME": lambda: "careeros-local",
            "RABBITMQ_PASSWORD": _secret,
            "S3_ACCESS_KEY": lambda: f"careeros-local-{secrets.token_hex(12)}",
            "S3_SECRET_KEY": _secret,
        },
    ),
    (
        "keycloak",
        "infra/keycloak/.env",
        "infra/keycloak/.env.example",
        {
            "KEYCLOAK_DB_PASSWORD": _secret,
            "KEYCLOAK_BOOTSTRAP_USERNAME": lambda: "careeros-local-admin",
            "KEYCLOAK_BOOTSTRAP_PASSWORD": _secret,
        },
    ),
)

SECRET_NAMES = {
    name
    for _, _, _, values in SPECIFICATIONS
    for name in values
    if name.endswith(("_PASSWORD", "_SECRET_KEY"))
}


def require_python_314() -> None:
    if sys.version_info[:2] != (3, 14):
        raise ValueError("Python 3.14 is required for CareerOS local infrastructure tooling.")


def _assert_root(root: Path) -> None:
    for _, _, example_path, _ in SPECIFICATIONS:
        if not (root / example_path).is_file():
            raise ValueError(f"Invalid repository root: missing {example_path}.")


def _create_environment_file(root: Path, relative_path: str, values: dict[str, Generator]) -> bool:
    target = root / relative_path
    content = "\n".join(
        ["# Generated locally. Never commit or share this file."]
        + [f"{name}={generate()}" for name, generate in values.items()]
        + [""]
    )
    try:
        descriptor = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        return False
    with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
        stream.write(content)
    if os.name != "nt":
        target.chmod(0o600)
    return True


def _read_environment_file(
    root: Path,
    relative_path: str,
    values: dict[str, Generator],
) -> dict[str, str]:
    target = root / relative_path
    try:
        content = target.read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise ValueError(f"Missing {relative_path}; run the local bootstrap first.") from error

    parsed: dict[str, str] = {}
    for line_number, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, separator, value = line.partition("=")
        if not separator or not re.fullmatch(r"[A-Z][A-Z0-9_]*", name):
            raise ValueError(f"Invalid assignment in {relative_path} at line {line_number}.")
        if name in parsed:
            raise ValueError(f"Duplicate variable {name} in {relative_path}.")
        parsed[name] = value

    expected = set(values)
    unexpected = parsed.keys() - expected
    if unexpected:
        raise ValueError(f"Unexpected variable {sorted(unexpected)[0]} in {relative_path}.")
    for name in expected:
        value = parsed.get(name)
        if not value:
            raise ValueError(f"Missing or empty variable {name} in {relative_path}.")
        if any(marker in value.casefold() for marker in ("placeholder", "change-me", "changeme")):
            raise ValueError(f"Variable {name} in {relative_path} still contains a placeholder.")
        if name in SECRET_NAMES and len(value) < 32:
            raise ValueError(f"Variable {name} in {relative_path} is too short.")
    if os.name != "nt" and target.stat().st_mode & 0o077:
        raise ValueError(f"{relative_path} must not be accessible by group or other users.")
    return parsed


def validate_environment_files(root: Path = REPOSITORY_ROOT) -> None:
    root = root.resolve()
    _assert_root(root)
    secrets_by_value: dict[str, str] = {}
    for _, relative_path, _, values in SPECIFICATIONS:
        for name, value in _read_environment_file(root, relative_path, values).items():
            if name not in SECRET_NAMES:
                continue
            if previous := secrets_by_value.get(value):
                raise ValueError(f"Secret variables {previous} and {name} must be independent.")
            secrets_by_value[value] = name


def _run(command: list[str], *, cwd: Path | None = None, failure: str) -> None:
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            timeout=30,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as error:
        raise ValueError(failure) from error
    if result.returncode:
        raise ValueError(failure)


def validate_tools_and_compose(root: Path = REPOSITORY_ROOT) -> None:
    root = root.resolve()
    _run(["docker", "compose", "version"], failure="Docker Engine with the Compose plugin is required.")
    compose_commands = (
        ("dependencies", ["--env-file", "infra/dependencies/.env", "-f", "infra/dependencies/compose.local.yml"]),
        ("keycloak", ["--env-file", "infra/keycloak/.env", "-f", "infra/keycloak/compose.local.yml"]),
        ("routing", ["-f", "infra/routing/compose.local.yml"]),
    )
    for name, arguments in compose_commands:
        _run(
            ["docker", "compose", *arguments, "config", "--quiet"],
            cwd=root,
            failure=f"Compose validation failed for {name}.",
        )


def bootstrap_environment(root: Path = REPOSITORY_ROOT, *, files_only: bool = False) -> list[str]:
    root = root.resolve()
    _assert_root(root)
    if not files_only:
        _run(["docker", "compose", "version"], failure="Docker Engine with the Compose plugin is required.")
    created = [
        name
        for name, relative_path, _, values in SPECIFICATIONS
        if _create_environment_file(root, relative_path, values)
    ]
    validate_environment_files(root)
    if not files_only:
        validate_tools_and_compose(root)
    return created
