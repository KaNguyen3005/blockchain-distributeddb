from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from credential_chain.service import CredentialService


class CredentialServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.temp_dir.name)
        self.service = CredentialService(base_dir=self.base_dir)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_issue_replicates_to_all_nodes_and_verifies(self) -> None:
        issued = self.service.issue_credential(
            credential_id="CERT-001",
            recipient_name="Nguyen Van A",
            institution_name="Open Digital University",
            degree="Bachelor",
            major="Computer Science",
            issue_date="2026-03-22",
            issuer_id="issuer-001",
            metadata={"gpa": "3.8", "classification": "Excellent"},
        )

        for node in ("node-a", "node-b", "node-c"):
            target = self.base_dir / "nodes" / node / "CERT-001.json"
            self.assertTrue(target.exists(), f"Expected replica in {node}")

        verification = self.service.verify_credential("CERT-001")
        self.assertTrue(verification["valid"])
        self.assertEqual(verification["credential"]["recipient_name"], "Nguyen Van A")
        self.assertEqual(verification["reason"], "Credential verified successfully")

    def test_detects_tampering(self) -> None:
        self.service.issue_credential(
            credential_id="CERT-002",
            recipient_name="Tran Thi B",
            institution_name="Open Digital University",
            degree="Master",
            major="Data Engineering",
            issue_date="2026-03-22",
            issuer_id="issuer-002",
        )
        tampered_file = self.base_dir / "nodes" / "node-a" / "CERT-002.json"
        payload = json.loads(tampered_file.read_text(encoding="utf-8"))
        payload["major"] = "Tampered Major"
        tampered_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

        verification = self.service.verify_credential("CERT-002")
        self.assertFalse(verification["valid"])
        self.assertIn("hash does not match", verification["reason"])

    def test_revoked_credential_is_invalid(self) -> None:
        self.service.issue_credential(
            credential_id="CERT-003",
            recipient_name="Le Thi C",
            institution_name="Open Digital University",
            degree="Certificate",
            major="Blockchain Fundamentals",
            issue_date="2026-03-22",
            issuer_id="issuer-003",
        )

        revoked = self.service.revoke_credential("CERT-003")
        self.assertTrue(revoked["revoked"])
        self.assertFalse(revoked["verification"]["valid"])
        self.assertIn("revoked", revoked["verification"]["reason"])


if __name__ == "__main__":
    unittest.main()
