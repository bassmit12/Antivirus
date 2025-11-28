# 📖 User Guide - SecureGuard Antivirus

## 🚀 Getting Started

### First Time Setup

1. **Open PowerShell in the Antivirus directory**
   ```powershell
   cd D:\Antivirus
   ```

2. **Activate virtual environment**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

3. **Initialize the database** (first time only)
   ```powershell
   python -m src.database --init
   ```

4. **Launch the GUI**
   ```powershell
   python -m src.gui.app
   ```
   
   **OR simply double-click:** `run_gui.bat`

---

## 🎨 Using the GUI

### Dashboard
The main hub of your antivirus.

**What you'll see:**
- 🛡️ **Protection Status**: Shows if protection is active
- 📝 **Signature Database**: Number of known threat signatures
- 🗄️ **Quarantined Files**: Count of isolated threats

**Quick Actions:**
- **⚡ Quick Scan**: Scan Downloads folder
- **🔍 Full Scan**: Comprehensive system scan
- **📁 Custom Scan**: Choose specific files/folders

**Recent Activity:**
- View recently quarantined threats
- See detection timestamps and methods

---

### Scanner View

#### How to Scan Files

1. **Select a Path:**
   - Type the path manually, or
   - Click "Browse" to choose a folder, or
   - Use quick shortcuts:
     - 📥 Downloads
     - 🖥️ Desktop
     - 📄 Documents

2. **Start Scan:**
   - Click "▶️ Start Scan"
   - Watch real-time progress
   - See files being scanned live

3. **Review Results:**
   - Summary: Total, Clean, Suspicious, Malicious
   - Detailed threat information
   - Detection methods used
   - Threat names from various engines

#### Understanding Results

**Clean** ✅
- No threats detected
- File is safe

**Suspicious** ⚠️
- Some indicators of potential threats
- Heuristic detection triggered
- May be a false positive
- Review carefully before action

**Malicious** ❌
- Confirmed threat detected
- Multiple engines flagged it
- Immediate action recommended

---

### Quarantine Manager

#### View Quarantined Files

**Each entry shows:**
- 📄 File name and original path
- ⚠️ Threat name
- 🔍 Detection method (signature/heuristic/virustotal)
- 💾 File size
- 📅 Quarantine timestamp
- 🆔 Unique quarantine ID

#### Actions

**🔄 Refresh**
- Reload quarantine list
- Update statistics

**🧹 Cleanup Old Files**
- Deletes files older than 30 days
- Confirms before deletion
- Frees up space

**❌ Delete All**
- Permanently removes all quarantined files
- Requires confirmation
- Cannot be undone

**Individual File Actions** (Future):
- Restore file to original location
- Delete permanently
- Submit to analysis

---

### Settings

#### Detection Settings

**Signature Detection** (Toggle)
- Uses local database of known malware
- Fast, no internet required
- Recommended: ✅ ON

**Heuristic Detection** (Toggle)
- Analyzes file characteristics
- Detects unknown threats
- May have false positives
- Recommended: ✅ ON

**Cloud Lookup (VirusTotal)** (Toggle)
- Queries 70+ antivirus engines
- Requires internet and API key
- 4 requests/minute limit
- Recommended: ✅ ON (if API key configured)

**Detection Sensitivity**
- **Low**: Only flag obvious threats (fewer false positives)
- **Medium**: Balanced (recommended for daily use)
- **High**: More aggressive detection
- **Paranoid**: Maximum sensitivity (more false positives)

#### Scanning Settings

**Recursive Scanning**
- Scan subdirectories
- Recommended: ✅ ON

**Scan Hidden Files**
- Include hidden/system files
- May increase scan time
- Recommended: ❌ OFF (unless needed)

**Scan Threads**
- Number of parallel scan threads
- Higher = faster, more CPU usage
- Recommended: 4

#### Appearance

**Theme**
- System: Follow Windows theme
- Dark: Dark mode
- Light: Light mode

---

## 🔍 Detection Methods Explained

