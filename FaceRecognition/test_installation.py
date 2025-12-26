#!/usr/bin/env python3
"""
Test face_recognition installation
"""

print("Testing face_recognition installation...")
print("=" * 60)

try:
    import face_recognition
    print("✓ face_recognition imported successfully")
    print(f"  Version: {face_recognition.__version__}")
except ImportError as e:
    print("✗ face_recognition import failed")
    print(f"  Error: {e}")
    print("\nFix: pip install face_recognition")
    exit(1)

try:
    import dlib
    print("✓ dlib imported successfully")
    print(f"  Version: {dlib.__version__}")
except ImportError as e:
    print("✗ dlib import failed")
    print(f"  Error: {e}")
    print("\nFix: pip install dlib")
    exit(1)

try:
    import numpy
    print("✓ numpy imported successfully")
    print(f"  Version: {numpy.__version__}")
except ImportError as e:
    print("✗ numpy import failed")
    print(f"  Error: {e}")
    exit(1)

try:
    from PIL import Image
    print("✓ PIL (Pillow) imported successfully")
except ImportError as e:
    print("✗ PIL import failed")
    print(f"  Error: {e}")
    exit(1)

try:
    import flask
    print("✓ flask imported successfully")
    print(f"  Version: {flask.__version__}")
except ImportError as e:
    print("✗ flask import failed")
    print(f"  Error: {e}")
    exit(1)

try:
    from flask_cors import CORS
    print("✓ flask-cors imported successfully")
except ImportError as e:
    print("✗ flask-cors import failed")
    print(f"  Error: {e}")
    exit(1)

print("=" * 60)
print("✓ All dependencies installed correctly!")
print("\nYou can now run: python face_recognition_server.py")
