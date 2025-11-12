from __future__ import annotations

from pathlib import Path

import pytest

from src import heuristics


def test_evaluate_observation_flags_temp_directory() -> None:
    observation = heuristics.ProcessObservation(
        pid=100,
        name="payload.exe",
        exe=Path("C:/Users/demo/AppData/Local/Temp/payload.exe"),
        username="demo",
        cmdline=("payload.exe", "--silent"),
    )
    finding = heuristics.evaluate_observation(observation)
    assert finding.score >= 70
    assert any("temporary" in reason for reason in finding.reasons)
    assert finding.severity == "High"


def test_evaluate_observation_trusted_location_low_score() -> None:
    observation = heuristics.ProcessObservation(
        pid=200,
        name="chrome.exe",
        exe=Path("C:/Program Files/Google/Chrome/Application/chrome.exe"),
        username="demo",
        cmdline=("chrome.exe",),
    )
    finding = heuristics.evaluate_observation(observation)
    assert finding.score <= 15
    assert finding.severity in {"Info", "Low"}


def test_assess_processes_respects_threshold(monkeypatch: pytest.MonkeyPatch) -> None:
    class DummyProc:
        def __init__(self, info: dict[str, object]) -> None:
            self.info = info
            self.pid = info["pid"]

    suspicious_info = {
        "pid": 300,
        "name": "badloader.exe",
        "username": "demo",
        "exe": "C:/Users/demo/AppData/Local/Temp/badloader.exe",
        "cmdline": ["badloader.exe", "--inject"],
    }
    benign_info = {
        "pid": 301,
        "name": "explorer.exe",
        "username": "NT AUTHORITY\\SYSTEM",
        "exe": "C:/Windows/explorer.exe",
        "cmdline": ["explorer.exe"],
    }

    def fake_process_iter(attrs: object) -> list[DummyProc]:
        return [DummyProc(suspicious_info), DummyProc(benign_info)]

    monkeypatch.setattr(heuristics.psutil, "process_iter", fake_process_iter)

    findings = heuristics.assess_processes(threshold=40, include_system_processes=False)
    assert len(findings) == 1
    assert findings[0].pid == suspicious_info["pid"]
    assert any("dangerous" in reason.lower() for reason in findings[0].reasons)

    findings_with_system = heuristics.assess_processes(
        threshold=40, include_system_processes=True
    )
    assert len(findings_with_system) == 1
    assert findings_with_system[0].pid == suspicious_info["pid"]
