from __future__ import annotations

import argparse
import json

from .service import CredentialService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Credential verification system prototype")
    parser.add_argument("--data-dir", default="data", help="Base directory for replicated nodes and blockchain ledger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    issue = subparsers.add_parser("issue", help="Issue a new credential")
    issue.add_argument("credential_id")
    issue.add_argument("recipient_name")
    issue.add_argument("institution_name")
    issue.add_argument("degree")
    issue.add_argument("major")
    issue.add_argument("issue_date")
    issue.add_argument("issuer_id")
    issue.add_argument("--metadata", default="{}", help="JSON metadata payload")

    verify = subparsers.add_parser("verify", help="Verify a credential")
    verify.add_argument("credential_id")

    revoke = subparsers.add_parser("revoke", help="Revoke a credential")
    revoke.add_argument("credential_id")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    service = CredentialService(base_dir=args.data_dir)

    if args.command == "issue":
        result = service.issue_credential(
            credential_id=args.credential_id,
            recipient_name=args.recipient_name,
            institution_name=args.institution_name,
            degree=args.degree,
            major=args.major,
            issue_date=args.issue_date,
            issuer_id=args.issuer_id,
            metadata=json.loads(args.metadata),
        )
    elif args.command == "verify":
        result = service.verify_credential(args.credential_id)
    else:
        result = service.revoke_credential(args.credential_id)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
