from __future__ import annotations

import os
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

from local_env import bootstrap_environment, validate_environment_files  # noqa: E402

DEPENDENCY_NAMES = (
    "POSTGRES_ADMIN_PASSWORD", "IDENTITY_DB_PASSWORD", "PROFILE_DB_PASSWORD",
    "JOB_DB_PASSWORD", "MATCHING_DB_PASSWORD", "RESUME_DB_PASSWORD", "ATS_DB_PASSWORD",
    "APPLICATION_DB_PASSWORD", "COMMUNICATION_DB_PASSWORD", "ANALYTICS_DB_PASSWORD",
    "AI_GATEWAY_DB_PASSWORD", "RABBITMQ_USERNAME", "RABBITMQ_PASSWORD", "S3_ACCESS_KEY",
    "S3_SECRET_KEY",
)
KEYCLOAK_NAMES = ("KEYCLOAK_DB_PASSWORD", "KEYCLOAK_BOOTSTRAP_USERNAME", "KEYCLOAK_BOOTSTRAP_PASSWORD")


class LocalEnvironmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory(prefix="careeros-env-")
        self.root = Path(self.temporary_directory.name)
        for directory, names in (("dependencies", DEPENDENCY_NAMES), ("keycloak", KEYCLOAK_NAMES)):
            target = self.root / "infra" / directory
            target.mkdir(parents=True)
            (target / ".env.example").write_text(
                "\n".join(f"{name}=" for name in names),
                encoding="utf-8",
            )

    def tearDown(self) -> None:
        self.temporary_directory.cleanup()

    def test_bootstrap_is_private_and_idempotent(self) -> None:
        self.assertEqual(bootstrap_environment(self.root, files_only=True), ["dependencies", "keycloak"])
        paths = [self.root / "infra" / name / ".env" for name in ("dependencies", "keycloak")]
        before = [path.read_text(encoding="utf-8") for path in paths]
        self.assertEqual(bootstrap_environment(self.root, files_only=True), [])
        self.assertEqual([path.read_text(encoding="utf-8") for path in paths], before)
        if os.name != "nt":
            self.assertTrue(all(path.stat().st_mode & 0o077 == 0 for path in paths))

    def test_validation_rejects_missing_value_without_exposing_secrets(self) -> None:
        bootstrap_environment(self.root, files_only=True)
        target = self.root / "infra" / "dependencies" / ".env"
        content = target.read_text(encoding="utf-8")
        target.write_text(
            re.sub(r"^PROFILE_DB_PASSWORD=.*$", "PROFILE_DB_PASSWORD=", content, flags=re.MULTILINE),
            encoding="utf-8",
        )
        if os.name != "nt":
            target.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "Missing or empty variable PROFILE_DB_PASSWORD"):
            validate_environment_files(self.root)

    def test_validation_rejects_reused_secrets_without_printing_the_value(self) -> None:
        bootstrap_environment(self.root, files_only=True)
        target = self.root / "infra" / "dependencies" / ".env"
        content = target.read_text(encoding="utf-8")
        admin_secret = re.search(r"^POSTGRES_ADMIN_PASSWORD=(.+)$", content, re.MULTILINE).group(1)
        target.write_text(
            re.sub(r"^PROFILE_DB_PASSWORD=.*$", f"PROFILE_DB_PASSWORD={admin_secret}", content, flags=re.MULTILINE),
            encoding="utf-8",
        )
        if os.name != "nt":
            target.chmod(0o600)
        with self.assertRaises(ValueError) as context:
            validate_environment_files(self.root)
        self.assertIn("POSTGRES_ADMIN_PASSWORD and PROFILE_DB_PASSWORD", str(context.exception))
        self.assertNotIn(admin_secret, str(context.exception))

    def test_validation_rejects_placeholder_values(self) -> None:
        bootstrap_environment(self.root, files_only=True)
        target = self.root / "infra" / "dependencies" / ".env"
        content = target.read_text(encoding="utf-8")
        target.write_text(
            re.sub(r"^RABBITMQ_USERNAME=.*$", "RABBITMQ_USERNAME=local-placeholder", content, flags=re.MULTILINE),
            encoding="utf-8",
        )
        if os.name != "nt":
            target.chmod(0o600)
        with self.assertRaisesRegex(ValueError, "RABBITMQ_USERNAME.*still contains a placeholder"):
            validate_environment_files(self.root)


if __name__ == "__main__":
    unittest.main()
