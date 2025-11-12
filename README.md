# Signature-Based Antivirus Demo

## Overview
This project implements a small signature-based antivirus demo. It scans directories, calculates SHA-256 hashes for files, and compares them against a SQLite database of known malicious signatures. Matching files are flagged in the scan report so you can inspect or quarantine them manually.

## Project Layout
```
Antivirus/
├── README.md
├── requirements.txt
├── signature_antivirus.db        # Created after running the init command
├── src/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── scanner.py
├── data/
│   └── seeds/
│       └── signatures_seed.sql
├── tests/
│   └── test_scanner.py
└── Virus/
    └── autohello_installer.exe   # Sample malicious file for the demo
```

## Features
- SQLite-backed signature store with a simple schema.
- CLI to initialise and inspect the signature database.
- Recursive directory scanner that hashes files and flags matches.
- Heuristic analyser that scores running processes for suspicious behaviour.
- Lightweight unit tests covering hashing, detection logic, and heuristics.

## Prerequisites
- Python 3.10+ (comes with the built-in `sqlite3` module).
- PowerShell (default on Windows) for the commands below.

## Setup Guide
1. **Create and activate a virtual environment**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

2. **Install dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

3. **Initialise the database**
   ```powershell
   python -m src.database --init
   ```
   This creates `signature_antivirus.db`, applies the schema, and loads seed signatures including the provided `autohello_installer.exe` sample.

4. **Run a file scan**
   ```powershell
   python -m src.main --path Virus
   ```
   The scanner traverses the given directory, logs file hashes, and prints a report highlighting any malicious matches.

5. **Add heuristic process analysis (optional)**
   ```powershell
   python -m src.main --scan-processes --process-threshold 40
   ```
   Combine with `--path` to run both checks in one command. Use `--include-system-processes` if you want to include services running under `NT AUTHORITY`.

6. **Run the automated tests (optional)**
   ```powershell
   pytest
   ```

## Extending the Demo
- Add a CLI command to submit new signatures from scanned files.
- Integrate a quarantine mechanism that copies flagged files to a safe location.
- Schedule periodic scans using Windows Task Scheduler.
- Expand the schema to track metadata such as discovery source, risk level, or remediation steps.
