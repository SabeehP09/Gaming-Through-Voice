#!/usr/bin/env python3
"""
Diagnostic script for face_recognition installation issues
"""

import sys
import platform
import subprocess

print("=" * 60)
print("Face Recognition Installation Diagnostic")
print("=" * 60)
print()

# Python version
print(f"Python Version: {sys.version}")
print(f"Python Executable: {sys.executable}")
print(f"Platform: {platform.platform()}")
print(f"Architecture: {platform.architecture()[0]}")
print()

# pip version
try:
    result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                          capture_output=True, text=True)
    print(f"pip Version: {result.stdout.strip()}")
except Exception as e:
    print(f"pip check failed: {e}")
print()

# Check installed packages
print("Checking installed packages...")
print("-" * 60)

packages = [
    "dlib",
    "face_recognition",
    "numpy",
    "Pillow",
    "flask",
    "flask-cors",
    "cmake"
]

for package in packages:
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", package],
                              capture_output=True, text=True)
        if result.returncode == 0:
            # Extract version
            for line in result.stdout.split('\n'):
                if line.startswith('Version:'):
                    version = line.split(':')[1].strip()
                    print(f"✓ {package:20s} {version}")
                    break
        else:
            print(f"✗ {package:20s} NOT INSTALLED")
    except Exception as e:
        print(f"✗ {package:20s} ERROR: {e}")

print()
print("=" * 60)
print("Diagnostic Complete")
print("=" * 60)
print()

# Recommendations
print("Recommendations:")
print()

# Check Python version
py_version = sys.version_info
if py_version.major == 3 and 7 <= py_version.minor <= 11:
    print("✓ Python version is compatible (3.7-3.11)")
else:
    print("⚠ Python version may not be compatible")
    print("  Recommended: Python 3.7-3.11")
    print("  Your version: {}.{}".format(py_version.major, py_version.minor))

print()
print("If packages are missing, run:")
print("  pip install face_recognition flask flask-cors Pillow numpy")
print()
print("If dlib installation fails:")
print("  1. Install Visual C++ Build Tools")
print("  2. Or use pre-built wheel")
print("  3. Or use conda: conda install -c conda-forge dlib")
print()
