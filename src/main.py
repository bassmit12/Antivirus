"""CLI entry point for the signature-based antivirus demo."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Optional

from . import database, heuristics, scanner


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Signature-based antivirus demo")
    parser.add_argument(
        "--path",
        type=Path,
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
    parser.add_argument(
        "--scan-processes",
        action="store_true",
        help="Run heuristic checks against running processes",
    )
    parser.add_argument(
        "--process-threshold",
        type=int,
        default=40,
        help="Minimum heuristic score to report (default: 40)",
    )
    parser.add_argument(
        "--include-system-processes",
        action="store_true",
        help="Include NT AUTHORITY/SYSTEM processes in heuristic scan",
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


def _emit_process_report(findings: list[heuristics.HeuristicFinding]) -> None:
    if not findings:
        print("No running processes exceeded the heuristic threshold.")
        return

    print("Process Heuristic Findings:\n")
    for finding in findings:
        exe = str(finding.exe) if finding.exe else "<unknown>"
        user = finding.username or "<unknown>"
        print(
            f"[{finding.severity:6}] PID {finding.pid:>5} | {finding.name} | {exe} | User: {user}"
        )
        if finding.reasons:
            joined = "; ".join(finding.reasons)
            print(f"          Reasons: {joined}")

    print(f"\nProcesses flagged : {len(findings)}")


def _persist_report(
    path: Path,
    file_findings: Optional[list[scanner.ScanFinding]],
    process_findings: Optional[list[heuristics.HeuristicFinding]],
) -> None:
    payload: dict[str, Any] = {}
    if file_findings is not None:
        payload["file_scan"] = [
            {
                "path": str(f.path),
                "sha256": f.sha256,
                "is_malicious": f.is_malicious,
                "signature_name": f.signature_name,
            }
            for f in file_findings
        ]
    if process_findings is not None:
        payload["process_scan"] = [
            {
                "pid": finding.pid,
                "name": finding.name,
                "exe": str(finding.exe) if finding.exe else None,
                "username": finding.username,
                "score": finding.score,
                "severity": finding.severity,
                "reasons": list(finding.reasons),
            }
            for finding in process_findings
        ]

    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main(argv: list[str] | None = None) -> None:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if args.init_db:
        database.init_database(db_path=args.db_path, seed_path=database.SEED_PATH)

    file_findings: Optional[list[scanner.ScanFinding]] = None
    process_findings: Optional[list[heuristics.HeuristicFinding]] = None

    if args.path is None and not args.scan_processes:
        parser.error("Provide --path for file scanning and/or --scan-processes for heuristics.")
        return

    if args.path is not None:
        try:
            file_findings = scanner.scan_path(
                target=args.path,
                db_path=args.db_path,
                recursive=args.recursive,
                include_hidden=args.include_hidden,
            )
        except FileNotFoundError as exc:
            parser.error(str(exc))
            return
        _emit_console_report(file_findings)

    if args.scan_processes:
        process_findings = heuristics.assess_processes(
            threshold=args.process_threshold,
            include_system_processes=args.include_system_processes,
        )
        print()
        _emit_process_report(process_findings)

    if args.save_report:
        _persist_report(args.save_report, file_findings, process_findings)
        print(f"Report written to {args.save_report}")


if __name__ == "__main__":
    main(sys.argv[1:])
