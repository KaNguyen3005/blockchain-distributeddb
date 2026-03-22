from __future__ import annotations

from pathlib import Path
from typing import Iterable
import json

from .models import Credential


class ReplicatedCredentialStore:
    def __init__(self, node_paths: Iterable[Path]):
        self.node_paths = [Path(path) for path in node_paths]
        for node in self.node_paths:
            node.mkdir(parents=True, exist_ok=True)

    def write(self, credential: Credential) -> list[Path]:
        written = []
        for node in self.node_paths:
            target = node / f"{credential.credential_id}.json"
            target.write_text(
                json.dumps(credential.to_dict(), indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            written.append(target)
        return written

    def read(self, credential_id: str) -> Credential | None:
        for node in self.node_paths:
            candidate = node / f"{credential_id}.json"
            if candidate.exists():
                data = json.loads(candidate.read_text(encoding="utf-8"))
                return Credential(**data)
        return None

    def revoke(self, credential_id: str) -> Credential | None:
        credential = self.read(credential_id)
        if credential is None:
            return None
        credential.revoked = True
        self.write(credential)
        return credential
