# SecureGuard Antivirus 🛡️

## Overview
SecureGuard is a comprehensive, multi-engine antivirus solution with signature-based, heuristic-based, and cloud-based detection capabilities. It features a modern GUI, real-time scanning, quarantine management, and integration with threat intelligence APIs like VirusTotal and MalwareBazaar.

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

## ✨ Features

### Multi-Engine Detection
- **Signature-Based Detection**: Local SQLite database with known malware signatures
- **Cloud Detection**: Integration with VirusTotal API (70+ antivirus engines)
- **MalwareBazaar Integration**: Community-driven malware database
- **Heuristic Analysis**: 
  - Entropy analysis for packed/encrypted malware
  - PE file structure analysis (Windows executables)
  - Suspicious API imports detection
  - String pattern matching (IPs, URLs, crypto wallets)
  - Obfuscation detection

### Modern GUI
- Beautiful dark/light theme support
- Real-time scan progress with visual feedback
- Dashboard with system status overview
- Quarantine manager with encrypted file storage
- Configurable settings panel
- Quick scan shortcuts (Downloads, Desktop, Documents)

### Security Features
- Encrypted quarantine with Fernet encryption
- Automatic threat detection and isolation
- Multiple sensitivity levels (low, medium, high, paranoid)
- Detailed threat reports with detection methods
- Secure API key management via environment variables

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

4. **Run a scan**
   ```powershell
   python -m src.main --path Virus
   ```
   The scanner traverses the given directory, logs file hashes, and prints a report highlighting any malicious matches.

5. **Run the automated tests (optional)**
   ```powershell
   pytest
   ```

## 📋 Usage Guide

### GUI Interface
1. **Dashboard**: View system status, recent threats, and quick scan options
2. **Scanner**: 
   - Select files/folders to scan
   - Use quick scan shortcuts for common locations
   - Monitor real-time progress
   - Review detailed detection results
3. **Quarantine**: Manage isolated threats, restore files, or delete permanently
4. **Settings**: Configure detection engines, sensitivity, and appearance

### Detection Methods
- **Signature**: Matches against local database and cloud APIs
- **Heuristic**: Analyzes file characteristics for suspicious patterns
- **Cloud**: Queries VirusTotal and MalwareBazaar

### Sensitivity Levels
- **Low**: Only flag highly suspicious files (fewer false positives)
- **Medium**: Balanced detection (recommended)
- **High**: More aggressive detection
- **Paranoid**: Maximum sensitivity (may have false positives)

## 🏗️ Architecture

```
SecureGuard Antivirus
├── Detection Engines
│   ├── Signature Scanner (Local DB + Cloud APIs)
│   ├── Heuristic Analyzer (Entropy, PE, Strings)
│   └── Behavior Monitor (Future feature)
├── Quarantine System (Encrypted storage)
├── GUI (CustomTkinter)
└── Configuration (YAML + .env)
```

## 🔧 Configuration

Edit `config.yaml` to customize:
- Detection sensitivity
- API settings and timeouts
- Scan options (threads, file size limits)
- Quarantine settings
- UI preferences

## 📊 API Integration

### VirusTotal
- **Rate Limit**: 4 requests/minute (free tier)
- **Daily Limit**: 500 requests/day
- **Caching**: 24-hour cache to minimize API calls
- **Features**: Hash lookup, 70+ engine results

### MalwareBazaar
- **Rate Limit**: None (unlimited)
- **Features**: Community malware database, hash lookup

## 🛡️ Security Notes

- Quarantined files are encrypted using Fernet (symmetric encryption)
- API keys are stored in `.env` (never commit to git)
- All file operations are logged for audit trails
- Signature database uses parameterized queries (SQL injection safe)

## 🧪 Testing

```powershell
# Run tests
pytest

# Run with coverage
pytest --cov=src tests/
```

## 📁 Project Structure

```
Antivirus/
├── src/
│   ├── gui/              # Modern GUI application
│   ├── api_integration/  # VirusTotal & MalwareBazaar clients
│   ├── heuristic/        # Heuristic detection engines
│   ├── behavior/         # Behavior monitoring (future)
│   ├── utils/            # Logging and utilities
│   ├── scanner_enhanced.py  # Multi-engine scanner
│   ├── quarantine.py     # Quarantine management
│   ├── config.py         # Configuration management
│   └── database.py       # Signature database
├── data/
│   ├── quarantine/       # Encrypted quarantined files
│   ├── api_cache/        # API response cache
│   └── seeds/            # Initial signatures
├── logs/                 # Application logs
├── config.yaml           # Main configuration
├── .env                  # API keys (not in git)
└── requirements.txt      # Python dependencies
```

## 🚧 Future Enhancements

- [ ] Real-time file system monitoring
- [ ] Process behavior analysis
- [ ] Network traffic monitoring
- [ ] Machine learning-based detection
- [ ] Scheduled scans
- [ ] System tray integration
- [ ] Auto-update signatures
- [ ] Email notifications
- [ ] Comprehensive reporting (PDF/HTML)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is for educational purposes. Use responsibly.

## ⚠️ Disclaimer

This antivirus is designed for educational and research purposes. It should not be used as a primary security solution for production systems. Always use professional, well-tested antivirus software for critical systems.
