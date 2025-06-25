# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import ctypes.util
from pathlib import Path
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.building.datastruct import TOC

# ---- DLL Path for Python runtime ----
python_dll_path = ctypes.util.find_library(f"python{sys.version_info.major}{sys.version_info.minor}")
if python_dll_path is None:
    raise FileNotFoundError("Cannot find system Python DLL (e.g., python311.dll)")
python_dll_tuple = (python_dll_path, '.\\GotoGlobal')

# ---- Resource Files ----
app_icon = os.path.abspath("c2gFav.ico")
autotel_icon = os.path.abspath("autoFav.ico")

datas = [
    (app_icon, "."),
    (autotel_icon, "."),
    *collect_data_files('playwright'),
    *collect_data_files("qfluentwidgets", includes=["*.qss", "*.ico", "*.png", "*.svg", "*.ttf", ".qrc"])
]

# ---- Collect your own resource files ----
resource_dir = Path("src/app/resource")
for file in resource_dir.rglob("*"):
    if file.suffix in [".qss", ".ico", ".png", ".svg", ".ttf", ".qrc"] and file.is_file():
        datas.append((str(file), str(file.parent)))

# ---- Main analysis ----
a = Analysis(
    ['main.py'],
    pathex=['.', 'services', 'src'],
    binaries=[python_dll_tuple],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["unittest", "pytest", "pydoc"],
    noarchive=False,  # necessary to keep numpy unpacked
    optimize=2,
)

# ---- Remove numpy from archive to avoid docstring optimization ----
numpy_modules = [x for x in a.pure if x[0].startswith("numpy")]
for mod in numpy_modules:
    a.pure.remove(mod)

pyz = PYZ(a.pure)

# ---- Re-add numpy files outside the archive ----
numpy_files = [(mod[1], os.path.join('numpy', os.path.basename(mod[1]))) for mod in numpy_modules]
datas += numpy_files

# ---- Build executable ----
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
    icon=app_icon
)

# ---- Final collection ----
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=["node.exe", '_uuid.pyd', 'python3.dll'],
    name='GotoGlobal',
)
