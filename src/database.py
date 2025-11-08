"""Lightweight SQLite helpers for the signature-based antivirus demo."""
from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Optional

ROOT_PATH = Path(__file__).resolve().parent.parent
DB_PATH = ROOT_PATH / "signature_antivirus.db"
SEED_PATH = ROOT_PATH / "data" / "seeds" / "signatures_seed.sql"

SCHEMA = """
BEGIN;
CREATE TABLE IF NOT EXISTS signatures (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    sha256 TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL
);
COMMIT;
"""


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    """Return a sqlite3 connection with sensible defaults."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_database(db_path: Path = DB_PATH, seed_path: Optional[Path] = SEED_PATH) -> None:
    """Create tables and load the seed signatures script."""
    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA)
        _apply_seed_script(conn, seed_path)
        conn.commit()
    finally:
        conn.close()


def _apply_seed_script(conn: sqlite3.Connection, seed_path: Optional[Path]) -> None:
    if seed_path is None:
        return
    if not seed_path.exists():
        return
    script = seed_path.read_text(encoding="utf-8")
    if not script.strip():
        return
    conn.executescript(script)


def insert_signature(
    name: str,
    sha256: str,
    db_path: Path = DB_PATH,
    created_at: Optional[str] = None,
) -> None:
    """Insert a signature if it does not already exist."""
    timestamp = created_at or datetime.now(timezone.utc).isoformat()
    conn = get_connection(db_path)
    try:
        conn.execute(
            "INSERT OR IGNORE INTO signatures (name, sha256, created_at) VALUES (?, ?, ?)",
            (name, sha256.lower(), timestamp),
        )
        conn.commit()
    finally:
        conn.close()


def fetch_known_hashes(db_path: Path = DB_PATH) -> list[sqlite3.Row]:
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("SELECT id, name, sha256, created_at FROM signatures ORDER BY id")
        return cursor.fetchall()
    finally:
        conn.close()


def lookup_signature(sha256: str, db_path: Path = DB_PATH) -> Optional[sqlite3.Row]:
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "SELECT id, name, sha256, created_at FROM signatures WHERE sha256 = ?",
            (sha256.lower(),),
        )
        return cursor.fetchone()
    finally:
        conn.close()


def bulk_insert(signatures: Iterable[tuple[str, str]], db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    try:
        rows = [
            (name, sha.lower(), datetime.now(timezone.utc).isoformat())
            for name, sha in signatures
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO signatures (name, sha256, created_at) VALUES (?, ?, ?)",
            rows,
        )
        conn.commit()
    finally:
        conn.close()


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Signature database utilities")
    parser.add_argument(
        "--init",
        action="store_true",
        help="Create the database and run the seed script",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List all known malicious signatures",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=DB_PATH,
        help="Override the path to the SQLite database",
    )
    parser.add_argument(
        "--seed-path",
        type=Path,
        default=SEED_PATH,
        help="Override the path to the seed SQL script",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    db_path: Path = args.db_path

    if args.init:
        init_database(db_path=db_path, seed_path=args.seed_path)

    if args.list:
        rows = fetch_known_hashes(db_path=db_path)
        if not rows:
            print("No signatures stored.")
            return
        for row in rows:
            print(f"{row['id']:>4} | {row['name']:<30} | {row['sha256']} | {row['created_at']}")

    if not args.init and not args.list:
        print("Nothing to do. Use --init and/or --list.")


if __name__ == "__main__":
    main()
