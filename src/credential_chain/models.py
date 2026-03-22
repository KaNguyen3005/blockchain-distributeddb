from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any
import json


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(slots=True)
class Credential:
    credential_id: str
    recipient_name: str
    institution_name: str
    degree: str
    major: str
    issue_date: str
    issuer_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=utc_now)
    revoked: bool = False

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def canonical_json(self) -> str:
        return json.dumps(self.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)

    def fingerprint(self) -> str:
        return sha256(self.canonical_json().encode("utf-8")).hexdigest()


@dataclass(slots=True)
class Block:
    index: int
    timestamp: str
    credential_id: str
    credential_hash: str
    previous_hash: str
    action: str

    def to_payload(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "credential_id": self.credential_id,
            "credential_hash": self.credential_hash,
            "previous_hash": self.previous_hash,
            "action": self.action,
        }

    def block_hash(self) -> str:
        payload = json.dumps(self.to_payload(), sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(payload.encode("utf-8")).hexdigest()
