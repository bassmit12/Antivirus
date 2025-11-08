from __future__ import annotations

import hashlib
from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src import database, scanner


def test_hash_file_matches_known_digest(tmp_path: Path) -> None:
    content = b"malware sample"
    sample_file = tmp_path / "sample.bin"
    sample_file.write_bytes(content)

    expected = hashlib.sha256(content).hexdigest()
    assert scanner.hash_file(sample_file) == expected


def test_scan_flags_known_signature(tmp_path: Path) -> None:
    sample_file = tmp_path / "payload.exe"
    sample_file.write_bytes(b"infected payload")

    digest = scanner.hash_file(sample_file)

    db_path = tmp_path / "signatures.db"
    seed_file = tmp_path / "seed.sql"
    seed_file.write_text(
        (
            "INSERT OR IGNORE INTO signatures (name, sha256, created_at) VALUES "
            f"('payload.exe', '{digest}', '2025-01-01T00:00:00+00:00');\n"
        ),
        encoding="utf-8",
    )

    database.init_database(db_path=db_path, seed_path=seed_file)

    findings = scanner.scan_path(sample_file, db_path=db_path)
    assert len(findings) == 1
    assert findings[0].is_malicious is True
    assert findings[0].signature_name == "payload.exe"


def test_scan_directory_non_recursive(tmp_path: Path) -> None:
    (tmp_path / "root").mkdir()
    root = tmp_path / "root"
    nested = root / "nested"
    nested.mkdir()

    clean_file = root / "clean.txt"
    clean_file.write_text("hello", encoding="utf-8")
    nested_file = nested / "ignored.txt"
    nested_file.write_text("world", encoding="utf-8")

    database.init_database(db_path=tmp_path / "db.sqlite", seed_path=None)

    findings = scanner.scan_path(root, db_path=tmp_path / "db.sqlite", recursive=False)
    scanned_paths = {f.path.name for f in findings}
    assert "clean.txt" in scanned_paths
    assert "ignored.txt" not in scanned_paths
    assert all(f.is_malicious is False for f in findings)
