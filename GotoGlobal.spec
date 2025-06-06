# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_data_files
from pathlib import Path

chromium_dir = Path.home() / "AppData" / "Local" / "ms-playwright" / "chromium-1169"

# Your app icon (replace with the actual path if needed)
app_icon = os.path.abspath("c2gFav.ico")  # Update this if needed

# Main analysis
a = Analysis(
    ['app.py'],
    pathex=['.', 'services', 'src'],  # Ensure your local modules are discoverable
    binaries=[],
    datas=[
        # Add Chromium browser so Playwright works in packaged app
        (chromium_dir, 'playwright/python/_impl/_driver/package/chromium'),
        
        # Add icon (if used)
        (app_icon, '.'),  # Only if you use a custom icon in your code
        
        # Collect Playwright and TinyDB data if needed
        *collect_data_files('playwright'),
        *collect_data_files('tinydb'),
    ],
    hiddenimports=[
        'playwright._impl._driver',  # Important for Playwright internal drivers
        'colorlog', 'PyQt6',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=False,  # <-- Must be False for onefile
    name='GotoGlobal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # or True if you want a terminal window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=app_icon,  # optional: keep if you're using an icon
    onefile=True     # <-- This line is required for single .exe
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='GotoGlobal',
)
