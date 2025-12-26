"""
Script to verify that all required models are present and can be loaded.
"""
import os
import sys

def check_file_exists(filepath, description):
    """Check if a file exists and return status."""
    if os.path.exists(filepath):
        size_mb = os.path.getsize(filepath) / (1024 * 1024)
        print(f"✓ {description}")
        print(f"  Path: {filepath}")
        print(f"  Size: {size_mb:.2f} MB")
        return True
    else:
        print(f"✗ {description}")
        print(f"  Path: {filepath}")
        print(f"  Status: NOT FOUND")
        return False

def verify_opencv_import():
    """Verify that OpenCV can be imported."""
    try:
        import cv2
        print(f"✓ OpenCV version: {cv2.__version__}")
        return True
    except ImportError as e:
        print(f"✗ OpenCV not installed: {e}")
        return False

def verify_model_loading():
    """Verify that models can be loaded by OpenCV."""
    try:
        import cv2
        script_dir = os.path.dirname(os.path.abspath(__file__))
        models_dir = os.path.join(script_dir, 'models')
        
        # Test DNN face detector
        prototxt = os.path.join(models_dir, 'deploy.prototxt')
        caffemodel = os.path.join(models_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
        
        if os.path.exists(prototxt) and os.path.exists(caffemodel):
            net = cv2.dnn.readNetFromCaffe(prototxt, caffemodel)
            print("✓ DNN face detector loaded successfully")
        else:
            print("✗ DNN face detector files missing")
            return False
        
        # Test face recognition model
        openface_model = os.path.join(models_dir, 'openface_nn4.small2.v1.t7')
        if os.path.exists(openface_model):
            recognizer = cv2.dnn.readNetFromTorch(openface_model)
            print("✓ Face recognition model loaded successfully")
        else:
            print("✗ Face recognition model missing")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error loading models: {e}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, 'models')
    
    print("=" * 60)
    print("OpenCV Face Recognition Model Verification")
    print("=" * 60)
    print()
    
    # Check OpenCV installation
    print("Checking OpenCV installation...")
    opencv_ok = verify_opencv_import()
    print()
    
    # Check model files
    print("Checking model files...")
    files_ok = True
    
    files_ok &= check_file_exists(
        os.path.join(models_dir, 'deploy.prototxt'),
        "DNN Face Detector Config (deploy.prototxt)"
    )
    print()
    
    files_ok &= check_file_exists(
        os.path.join(models_dir, 'res10_300x300_ssd_iter_140000.caffemodel'),
        "DNN Face Detector Model (res10_300x300_ssd_iter_140000.caffemodel)"
    )
    print()
    
    files_ok &= check_file_exists(
        os.path.join(models_dir, 'openface_nn4.small2.v1.t7'),
        "Face Recognition Model (openface_nn4.small2.v1.t7)"
    )
    print()
    
    # Try loading models if OpenCV is available
    if opencv_ok and files_ok:
        print("Testing model loading...")
        loading_ok = verify_model_loading()
        print()
    else:
        loading_ok = False
    
    # Summary
    print("=" * 60)
    print("Verification Summary")
    print("=" * 60)
    print(f"OpenCV Installation: {'✓ OK' if opencv_ok else '✗ FAILED'}")
    print(f"Model Files Present: {'✓ OK' if files_ok else '✗ FAILED'}")
    print(f"Model Loading Test: {'✓ OK' if loading_ok else '✗ FAILED'}")
    print()
    
    if opencv_ok and files_ok and loading_ok:
        print("✓ All checks passed! Models are ready to use.")
        return 0
    else:
        print("✗ Some checks failed. Please review the errors above.")
        if not files_ok:
            print("\nTo download models, run: python download_models.py")
        if not opencv_ok:
            print("\nTo install OpenCV, run: pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