### Signature-Based Detection
**How it works:**
- Calculates SHA-256 hash of file
- Looks up hash in database
- Matches against known malware signatures

**Pros:**
- Fast and accurate
- No false positives
- Works offline

**Cons:**
- Only detects known malware
- Requires signature updates

---

### Cloud Detection (VirusTotal)
**How it works:**
- Sends file hash to VirusTotal API
- VirusTotal queries 70+ antivirus engines
- Returns aggregated results

**Pros:**
- Access to multiple engines
- Always up-to-date
- Community-driven

**Cons:**
- Requires internet
- Rate limited (4/minute)
- Privacy consideration (hash is sent)

**Threat Threshold:**
- 3+ engines flag = Malicious
- 1-2 engines flag = Suspicious

---

### Heuristic Detection
**How it works:**
Analyzes file characteristics without knowing specific signatures.

**Entropy Analysis:**
- Measures data randomness
- High entropy (>7.2) = packed/encrypted
- Common in malware

**PE File Analysis (Windows .exe):**
- Checks suspicious API imports
- Detects packer signatures
- Finds unusual entry points
- Verifies digital signatures

**String Analysis:**
- Extracts readable text
- Searches for suspicious patterns:
  - IP addresses
  - URLs and emails
  - Registry keys
  - Bitcoin addresses
  - Keywords: "password", "keylog", etc.

**Threat Scoring:**
- Each suspicious indicator adds points
- Threshold depends on sensitivity setting
- Multiple indicators = higher confidence

**Pros:**
- Detects unknown threats
- No updates needed
- Catches variants

**Cons:**
- May have false positives
- Slower than signature matching
- Requires tuning

---

## 🛡️ Best Practices

### Regular Scanning
- **Quick Scan**: Daily (Downloads, Desktop)
- **Full Scan**: Weekly (entire system)
- **Custom Scan**: After downloading files

### Sensitivity Settings
- **Daily Use**: Medium
- **High Security**: High
- **Testing Files**: Low (to reduce false positives)
- **Unknown Sources**: Paranoid

### Quarantine Management
- Review quarantined files monthly
- Delete confirmed threats permanently
- Restore false positives carefully
- Keep cleanup interval at 30 days

### API Usage
- Enable VirusTotal for best protection
- Be mindful of rate limits (4/minute)
- Cache reduces API calls automatically
- Consider upgrading API tier for heavy use

---

## 🔧 Troubleshooting

### GUI Won't Start
**Problem:** Window doesn't appear
**Solution:**
```powershell
# Check if CustomTkinter is installed
python -c "import customtkinter; print('OK')"

# Reinstall if needed
pip install --upgrade customtkinter
```

### VirusTotal Not Working
**Problem:** "VirusTotal client disabled"
**Solution:**
1. Check `.env` file exists
2. Verify API key is correct
3. Test connection:
   ```powershell
   python test_vt.py
   ```

### Scan is Slow
**Problem:** Scanning takes too long
**Solution:**
1. Increase threads in Settings (4-8)
2. Disable heuristic for quick scans
3. Exclude large media files
4. Check internet connection (for cloud lookups)

### False Positives
**Problem:** Clean files flagged as threats
**Solution:**
1. Lower sensitivity to Medium or Low
2. Review heuristic detections carefully
3. Check VirusTotal results (if <3 engines, likely false positive)
4. Disable heuristic temporarily
5. Add to whitelist (future feature)

### Database Errors
**Problem:** "Database not found"
**Solution:**
```powershell
python -m src.database --init
```

### Permission Errors
**Problem:** "Access denied"
**Solution:**
1. Run as Administrator (if scanning system folders)
2. Check file permissions
3. Skip protected system files

---

## 📊 Understanding Threat Levels

### Clean ✅
- **0 detections**
- File is safe
- No action needed

### Suspicious ⚠️
**Characteristics:**
- 1-2 engine detections, OR
- Heuristic score below malicious threshold, OR
- Unusual but not clearly malicious

