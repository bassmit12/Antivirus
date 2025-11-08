"""CLI entry point for the signature-based antivirus demo."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import database, scanner


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Signature-based antivirus demo")
    parser.add_argument(
        "--path",
        type=Path,
        required=True,
        help="File or directory to scan",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=database.DB_PATH,
        help="Path to the SQLite signature database",
    )
    parser.add_argument(
        "--recursive",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Recurse into subdirectories (default: enabled)",
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files in the scan",
    )
    parser.add_argument(
        "--save-report",
        type=Path,
        help="Optional path to save a JSON report",
    )
    parser.add_argument(
        "--init-db",
        action="store_true",
        help="Initialise the database before scanning",
    )
    return parser


def _emit_console_report(findings: list[scanner.ScanFinding]) -> None:
    if not findings:
        print("No files scanned.")
        return

    infected = [f for f in findings if f.is_malicious]
    clean = len(findings) - len(infected)

    print("Scan Results:\n")
    for finding in findings:
        status = "INFECTED" if finding.is_malicious else "CLEAN"
        suffix = f" -> matched signature: {finding.signature_name}" if finding.is_malicious else ""
        print(f"[{status:8}] {finding.path} | {finding.sha256}{suffix}")

    print("\nSummary:")
    print(f"  Files scanned : {len(findings)}")
    print(f"  Clean files  : {clean}")
    print(f"  Infected     : {len(infected)}")


def _persist_report(path: Path, findings: list[scanner.ScanFinding]) -> None:
    payload: list[dict[str, Any]] = [
        {
            "path": str(f.path),
            "sha256": f.sha256,
            "is_malicious": f.is_malicious,
            "signature_name": f.signature_name,
        }
        for f in findings
    ]
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.init_db:
        database.init_database(db_path=args.db_path, seed_path=database.SEED_PATH)

    try:
        findings = scanner.scan_path(
            target=args.path,
            db_path=args.db_path,
            recursive=args.recursive,
            include_hidden=args.include_hidden,
        )
    except FileNotFoundError as exc:
        parser.error(str(exc))
        return

    _emit_console_report(findings)

    if args.save_report:
        _persist_report(args.save_report, findings)
        print(f"Report written to {args.save_report}")


if __name__ == "__main__":
    main(sys.argv[1:])
