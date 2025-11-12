"""Heuristic checks for suspicious running processes."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Sequence

import psutil

# Directories outside of standard install locations often used by malware.
SUSPICIOUS_DIR_KEYWORDS = (
    "temp",
    "appdata\\local\\temp",
    "downloads",
    "startup",
    "public",
)

SUSPICIOUS_NAME_KEYWORDS = (
    "virus",
    "hack",
    "crack",
    "keygen",
    "loader",
    "payload",
)

TRUSTED_INSTALLATION_ROOTS = (
    Path("C:/Windows").resolve(),
    Path("C:/Windows/System32").resolve(),
    Path("C:/Windows/SysWOW64").resolve(),
    Path("C:/Program Files").resolve(),
    Path("C:/Program Files (x86)").resolve(),
)


@dataclass(frozen=True)
class ProcessObservation:
    pid: int
    name: str
    exe: Optional[Path]
    username: Optional[str]
    cmdline: Optional[Sequence[str]] = None


@dataclass(frozen=True)
class HeuristicFinding:
    pid: int
    name: str
    exe: Optional[Path]
    username: Optional[str]
    score: int
    reasons: tuple[str, ...]

    @property
    def severity(self) -> str:
        if self.score >= 70:
            return "High"
        if self.score >= 40:
            return "Medium"
        if self.score > 0:
            return "Low"
        return "Info"

    @property
    def is_suspicious(self) -> bool:
        return self.score >= 40


def assess_processes(
    threshold: int = 30,
    include_system_processes: bool = False,
) -> list[HeuristicFinding]:
    """Return heuristic findings for running processes above the given threshold."""
    findings: list[HeuristicFinding] = []

    for proc in psutil.process_iter(["pid", "name", "username", "exe", "cmdline"]):
        try:
            info = proc.info
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

        username = info.get("username")
        if not include_system_processes and username and username.lower().startswith("nt authority"):
            continue

        exe = info.get("exe")
        exe_path = Path(exe) if exe else None
        cmdline = tuple(info.get("cmdline") or ()) or None

        observation = ProcessObservation(
            pid=info.get("pid", proc.pid),
            name=info.get("name") or "unknown",
            exe=exe_path,
            username=username,
            cmdline=cmdline,
        )
        finding = evaluate_observation(observation)
        if finding.score >= threshold:
            findings.append(finding)

    findings.sort(key=lambda f: f.score, reverse=True)
    return findings


def evaluate_observation(observation: ProcessObservation) -> HeuristicFinding:
    """Score a process observation and return a finding."""
    score = 0
    reasons: List[str] = []

    exe = observation.exe
    if exe is None:
        score += 10
        reasons.append("Process hides executable path")
    else:
        exe_lower = str(exe).lower()
        parent_lower = str(exe.parent).lower()

        if any(keyword in exe_lower for keyword in SUSPICIOUS_NAME_KEYWORDS):
            score += 35
            reasons.append("Executable name matches suspicious keyword")

        if any(keyword in parent_lower for keyword in SUSPICIOUS_DIR_KEYWORDS):
            score += 40
            reasons.append("Executable resides in a user/temporary directory")

        if not _is_under_trusted_root(exe):
            score += 15
            reasons.append("Executable outside trusted install locations")

        if exe.suffix.lower() not in {".exe", ".dll", ".scr", ".bat", ".ps1"}:
            score += 10
            reasons.append("Process running non-standard binary type")

    if observation.username and observation.username.lower().startswith("administrator"):
        score += 10
        reasons.append("Process running under Administrator account")

    if observation.cmdline:
        flat_cmd = " ".join(observation.cmdline).lower()
        if "--inject" in flat_cmd or "-enc" in flat_cmd or "powershell" in flat_cmd:
            score += 20
            reasons.append("Command line includes potentially dangerous flags")

    return HeuristicFinding(
        pid=observation.pid,
        name=observation.name,
        exe=observation.exe,
        username=observation.username,
        score=score,
        reasons=tuple(reasons),
    )


def _is_under_trusted_root(path: Path) -> bool:
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError):
        return False
    return any(_is_relative_to(resolved, root) for root in TRUSTED_INSTALLATION_ROOTS)


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True
