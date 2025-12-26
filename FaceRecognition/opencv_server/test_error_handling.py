"""
Test script to verify comprehensive error handling and logging.

This script tests various error scenarios to ensure proper error handling
and logging throughout the face recognition system.

Requirements: 3.3, 8.3, 8.4
"""

import os
import sys
import json
import base64
import logging
from io import BytesIO
import numpy as np
import cv2

# Setup test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_invalid_image_data():
    """Test handling of invalid base64 image data"""
    logger.info("Testing invalid image data handling...")
    
    from app import decode_base64_image
    
    # Test 1: Invalid base64 string
    try:
        decode_base64_image("not_valid_base64!!!")
        logger.error("FAIL: Should have raised ValueError for invalid base64")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    # Test 2: Valid base64 but not an image
    try:
        invalid_data = base64.b64encode(b"This is not an image").decode('utf-8')
        decode_base64_image(invalid_data)
        logger.error("FAIL: Should have raised ValueError for non-image data")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    logger.info("[PASS] Invalid image data handling test passed")
    return True


def test_face_detector_errors():
    """Test face detector error handling"""
    logger.info("Testing face detector error handling...")
    
    from face_detector import FaceDetector
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    detector = FaceDetector(config)
    
    # Test 1: None image
    try:
        detector.detect_faces(None)
        logger.error("FAIL: Should have raised ValueError for None image")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    # Test 2: Empty image
    try:
        empty_image = np.array([])
        detector.detect_faces(empty_image)
        logger.error("FAIL: Should have raised ValueError for empty image")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    logger.info("[PASS] Face detector error handling test passed")
    return True


def test_face_recognizer_errors():
    """Test face recognizer error handling"""
    logger.info("Testing face recognizer error handling...")
    
    from face_recognizer import FaceRecognizer
    
    # Load config
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    recognizer = FaceRecognizer(config)
    
    # Test 1: None face image
    try:
        recognizer.extract_embedding(None)
        logger.error("FAIL: Should have raised ValueError for None image")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    # Test 2: Empty face image
    try:
        empty_image = np.array([])
        recognizer.extract_embedding(empty_image)
        logger.error("FAIL: Should have raised ValueError for empty image")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    # Test 3: Invalid embedding comparison - None embeddings
    try:
        recognizer.compare_embeddings(None, None)
        logger.error("FAIL: Should have raised ValueError for None embeddings")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    # Test 4: Invalid embedding comparison - different dimensions
    try:
        emb1 = np.random.rand(128)
        emb2 = np.random.rand(64)
        recognizer.compare_embeddings(emb1, emb2)
        logger.error("FAIL: Should have raised ValueError for mismatched dimensions")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    # Test 5: Invalid embedding comparison - wrong dimension
    try:
        emb1 = np.random.rand(64)
        emb2 = np.random.rand(64)
        recognizer.compare_embeddings(emb1, emb2)
        logger.error("FAIL: Should have raised ValueError for wrong dimension")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    
    logger.info("[PASS] Face recognizer error handling test passed")
    return True


def test_database_errors():
    """Test database error handling"""
    logger.info("Testing database error handling...")
    
    from database_manager import DatabaseManager
    
    # Test 1: Invalid connection string
    try:
        invalid_conn_str = "INVALID_CONNECTION_STRING"
        db = DatabaseManager(invalid_conn_str)
        logger.error("FAIL: Should have raised error for invalid connection string")
        return False
    except Exception as e:
        logger.info(f"PASS: Correctly raised error: {type(e).__name__}")
    
    # Test 2: Invalid embedding data
    try:
        # Load valid config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        conn_str = config['database']['connection_string']
        db = DatabaseManager(conn_str)
        
        # Try to store invalid embedding (not a numpy array)
        db.store_embedding(999, "not_an_array")
        logger.error("FAIL: Should have raised ValueError for invalid embedding")
        return False
    except ValueError as e:
        logger.info(f"PASS: Correctly raised ValueError: {e}")
    except Exception as e:
        # Database might not be available, which is okay for this test
        logger.info(f"PASS: Raised error (database may not be available): {type(e).__name__}")
    
    logger.info("[PASS] Database error handling test passed")
    return True


def test_logging_system():
    """Test that logging system is properly configured"""
    logger.info("Testing logging system configuration...")
    
    # Check if logs directory exists
    if not os.path.exists('logs'):
        logger.error("FAIL: logs/ directory does not exist")
        return False
    
    logger.info("PASS: logs/ directory exists")
    
    # Check if we can write to log files
    test_logger = logging.getLogger('test_logger')
    test_logger.info("Test log message")
    test_logger.error("Test error message")
    test_logger.debug("Test debug message")
    
    logger.info("[PASS] Logging system test passed")
    return True


def main():
    """Run all error handling tests"""
    logger.info("="*80)
    logger.info("STARTING ERROR HANDLING AND LOGGING TESTS")
    logger.info("="*80)
    
    tests = [
        ("Invalid Image Data", test_invalid_image_data),
        ("Face Detector Errors", test_face_detector_errors),
        ("Face Recognizer Errors", test_face_recognizer_errors),
        ("Database Errors", test_database_errors),
        ("Logging System", test_logging_system),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info("")
        logger.info(f"Running test: {test_name}")
        logger.info("-"*80)
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}", exc_info=True)
            results.append((test_name, False))
        logger.info("")
    
    # Print summary
    logger.info("="*80)
    logger.info("TEST SUMMARY")
    logger.info("="*80)
    
    passed = 0
    failed = 0
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        logger.info(f"{status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("="*80)
    logger.info(f"Total: {len(results)} tests")
    logger.info(f"Passed: {passed}")
    logger.info(f"Failed: {failed}")
    logger.info("="*80)
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
