# 🚀 Quick Start Guide - SecureGuard Antivirus

## ⚡ 30-Second Setup

```powershell
cd D:\Antivirus
.\.venv\Scripts\Activate.ps1
python -m src.gui.app
```

**OR** double-click: `run_gui.bat`

---

## 🎯 Quick Actions

| Action | How To |
|--------|--------|
| **Scan Downloads** | Dashboard → Quick Scan |
| **Scan Any Folder** | Scanner → Browse → Select → Start |
| **View Threats** | Quarantine tab |
| **Change Settings** | Settings tab → Adjust → Auto-saves |
| **Test VirusTotal** | Run: `python test_vt.py` |

---

## 🔍 Detection Methods

| Method | Speed | Accuracy | Internet |
|--------|-------|----------|----------|
| **Signature** | ⚡⚡⚡ Fast | ✅ High | ❌ No |
| **VirusTotal** | ⚡ Slow | ✅✅ Very High | ✅ Yes |
| **Heuristic** | ⚡⚡ Medium | ⚠️ Medium | ❌ No |

---

## ⚙️ Recommended Settings

**Daily Use:**
- Sensitivity: Medium
- All engines: ON
- Recursive: ON
- Hidden files: OFF

**High Security:**
- Sensitivity: High
- All engines: ON
- Recursive: ON
- Hidden files: ON

**Quick Scan:**
- Sensitivity: Low
- Signature only: ON
- Others: OFF

---

## 🎨 GUI Navigation

```
🏠 Dashboard   → System overview, quick scans
🔍 Scan        → Start scanning files/folders
⚠️  Threats    → View threat history
🗄️  Quarantine → Manage isolated files
⚙️  Settings   → Configure detection engines
```

---

## 🛡️ When to Scan

| Situation | Scan Type | Settings |
|-----------|-----------|----------|
| **New download** | Quick (Downloads) | Medium |
| **Email attachment** | Custom scan | High |
| **USB drive** | Full scan + hidden | High |
| **Weekly maintenance** | Full system scan | Medium |
| **System acting odd** | Full scan | Paranoid |

---

## 📊 Understanding Results

```
✅ Clean       → Safe, no action needed
⚠️  Suspicious → Review, possibly false positive
❌ Malicious   → Quarantine immediately!
```

**Threat Level = Detection Methods + Engine Count + Heuristic Score**

---

## 🔥 Troubleshooting

| Problem | Solution |
|---------|----------|
| GUI won't start | `pip install --upgrade customtkinter` |
| VirusTotal error | Check `.env` file, verify API key |
| Scan too slow | Increase threads (Settings) |
| False positives | Lower sensitivity to Medium/Low |
| Database error | `python -m src.database --init` |

---

## 💡 Pro Tips

1. **Enable VirusTotal** for best protection (need API key)
2. **Use Medium sensitivity** for daily scanning
3. **Scan Downloads folder** after every download
4. **Review Quarantine monthly** and delete old files
5. **Keep Heuristic ON** to catch unknown threats
6. **Check logs** when suspicious: `logs\antivirus.log`

---

## 🔑 API Setup (One-Time)

1. Get free VirusTotal API key: https://www.virustotal.com/
2. Edit `.env` file:
   ```
   VT_API_KEY=your_key_here
   ```
3. Test: `python test_vt.py`
4. Enjoy 70+ engines! 🎉

---

## 📈 Performance

| Scan Type | Time (estimate) | Files/sec |
|-----------|-----------------|-----------|
| Downloads (~100 files) | 10-30 sec | 3-10 |
| Desktop (~500 files) | 1-3 min | 3-10 |
| Full System (~50K files) | 30-120 min | 7-30 |

*Times vary based on:*
- Internet speed (for cloud lookups)
- CPU (thread count)
- Enabled engines
- File sizes

---

## 🎓 Learning Resources

| Document | Purpose |
|----------|---------|
| `README.md` | Overview & installation |
| `USER_GUIDE.md` | Detailed usage instructions |
| `IMPLEMENTATION_SUMMARY.md` | Technical details |
| `config.yaml` | All settings explained |

---

## 📞 Quick Commands

```powershell
# Launch GUI
python -m src.gui.app

# Test VirusTotal API
python test_vt.py

# Initialize database
python -m src.database --init

# List signatures
python -m src.database --list

# CLI scan (legacy)
python -m src.main --path C:\Path\To\Scan

# View logs
Get-Content logs\antivirus.log -Tail 20
```

---

## 🎯 File Detection Priority

1. **Signature Match** (local DB) → Instant malicious
2. **VirusTotal** (3+ engines) → Malicious
3. **MalwareBazaar** (found) → Malicious
4. **Heuristic** (score ≥ threshold) → Suspicious/Malicious
5. **No detection** → Clean ✅

---

## 🔒 Privacy & Security

**Local:**
- Quarantine encrypted with Fernet
- No telemetry or tracking
- All processing on your PC

**Cloud (VirusTotal):**
- Only file HASH sent (not file content)
- Hash cannot recreate file
- See their privacy policy for details

**API Key:**
- Stored in `.env` (excluded from git)
- Never share your key
- Free tier: 500 requests/day

---

## ✅ Daily Checklist

- [ ] Scan Downloads before opening files
- [ ] Check Dashboard for protection status
- [ ] Review any quarantined files
- [ ] Keep VirusTotal enabled
- [ ] Use Medium sensitivity

---

## 🚨 Emergency: Suspected Infection

1. **Stop using the system**
2. **Run Full Scan** (Paranoid sensitivity)
3. **Enable all detection engines**
4. **Include hidden files**
5. **Quarantine ALL threats**
6. **Review quarantine carefully**
7. **Delete confirmed threats**
8. **Change passwords** (from different device)
9. **Monitor system** for 24-48 hours

---

## 🎉 You're Ready!

**Your SecureGuard Antivirus includes:**
- ✅ Multi-engine detection (Signature + Cloud + Heuristic)
- ✅ VirusTotal API (70+ engines) - TESTED & WORKING!
- ✅ Modern GUI with real-time updates
- ✅ Encrypted quarantine system
- ✅ Configurable sensitivity
- ✅ Production-ready logging

**Launch now:** `python -m src.gui.app` 🛡️

---

## 📱 Contact & Support

**Check Documentation:**
- README.md
- USER_GUIDE.md
- IMPLEMENTATION_SUMMARY.md

**Review Logs:**
- `logs\antivirus.log`

**Test Components:**
- `python test_vt.py`

**Need Help?**
- Check settings configuration
- Review error messages in logs
- Verify .env file for API keys
- Ensure dependencies installed

---

**Made with ❤️ | SecureGuard Antivirus v2.0.0 | 2024**
