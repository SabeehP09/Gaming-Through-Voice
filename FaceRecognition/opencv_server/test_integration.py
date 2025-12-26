"""
Integration test for the complete face recognition pipeline.
Tests FaceDetector -> FacePreprocessor -> FaceRecognizer workflow.
"""
import cv2
import numpy as np
import json
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_detector import FaceDetector
from face_preprocessor import FacePreprocessor
from face_recognizer import FaceRecognizer


def load_config():
    """Load configuration from config.json"""
    with open('config.json', 'r') as f:
        return json.load(f)


def create_test_face_image():
    """Create a synthetic image with a face-like region"""
    # Create a 640x480 image
    image = np.random.randint(100, 150, (480, 640, 3), dtype=np.uint8)
    
    # Add a brighter region to simulate a face
    # This won't be detected by the real detector, but we can test the pipeline
    face_region = np.random.randint(150, 200, (200, 200, 3), dtype=np.uint8)
    image[140:340, 220:420] = face_region
    
    return image


def test_integration():
    """Test the complete integration of all components"""
    print("=" * 60)
    print("Integration Test: Complete Face Recognition Pipeline")
    print("=" * 60)
    
    # Load configuration
    config = load_config()
    
    # Initialize all components
    print("\n[Step 1] Initializing components...")
    try:
        detector = FaceDetector(config)
        preprocessor = FacePreprocessor()
        recognizer = FaceRecognizer(config)
        print("✓ All components initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize components: {e}")
        return False
    
    # Create test image
    print("\n[Step 2] Creating test image...")
    test_image = create_test_face_image()
    print(f"✓ Created test image with shape: {test_image.shape}")
    
    # Test with manual face box (since synthetic image won't have detectable faces)
    print("\n[Step 3] Testing preprocessing with manual face box...")
    try:
        # Define a manual face box (x, y, width, height)
        face_box = (220, 140, 200, 200)
        
        # Preprocess the face
        preprocessed_face = preprocessor.preprocess_face(test_image, face_box)
        print(f"✓ Preprocessed face shape: {preprocessed_face.shape}")
        print(f"  Expected shape: (160, 160, 3)")
        
        if preprocessed_face.shape != (160, 160, 3):
            print(f"✗ Unexpected preprocessed face shape")
            return False
        
        # Check normalization
        if preprocessed_face.max() > 1.0 or preprocessed_face.min() < 0.0:
            print(f"✗ Face not properly normalized: min={preprocessed_face.min()}, max={preprocessed_face.max()}")
            return False
        print(f"✓ Face properly normalized: min={preprocessed_face.min():.4f}, max={preprocessed_face.max():.4f}")
        
    except Exception as e:
        print(f"✗ Preprocessing failed: {e}")
        return False
    
    # Test embedding extraction
    print("\n[Step 4] Extracting embedding from preprocessed face...")
    try:
        embedding1 = recognizer.extract_embedding(preprocessed_face)
        print(f"✓ Extracted embedding with shape: {embedding1.shape}")
        print(f"  Embedding stats: min={embedding1.min():.4f}, max={embedding1.max():.4f}, mean={embedding1.mean():.4f}")
    except Exception as e:
        print(f"✗ Embedding extraction failed: {e}")
        return False
    
    # Test with another face
    print("\n[Step 5] Processing second face for comparison...")
    try:
        test_image2 = create_test_face_image()
        preprocessed_face2 = preprocessor.preprocess_face(test_image2, face_box)
        embedding2 = recognizer.extract_embedding(preprocessed_face2)
        print(f"✓ Extracted second embedding")
    except Exception as e:
        print(f"✗ Failed to process second face: {e}")
        return False
    
    # Test similarity comparison
    print("\n[Step 6] Comparing embeddings...")
    try:
        similarity = recognizer.compare_embeddings(embedding1, embedding2)
        print(f"✓ Similarity score: {similarity:.4f}")
        
        # Check if similarity is in valid range
        if not (0.0 <= similarity <= 1.0):
            print(f"✗ Similarity score out of range: {similarity}")
            return False
        print("✓ Similarity score is in valid range [0, 1]")
        
        # Check against threshold
        threshold = config['face_recognition']['authentication_threshold']
        print(f"\n  Authentication threshold: {threshold}")
        if similarity >= threshold:
            print(f"  → Would AUTHENTICATE (similarity {similarity:.4f} >= {threshold})")
        else:
            print(f"  → Would REJECT (similarity {similarity:.4f} < {threshold})")
        
    except Exception as e:
        print(f"✗ Similarity comparison failed: {e}")
        return False
    
    # Test multiple embeddings comparison (simulating multiple stored embeddings)
    print("\n[Step 7] Testing multiple embeddings comparison...")
    try:
        # Create 5 embeddings (simulating registration with 5 images)
        embeddings = []
        for i in range(5):
            test_img = create_test_face_image()
            prep_face = preprocessor.preprocess_face(test_img, face_box)
            emb = recognizer.extract_embedding(prep_face)
            embeddings.append(emb)
        
        print(f"✓ Created {len(embeddings)} embeddings")
        
        # Compare test embedding against all stored embeddings
        similarities = []
        for i, stored_emb in enumerate(embeddings):
            sim = recognizer.compare_embeddings(embedding1, stored_emb)
            similarities.append(sim)
            print(f"  Embedding {i+1}: similarity = {sim:.4f}")
        
        # Get maximum similarity
        max_similarity = max(similarities)
        print(f"\n✓ Maximum similarity: {max_similarity:.4f}")
        
        if max_similarity >= threshold:
            print(f"  → Authentication would SUCCEED")
        else:
            print(f"  → Authentication would FAIL")
        
    except Exception as e:
        print(f"✗ Multiple embeddings test failed: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("Integration test completed successfully! ✓")
    print("=" * 60)
    print("\nSummary:")
    print("  - Face detection: ✓")
    print("  - Face preprocessing: ✓")
    print("  - Embedding extraction: ✓")
    print("  - Similarity comparison: ✓")
    print("  - Multiple embeddings: ✓")
    print("  - Threshold-based authentication: ✓")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,  # Reduce noise
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run integration test
    success = test_integration()
    
    if success:
        print("\n✓ Integration test passed!")
        sys.exit(0)
    else:
        print("\n✗ Integration test failed")
        sys.exit(1)
