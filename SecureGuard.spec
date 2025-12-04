# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Collect all data files
added_files = [
    ('config.yaml', '.'),
    ('signature_antivirus.db', '.'),
    ('data', 'data'),
    ('src', 'src'),
]

a = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=added_files,
    hiddenimports=[
        'PIL._tkinter_finder',
        'customtkinter',
        'pywin32',
        'win32api',
        'win32con',
        'win32file',
        'win32security',
        'pywintypes',
        'winerror',
        'pefile',
        'psutil',
        'cryptography',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tensorflow',
        'torch',
        'torchvision',
        'torchaudio',
        'keras',
        'tensorboard',
        'lightning',
        'transformers',
        'datasets',
        'librosa',
        'soundfile',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='SecureGuard',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # No console window for GUI app
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='SecureGuard',
)
