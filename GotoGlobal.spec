# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files

import ctypes.util

python_dll_path = ctypes.util.find_library(f"python{sys.version_info.major}{sys.version_info.minor}")
if python_dll_path is None:
    raise FileNotFoundError("Cannot find system Python DLL (e.g., python311.dll)")
python_dll_tuple = (python_dll_path, '.')



# Your app icon (replace with the actual path if needed)
app_icon = os.path.abspath("c2gFav.ico") if os.path.exists("c2gFav.ico") else None

# Main analysis
a = Analysis(
    ['app.py'],
    pathex=['.', 'services', 'src'],
    binaries=[
        python_dll_tuple  # Include Python DLL explicitly
    ],
    datas=[
        # Add icon (if used)
        *([(app_icon, '.')] if app_icon else [] ),

        # Collect Playwright and TinyDB data
        *collect_data_files('playwright'),
        *collect_data_files('tinydb'),
    ],
    hiddenimports=[
        'playwright._impl._driver',  # Important for Playwright internal drivers
        'PyQt6',
        'PyInstaller'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=2,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,
    name='GotoGlobal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=app_icon,
)

coll = COLLECT(
    exe,
    a.binaries,  # REQUIRED: This pulls in python311.dll and other critical .dll/.pyds
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["node.exe", '_uuid.pyd', 'python3.dll'],
    name='GotoGlobal',
)
