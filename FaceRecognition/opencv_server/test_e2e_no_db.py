"""
End-to-End Testing WITHOUT Database
Tests the face recognition pipeline without database dependency
"""
import cv2
import numpy as np
import json
import sys
import os
import base64

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_detector import FaceDetector
from face_preprocessor import FacePreprocessor
from face_recognizer import FaceRecognizer


def load_config():
    """Load configuration from config.json"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.json')
    with open(config_path, 'r') as f:
        return json.load(f)


def create_test_face_image(seed=None):
    """Create a synthetic image with a face-like region"""
    if seed is not None:
        np.random.seed(seed)
    
    # Create a 640x480 image
    image = np.random.randint(100, 150, (480, 640, 3), dtype=np.uint8)
    
    # Add a brighter region to simulate a face
    face_region = np.random.randint(150, 200, (200, 200, 3), dtype=np.uint8)
    image[140:340, 220:420] = face_region
    
    return image


def image_to_base64(image):
    """Convert numpy image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return base64_str


def base64_to_image(base64_str):
    """Convert base64 string to numpy image"""
    img_data = base64.b64decode(base64_str)
    nparr = np.frombuffer(img_data, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


def test_pipeline_without_db():
    """Test the complete pipeline without database"""
    print("\n" + "=" * 60)
    print("END-TO-END TEST: Pipeline Without Database")
    print("=" * 60)
    
    try:
        # Initialize components
        print("\n[Step 1] Initializing components...")
        config = load_config()
        detector = FaceDetector(config)
        preprocessor = FacePreprocessor()
        recognizer = FaceRecognizer(config)
        print("✓ All components initialized")
        
        # Simulate registration flow
        print("\n[Step 2] Simulating registration (5 images)...")
        embeddings = []
        face_box = (220, 140, 200, 200)
        
        for i in range(5):
            # Create image
            image = create_test_face_image(seed=100 + i)
            
            # Convert to base64 and back (simulating C# → Python)
            base64_img = image_to_base64(image)
            decoded_img = base64_to_image(base64_img)
            
            # Preprocess
            preprocessed = preprocessor.preprocess_face(decoded_img, face_box)
            
            # Extract embedding
            embedding = recognizer.extract_embedding(preprocessed)
            embeddings.append(embedding)
            
            print(f"  ✓ Image {i+1}/5: Embedding shape {embedding.shape}")
        
        print(f"✓ Registration complete: {len(embeddings)} embeddings")
        
        # Simulate authentication flow
        print("\n[Step 3] Simulating authentication...")
        
        # Create test image (similar to registration)
        test_image = create_test_face_image(seed=100)
        base64_img = image_to_base64(test_image)
        decoded_img = base64_to_image(base64_img)
        preprocessed = preprocessor.preprocess_face(decoded_img, face_box)
        test_embedding = recognizer.extract_embedding(preprocessed)
        
        print(f"  ✓ Test embedding extracted: {test_embedding.shape}")
        
        # Compare against all stored embeddings
        print("\n[Step 4] Comparing against stored embeddings...")
        similarities = []
        for i, stored_emb in enumerate(embeddings):
            sim = recognizer.compare_embeddings(test_embedding, stored_emb)
            similarities.append(sim)
            print(f"  Embedding {i+1}: similarity = {sim:.4f}")
        
        max_similarity = max(similarities)
        threshold = config['face_recognition']['authentication_threshold']
        
        print(f"\n  Max similarity: {max_similarity:.4f}")
        print(f"  Threshold: {threshold}")
        
        if max_similarity >= threshold:
            print(f"  ✓ Authentication would SUCCEED")
            auth_success = True
        else:
            print(f"  ✗ Authentication would FAIL")
            auth_success = False
        
        # Test with non-matching face
        print("\n[Step 5] Testing with non-matching face...")
        different_image = create_test_face_image(seed=999)
        base64_img = image_to_base64(different_image)
        decoded_img = base64_to_image(base64_img)
        preprocessed = preprocessor.preprocess_face(decoded_img, face_box)
        different_embedding = recognizer.extract_embedding(preprocessed)
        
        similarities2 = []
        for stored_emb in embeddings:
            sim = recognizer.compare_embeddings(different_embedding, stored_emb)
            similarities2.append(sim)
        
        max_similarity2 = max(similarities2)
        print(f"  Max similarity: {max_similarity2:.4f}")
        
        if max_similarity2 < threshold:
            print(f"  ✓ Correctly rejects non-matching face")
            reject_success = True
        else:
            print(f"  ✗ Should have rejected non-matching face")
            reject_success = False
        
        # Summary
        print("\n" + "=" * 60)
        print("TEST RESULTS")
        print("=" * 60)
        print(f"✓ Component initialization: PASSED")
        print(f"✓ Registration flow (5 images): PASSED")
        print(f"✓ Embedding extraction: PASSED")
        print(f"✓ Similarity comparison: PASSED")
        print(f"{'✓' if auth_success else '✗'} Matching face authentication: {'PASSED' if auth_success else 'FAILED'}")
        print(f"{'✓' if reject_success else '✗'} Non-matching face rejection: {'PASSED' if reject_success else 'FAILED'}")
        print("=" * 60)
        
        return auth_success and reject_success
        
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = test_pipeline_without_db()
    
    if success:
        print("\n✓ End-to-end test (without DB) PASSED!")
        sys.exit(0)
    else:
        print("\n✗ End-to-end test (without DB) FAILED")
        sys.exit(1)
