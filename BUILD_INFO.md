# SecureGuard Antivirus - PyInstaller Build

## Build Information

**Build Date:** November 30, 2025
**PyInstaller Version:** 6.17.0
**Python Version:** 3.12
**Build Type:** Portable Windows Executable

## Output Location

The executable and all required files are in: `dist\SecureGuard\`

## Build Summary

- **Executable:** SecureGuard.exe (15.9 MB)
- **Total Package Size:** ~118 MB
- **No Installation Required:** Portable application

## What's Included

✅ Main antivirus GUI application
✅ All required Python dependencies
✅ Configuration file (config.yaml)
✅ Virus signature database
✅ Data files and resources

## What's Excluded

To keep the package size manageable and avoid build issues, the following libraries were excluded:
- TensorFlow
- PyTorch (torch, torchvision, torchaudio)
- Keras
- Large ML/AI libraries

This means:
- Basic ML features using scikit-learn still work
- Advanced deep learning features are disabled
- The application is faster and more stable

## Running the Application

1. Navigate to `dist\SecureGuard\`
2. Double-click `SecureGuard.exe` or `Run_SecureGuard.bat`
3. The GUI will launch

## Configuration

Edit `config.yaml` in the SecureGuard folder to customize settings.

## Distribution

The entire `dist\SecureGuard\` folder can be:
- Zipped and distributed
- Copied to other Windows machines
- Run from USB drives
- Used without installation

## Spec File

The build configuration is in `SecureGuard.spec` for future rebuilds.

## Rebuilding

To rebuild the executable:
```bash
pyinstaller SecureGuard.spec --clean
```

## Notes

- First run may take 10-20 seconds to start
- Windows Defender may flag it (false positive - common with PyInstaller)
- Requires 64-bit Windows 10 or later
- Administrator rights recommended for full features
