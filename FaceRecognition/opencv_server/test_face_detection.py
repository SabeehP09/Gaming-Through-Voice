"""
Simple test script to verify face detection and preprocessing modules.
"""
import cv2
import numpy as np
import json
import logging
from face_detector import FaceDetector
from face_preprocessor import FacePreprocessor

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_face_detector():
    """Test the FaceDetector class."""
    logger.info("Testing FaceDetector...")
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Initialize detector
    try:
        detector = FaceDetector(config)
        logger.info("✓ FaceDetector initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize FaceDetector: {e}")
        return False
    
    # Create a test image (simple colored rectangle)
    test_image = np.zeros((480, 640, 3), dtype=np.uint8)
    test_image[:] = (100, 150, 200)  # Fill with a color
    
    # Test detect_faces with empty image (should return empty list)
    try:
        faces = detector.detect_faces(test_image)
        logger.info(f"✓ detect_faces executed successfully, found {len(faces)} faces")
    except Exception as e:
        logger.error(f"✗ detect_faces failed: {e}")
        return False
    
    # Test with invalid image
    try:
        detector.detect_faces(None)
        logger.error("✗ Should have raised ValueError for None image")
        return False
    except ValueError:
        logger.info("✓ Correctly raised ValueError for None image")
    except Exception as e:
        logger.error(f"✗ Unexpected exception: {e}")
        return False
    
    return True


def test_face_preprocessor():
    """Test the FacePreprocessor class."""
    logger.info("\nTesting FacePreprocessor...")
    
    # Initialize preprocessor
    try:
        preprocessor = FacePreprocessor()
        logger.info("✓ FacePreprocessor initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize FacePreprocessor: {e}")
        return False
    
    # Create a test image
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    test_box = (100, 100, 200, 200)  # (x, y, w, h)
    
    # Test extract_face_region
    try:
        face_region = preprocessor.extract_face_region(test_image, test_box)
        logger.info(f"✓ extract_face_region executed successfully, shape: {face_region.shape}")
    except Exception as e:
        logger.error(f"✗ extract_face_region failed: {e}")
        return False
    
    # Test align_face
    try:
        aligned = preprocessor.align_face(face_region)
        logger.info(f"✓ align_face executed successfully, shape: {aligned.shape}")
        
        # Verify output properties
        if aligned.shape != (160, 160, 3):
            logger.error(f"✗ Incorrect output shape: {aligned.shape}, expected (160, 160, 3)")
            return False
        
        if aligned.dtype != np.float32:
            logger.error(f"✗ Incorrect dtype: {aligned.dtype}, expected float32")
            return False
        
        if aligned.min() < 0 or aligned.max() > 1:
            logger.error(f"✗ Values not normalized to [0, 1]: min={aligned.min()}, max={aligned.max()}")
            return False
        
        logger.info("✓ Output has correct shape, dtype, and normalization")
        
    except Exception as e:
        logger.error(f"✗ align_face failed: {e}")
        return False
    
    # Test preprocess_face (complete pipeline)
    try:
        preprocessed = preprocessor.preprocess_face(test_image, test_box)
        logger.info(f"✓ preprocess_face executed successfully, shape: {preprocessed.shape}")
    except Exception as e:
        logger.error(f"✗ preprocess_face failed: {e}")
        return False
    
    # Test with invalid inputs
    try:
        preprocessor.extract_face_region(None, test_box)
        logger.error("✗ Should have raised ValueError for None image")
        return False
    except ValueError:
        logger.info("✓ Correctly raised ValueError for None image")
    except Exception as e:
        logger.error(f"✗ Unexpected exception: {e}")
        return False
    
    return True


if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("Face Detection Module Test Suite")
    logger.info("=" * 60)
    
    detector_ok = test_face_detector()
    preprocessor_ok = test_face_preprocessor()
    
    logger.info("\n" + "=" * 60)
    if detector_ok and preprocessor_ok:
        logger.info("✓ All tests passed!")
    else:
        logger.error("✗ Some tests failed")
        if not detector_ok:
            logger.error("  - FaceDetector tests failed")
        if not preprocessor_ok:
            logger.error("  - FacePreprocessor tests failed")
    logger.info("=" * 60)
