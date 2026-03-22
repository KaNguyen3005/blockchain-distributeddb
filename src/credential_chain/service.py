from __future__ import annotations

from pathlib import Path
from typing import Any

from .blockchain import BlockchainLedger
from .models import Credential
from .storage import ReplicatedCredentialStore


class CredentialService:
    def __init__(self, base_dir: str | Path = "data"):
        base_path = Path(base_dir)
        self.store = ReplicatedCredentialStore(
            [
                base_path / "nodes" / "node-a",
                base_path / "nodes" / "node-b",
                base_path / "nodes" / "node-c",
            ]
        )
        self.ledger = BlockchainLedger(base_path / "blockchain" / "ledger.json")

    def issue_credential(
        self,
        credential_id: str,
        recipient_name: str,
        institution_name: str,
        degree: str,
        major: str,
        issue_date: str,
        issuer_id: str,
        metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        credential = Credential(
            credential_id=credential_id,
            recipient_name=recipient_name,
            institution_name=institution_name,
            degree=degree,
            major=major,
            issue_date=issue_date,
            issuer_id=issuer_id,
            metadata=metadata or {},
        )
        self.store.write(credential)
        block = self.ledger.append(credential, action="ISSUE")
        return {
            "credential": credential.to_dict(),
            "credential_hash": credential.fingerprint(),
            "block": block.to_payload() | {"block_hash": block.block_hash()},
        }

    def verify_credential(self, credential_id: str) -> dict[str, Any]:
        credential = self.store.read(credential_id)
        if credential is None:
            return {"valid": False, "reason": "Credential does not exist in distributed storage"}
        result = self.ledger.verify(credential)
        return result | {"credential": credential.to_dict()}

    def revoke_credential(self, credential_id: str) -> dict[str, Any]:
        credential = self.store.revoke(credential_id)
        if credential is None:
            return {"revoked": False, "reason": "Credential does not exist"}
        block = self.ledger.append(credential, action="REVOKE")
        verification = self.ledger.verify(credential)
        return {
            "revoked": True,
            "credential": credential.to_dict(),
            "block": block.to_payload() | {"block_hash": block.block_hash()},
            "verification": verification,
        }