**Recommended Action:**
1. Review detection details
2. Check VirusTotal report
3. Research file online
4. Quarantine if uncertain
5. Submit to analysis

### Malicious ❌
**Characteristics:**
- 3+ engine detections, OR
- High heuristic score (≥70), OR
- Known malware signature match

**Recommended Action:**
1. **Quarantine immediately**
2. Do not execute
3. Delete permanently if confirmed
4. Scan related folders
5. Change passwords if data was exposed

---

## 🎯 Common Scenarios

### Downloaded a Suspicious File
1. Navigate to Scanner view
2. Click "📥 Downloads" quick button
3. Start scan
4. Review any detections
5. Quarantine suspicious files

### Checking a USB Drive
1. Insert USB drive
2. In Scanner, browse to drive letter (e.g., E:\)
3. Enable "Scan Hidden Files" (USB malware often hidden)
4. Start scan
5. Review and quarantine threats

### System Acting Strange
1. Run Full Scan from Dashboard
2. Enable all detection engines in Settings
3. Set sensitivity to High
4. Wait for complete scan
5. Quarantine all detected threats
6. Delete quarantine after verification

### Before Opening Email Attachment
1. Save attachment to Downloads
2. Quick scan Downloads folder
3. Check results before opening
4. If suspicious, delete immediately

---

## 📱 Keyboard Shortcuts

Currently in development. Future features:
- `Ctrl+N`: New scan
- `Ctrl+R`: Refresh current view
- `F5`: Refresh quarantine
- `Ctrl+S`: Settings
- `Esc`: Cancel scan

---

## 💡 Tips & Tricks

### Speed Up Scans
- Scan specific folders instead of entire drive
- Disable cloud lookups for offline scanning
- Use signature-only mode for known files
- Increase thread count (up to CPU cores)

### Reduce False Positives
- Use Medium sensitivity for daily use
- Check VirusTotal results (majority rules)
- Research unfamiliar detections online
- Keep heuristic enabled but don't rely solely on it

### Maximize Detection
- Enable all engines (Signature + Cloud + Heuristic)
- Use High or Paranoid sensitivity
- Include hidden files
- Scan compressed archives

### Save Time
- Use quick scan shortcuts
- Enable recursive scanning
- Set up scheduled scans (future)
- Review quarantine monthly

---

## 📞 Getting Help

### Check Logs
Logs are saved in `logs/antivirus.log`:
```powershell
# View recent logs
Get-Content logs\antivirus.log -Tail 50
```

### Test Components
```powershell
# Test VirusTotal
python test_vt.py

# Test scanner
python -c "from src.scanner_enhanced import EnhancedScanner; print('OK')"

# Test GUI
python -c "import customtkinter; print('OK')"
```

### Common Issues
1. **API Key Issues**: Check `.env` file
2. **Database Issues**: Reinitialize with `--init`
3. **Import Errors**: Reinstall requirements
4. **GUI Issues**: Update CustomTkinter

---

## 🎓 Additional Resources

### API Keys
- **VirusTotal**: https://www.virustotal.com/
- **MalwareBazaar**: No key needed (unlimited)

### Documentation
- `README.md`: Project overview
- `IMPLEMENTATION_SUMMARY.md`: Technical details
- `config.yaml`: Configuration options

### Test Files
- **EICAR Test File**: Safe malware test (google "EICAR test file")
- Use only for testing, not real malware!

---

## 🔒 Security & Privacy

### What Data is Shared?
**VirusTotal:**
- File hash (SHA-256) only
- No file content sent
- Hash is one-way (cannot recreate file)

**MalwareBazaar:**
- File hash only
- No personal data

### Local Data
- Quarantined files encrypted (Fernet)
- Encryption key stored locally
- Logs contain file paths (not content)
- No telemetry or tracking

### API Key Security
- Stored in `.env` (not in git)
- Never share your API key
- Rotate if compromised
- Use read-only keys when possible

---

**Need more help? Check the logs or review the README.md!** 🚀
