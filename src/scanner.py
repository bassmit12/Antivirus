"""Directory scanner that hashes files and compares against the signature DB."""
from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Iterator, Optional

from . import database


@dataclass(frozen=True)
class ScanFinding:
    path: Path
    sha256: str
    signature_name: Optional[str]

    @property
    def is_malicious(self) -> bool:
        return self.signature_name is not None


def hash_file(path: Path, chunk_size: int = 1024 * 1024) -> str:
    """Return the lowercase SHA-256 hash of a file."""
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(chunk_size), b""):
            digest.update(chunk)
    return digest.hexdigest()


def scan_path(
    target: Path,
    db_path: Path = database.DB_PATH,
    recursive: bool = True,
    include_hidden: bool = False,
) -> list[ScanFinding]:
    """Scan the target file or directory and return the findings."""
    normalized = target.expanduser().resolve()
    if not normalized.exists():
        raise FileNotFoundError(f"Path not found: {normalized}")

    files_to_scan = list(_iter_files(normalized, recursive=recursive, include_hidden=include_hidden))
    findings: list[ScanFinding] = []
    for path in files_to_scan:
        try:
            file_hash = hash_file(path)
        except OSError as exc:
            # Skip unreadable files but keep a breadcrumb in the output.
            findings.append(
                ScanFinding(path=path, sha256=f"error:{exc.strerror or exc}", signature_name=None)
            )
            continue

        match = database.lookup_signature(file_hash, db_path=db_path)
        findings.append(
            ScanFinding(
                path=path,
                sha256=file_hash,
                signature_name=match["name"] if match else None,
            )
        )
    return findings


def _iter_files(
    target: Path,
    recursive: bool,
    include_hidden: bool,
) -> Iterator[Path]:
    if target.is_file():
        yield target
        return

    iterator: Iterable[Path]
    if recursive:
        iterator = target.rglob("*")
    else:
        iterator = target.glob("*")

    for candidate in iterator:
        if candidate.is_dir():
            continue
        if not include_hidden and _is_hidden(candidate):
            continue
        yield candidate


def _is_hidden(path: Path) -> bool:
    name = path.name
    if name.startswith('.'):
        return True
    try:
        attrs = os.stat(path, follow_symlinks=False).st_file_attributes
    except AttributeError:
        # st_file_attributes is Windows-only; fall back to dotfile check.
        return False
    # FILE_ATTRIBUTE_HIDDEN = 0x2
    return bool(attrs & 0x2)
