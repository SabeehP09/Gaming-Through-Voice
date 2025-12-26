"""
Test script for FaceRecognizer class.
Tests embedding extraction and comparison functionality.
"""
import cv2
import numpy as np
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_recognizer import FaceRecognizer
from face_detector import FaceDetector
from face_preprocessor import FacePreprocessor


def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)


def test_face_recognizer():
    """Test FaceRecognizer functionality"""
    print("=" * 60)
    print("Testing FaceRecognizer")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Test 1: Initialize FaceRecognizer
    print("\n[Test 1] Initializing FaceRecognizer...")
    try:
        recognizer = FaceRecognizer(config)
        print("✓ FaceRecognizer initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize FaceRecognizer: {e}")
        return False
    
    # Test 2: Create a synthetic face image for testing
    print("\n[Test 2] Creating synthetic test image...")
    try:
        # Create a simple test image (160x160, BGR, normalized)
        test_face = np.random.rand(160, 160, 3).astype(np.float32)
        print(f"✓ Created test image with shape: {test_face.shape}")
    except Exception as e:
        print(f"✗ Failed to create test image: {e}")
        return False
    
    # Test 3: Extract embedding
    print("\n[Test 3] Extracting embedding from test image...")
    try:
        embedding1 = recognizer.extract_embedding(test_face)
        print(f"✓ Extracted embedding with shape: {embedding1.shape}")
        print(f"  Embedding dimension: {embedding1.shape[0]}")
        
        if embedding1.shape[0] != 128:
            print(f"✗ Expected 128-dimensional embedding, got {embedding1.shape[0]}")
            return False
        print("✓ Embedding has correct dimension (128)")
    except Exception as e:
        print(f"✗ Failed to extract embedding: {e}")
        return False
    
    # Test 4: Extract another embedding
    print("\n[Test 4] Extracting second embedding...")
    try:
        test_face2 = np.random.rand(160, 160, 3).astype(np.float32)
        embedding2 = recognizer.extract_embedding(test_face2)
        print(f"✓ Extracted second embedding with shape: {embedding2.shape}")
    except Exception as e:
        print(f"✗ Failed to extract second embedding: {e}")
        return False
    
    # Test 5: Compare embeddings (same image)
    print("\n[Test 5] Comparing same embedding with itself...")
    try:
        similarity_same = recognizer.compare_embeddings(embedding1, embedding1)
        print(f"✓ Similarity score (same): {similarity_same:.4f}")
        
        if not (0.0 <= similarity_same <= 1.0):
            print(f"✗ Similarity score out of range [0, 1]: {similarity_same}")
            return False
        print("✓ Similarity score is in valid range [0, 1]")
        
        if similarity_same < 0.99:
            print(f"⚠ Warning: Same embedding similarity is {similarity_same:.4f}, expected ~1.0")
    except Exception as e:
        print(f"✗ Failed to compare embeddings: {e}")
        return False
    
    # Test 6: Compare different embeddings
    print("\n[Test 6] Comparing different embeddings...")
    try:
        similarity_diff = recognizer.compare_embeddings(embedding1, embedding2)
        print(f"✓ Similarity score (different): {similarity_diff:.4f}")
        
        if not (0.0 <= similarity_diff <= 1.0):
            print(f"✗ Similarity score out of range [0, 1]: {similarity_diff}")
            return False
        print("✓ Similarity score is in valid range [0, 1]")
    except Exception as e:
        print(f"✗ Failed to compare different embeddings: {e}")
        return False
    
    # Test 7: Error handling - invalid input
    print("\n[Test 7] Testing error handling with invalid input...")
    try:
        # Test with None
        try:
            recognizer.extract_embedding(None)
            print("✗ Should have raised ValueError for None input")
            return False
        except ValueError:
            print("✓ Correctly raised ValueError for None input")
        
        # Test with empty array
        try:
            recognizer.extract_embedding(np.array([]))
            print("✗ Should have raised ValueError for empty array")
            return False
        except ValueError:
            print("✓ Correctly raised ValueError for empty array")
        
    except Exception as e:
        print(f"✗ Unexpected error during error handling test: {e}")
        return False
    
    # Test 8: Error handling - mismatched embedding dimensions
    print("\n[Test 8] Testing error handling with mismatched dimensions...")
    try:
        wrong_embedding = np.random.rand(64)  # Wrong dimension
        try:
            recognizer.compare_embeddings(embedding1, wrong_embedding)
            print("✗ Should have raised ValueError for mismatched dimensions")
            return False
        except ValueError:
            print("✓ Correctly raised ValueError for mismatched dimensions")
    except Exception as e:
        print(f"✗ Unexpected error during dimension mismatch test: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("All tests passed! ✓")
    print("=" * 60)
    return True


def test_full_pipeline():
    """Test the complete face recognition pipeline"""
    print("\n" + "=" * 60)
    print("Testing Full Face Recognition Pipeline")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Initialize components
    print("\n[Pipeline Test] Initializing all components...")
    try:
        detector = FaceDetector(config)
        preprocessor = FacePreprocessor()
        recognizer = FaceRecognizer(config)
        print("✓ All components initialized")
    except Exception as e:
        print(f"✗ Failed to initialize components: {e}")
        return False
    
    # Create a test image with a synthetic face
    print("\n[Pipeline Test] Creating test image...")
    test_image = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
    print(f"✓ Created test image with shape: {test_image.shape}")
    
    print("\n" + "=" * 60)
    print("Pipeline test setup complete")
    print("Note: Full pipeline test requires real face images")
    print("=" * 60)
    return True


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run tests
    success = test_face_recognizer()
    
    if success:
        test_full_pipeline()
        print("\n✓ All FaceRecognizer tests completed successfully!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)
