"""
Build script for VoiceListener.exe
This script creates a PyInstaller spec file with proper VOSK library inclusion
"""

import os
import sys
import subprocess

# Get the vosk library path
try:
    import vosk
    vosk_path = os.path.dirname(vosk.__file__)
    print(f"Found VOSK library at: {vosk_path}")
except ImportError:
    print("ERROR: VOSK library not found. Please install it:")
    print("  pip install vosk")
    sys.exit(1)

# Create PyInstaller spec file
spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['voice_listener.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=['vosk', '_cffi_backend'],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Add VOSK DLL files
import os
vosk_path = r'{vosk_path}'
vosk_dlls = []
for file in os.listdir(vosk_path):
    if file.endswith('.dll') or file.endswith('.pyd'):
        vosk_dlls.append((os.path.join(vosk_path, file), 'vosk'))

a.binaries += vosk_dlls

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='VoiceListener',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VoiceListener',
)
"""

# Write spec file
spec_file = "voice_listener.spec"
with open(spec_file, "w") as f:
    f.write(spec_content)

print(f"Created PyInstaller spec file: {spec_file}")
print()
print("Building VoiceListener.exe...")
print("This may take a few minutes...")
print()

# Run PyInstaller
try:
    result = subprocess.run(
        ["pyinstaller", "--clean", spec_file],
        check=True,
        capture_output=True,
        text=True
    )
    print(result.stdout)
    print()
    print("=" * 60)
    print("Build completed successfully!")
    print("=" * 60)
    print()
    print("Executable location: dist\\VoiceListener\\VoiceListener.exe")
    print()
    print("Next steps:")
    print("1. Copy dist\\VoiceListener\\VoiceListener.exe to this directory")
    print("2. Copy all files from dist\\VoiceListener\\ to this directory")
    print("3. Test by running: .\\VoiceListener.exe")
    print()
    
except subprocess.CalledProcessError as e:
    print("ERROR: Build failed!")
    print(e.stderr)
    sys.exit(1)
except FileNotFoundError:
    print("ERROR: PyInstaller not found. Please install it:")
    print("  pip install pyinstaller")
    sys.exit(1)
