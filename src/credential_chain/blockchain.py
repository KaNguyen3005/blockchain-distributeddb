from __future__ import annotations

from pathlib import Path
import json

from .models import Block, Credential, utc_now


class BlockchainLedger:
    def __init__(self, ledger_file: Path):
        self.ledger_file = Path(ledger_file)
        self.ledger_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.ledger_file.exists():
            self.ledger_file.write_text("[]", encoding="utf-8")

    def _load(self) -> list[dict]:
        return json.loads(self.ledger_file.read_text(encoding="utf-8"))

    def _save(self, chain: list[dict]) -> None:
        self.ledger_file.write_text(json.dumps(chain, indent=2, ensure_ascii=False), encoding="utf-8")

    def append(self, credential: Credential, action: str) -> Block:
        chain = self._load()
        previous_hash = chain[-1]["block_hash"] if chain else "GENESIS"
        block = Block(
            index=len(chain),
            timestamp=utc_now(),
            credential_id=credential.credential_id,
            credential_hash=credential.fingerprint(),
            previous_hash=previous_hash,
            action=action,
        )
        payload = block.to_payload()
        payload["block_hash"] = block.block_hash()
        chain.append(payload)
        self._save(chain)
        return block

    def verify(self, credential: Credential) -> dict[str, object]:
        chain = self._load()
        if not chain:
            return {"valid": False, "reason": "Blockchain ledger is empty"}

        previous_hash = "GENESIS"
        matched_block = None
        for raw_block in chain:
            recomputed = Block(
                index=raw_block["index"],
                timestamp=raw_block["timestamp"],
                credential_id=raw_block["credential_id"],
                credential_hash=raw_block["credential_hash"],
                previous_hash=raw_block["previous_hash"],
                action=raw_block["action"],
            ).block_hash()
            if raw_block["previous_hash"] != previous_hash:
                return {"valid": False, "reason": f"Broken chain at block {raw_block['index']}"}
            if raw_block["block_hash"] != recomputed:
                return {"valid": False, "reason": f"Tampered block detected at index {raw_block['index']}"}
            previous_hash = raw_block["block_hash"]
            if raw_block["credential_id"] == credential.credential_id:
                matched_block = raw_block

        if matched_block is None:
            return {"valid": False, "reason": "Credential not found on blockchain"}
        if matched_block["credential_hash"] != credential.fingerprint():
            return {"valid": False, "reason": "Credential content hash does not match ledger"}
        if credential.revoked:
            return {"valid": False, "reason": "Credential has been revoked"}
        return {
            "valid": True,
            "reason": "Credential verified successfully",
            "block_index": matched_block["index"],
            "block_hash": matched_block["block_hash"],
        }
