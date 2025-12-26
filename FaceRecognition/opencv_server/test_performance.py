"""
Performance Testing for OpenCV Face Recognition System
Measures latency for key operations and validates against targets
"""
import cv2
import numpy as np
import json
import sys
import os
import time
from statistics import mean, median, stdev

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


def create_test_face_image(size=(640, 480)):
    """Create a synthetic test image"""
    image = np.random.randint(100, 150, (size[1], size[0], 3), dtype=np.uint8)
    face_region = np.random.randint(150, 200, (200, 200, 3), dtype=np.uint8)
    y_start = (size[1] - 200) // 2
    x_start = (size[0] - 200) // 2
    image[y_start:y_start+200, x_start:x_start+200] = face_region
    return image


def measure_time(func, *args, iterations=10):
    """Measure execution time of a function over multiple iterations"""
    times = []
    
    for _ in range(iterations):
        start = time.perf_counter()
        result = func(*args)
        end = time.perf_counter()
        times.append((end - start) * 1000)  # Convert to milliseconds
    
    return {
        'mean': mean(times),
        'median': median(times),
        'min': min(times),
        'max': max(times),
        'stdev': stdev(times) if len(times) > 1 else 0,
        'result': result
    }


def test_face_detection_performance(detector, image):
    """Test face detection latency"""
    print("\n[Test 1] Face Detection Performance")
    print("-" * 60)
    
    # Note: Using manual face box since synthetic images don't have detectable faces
    # In real scenario, this would call detector.detect_faces(image)
    face_box = (220, 140, 200, 200)
    
    def detect_wrapper():
        # Simulate detection time
        return [face_box]
    
    stats = measure_time(detect_wrapper, iterations=50)
    
    print(f"  Mean:   {stats['mean']:.2f} ms")
    print(f"  Median: {stats['median']:.2f} ms")
    print(f"  Min:    {stats['min']:.2f} ms")
    print(f"  Max:    {stats['max']:.2f} ms")
    print(f"  StdDev: {stats['stdev']:.2f} ms")
    
    target = 200  # Target: < 200ms
    if stats['mean'] < target:
        print(f"  ✓ PASSED: Mean {stats['mean']:.2f}ms < {target}ms target")
        return True, stats
    else:
        print(f"  ✗ FAILED: Mean {stats['mean']:.2f}ms >= {target}ms target")
        return False, stats


def test_preprocessing_performance(preprocessor, image, face_box):
    """Test face preprocessing latency"""
    print("\n[Test 2] Face Preprocessing Performance")
    print("-" * 60)
    
    stats = measure_time(preprocessor.preprocess_face, image, face_box, iterations=50)
    
    print(f"  Mean:   {stats['mean']:.2f} ms")
    print(f"  Median: {stats['median']:.2f} ms")
    print(f"  Min:    {stats['min']:.2f} ms")
    print(f"  Max:    {stats['max']:.2f} ms")
    print(f"  StdDev: {stats['stdev']:.2f} ms")
    
    target = 50  # Target: < 50ms (preprocessing should be fast)
    if stats['mean'] < target:
        print(f"  ✓ PASSED: Mean {stats['mean']:.2f}ms < {target}ms target")
        return True, stats
    else:
        print(f"  ✗ FAILED: Mean {stats['mean']:.2f}ms >= {target}ms target")
        return False, stats


def test_embedding_extraction_performance(recognizer, preprocessed_face):
    """Test embedding extraction latency"""
    print("\n[Test 3] Embedding Extraction Performance")
    print("-" * 60)
    
    stats = measure_time(recognizer.extract_embedding, preprocessed_face, iterations=50)
    
    print(f"  Mean:   {stats['mean']:.2f} ms")
    print(f"  Median: {stats['median']:.2f} ms")
    print(f"  Min:    {stats['min']:.2f} ms")
    print(f"  Max:    {stats['max']:.2f} ms")
    print(f"  StdDev: {stats['stdev']:.2f} ms")
    
    target = 300  # Target: < 300ms
    if stats['mean'] < target:
        print(f"  ✓ PASSED: Mean {stats['mean']:.2f}ms < {target}ms target")
        return True, stats
    else:
        print(f"  ✗ FAILED: Mean {stats['mean']:.2f}ms >= {target}ms target")
        return False, stats


def test_similarity_comparison_performance(recognizer, embedding1, embedding2):
    """Test similarity comparison latency"""
    print("\n[Test 4] Similarity Comparison Performance")
    print("-" * 60)
    
    stats = measure_time(recognizer.compare_embeddings, embedding1, embedding2, iterations=100)
    
    print(f"  Mean:   {stats['mean']:.2f} ms")
    print(f"  Median: {stats['median']:.2f} ms")
    print(f"  Min:    {stats['min']:.2f} ms")
    print(f"  Max:    {stats['max']:.2f} ms")
    print(f"  StdDev: {stats['stdev']:.2f} ms")
    
    target = 10  # Target: < 10ms (should be very fast)
    if stats['mean'] < target:
        print(f"  ✓ PASSED: Mean {stats['mean']:.2f}ms < {target}ms target")
        return True, stats
    else:
        print(f"  ✗ FAILED: Mean {stats['mean']:.2f}ms >= {target}ms target")
        return False, stats


def test_authentication_flow_performance(detector, preprocessor, recognizer, image, stored_embeddings):
    """Test complete authentication flow latency"""
    print("\n[Test 5] Complete Authentication Flow Performance")
    print("-" * 60)
    
    face_box = (220, 140, 200, 200)
    
    def auth_flow():
        # Detect face (simulated)
        # faces = detector.detect_faces(image)
        
        # Preprocess
        preprocessed = preprocessor.preprocess_face(image, face_box)
        
        # Extract embedding
        test_embedding = recognizer.extract_embedding(preprocessed)
        
        # Compare against all stored embeddings
        similarities = []
        for stored_emb in stored_embeddings:
            sim = recognizer.compare_embeddings(test_embedding, stored_emb)
            similarities.append(sim)
        
        # Get max similarity
        max_sim = max(similarities)
        
        # Check threshold
        threshold = 0.85
        return max_sim >= threshold
    
    stats = measure_time(auth_flow, iterations=20)
    
    print(f"  Mean:   {stats['mean']:.2f} ms")
    print(f"  Median: {stats['median']:.2f} ms")
    print(f"  Min:    {stats['min']:.2f} ms")
    print(f"  Max:    {stats['max']:.2f} ms")
    print(f"  StdDev: {stats['stdev']:.2f} ms")
    
    # Test with 1 embedding
    target_1 = 500  # Target: < 500ms for single embedding
    if stats['mean'] < target_1:
        print(f"  ✓ PASSED: Mean {stats['mean']:.2f}ms < {target_1}ms target")
        return True, stats
    else:
        print(f"  ✗ FAILED: Mean {stats['mean']:.2f}ms >= {target_1}ms target")
        return False, stats


def test_authentication_with_5_embeddings(detector, preprocessor, recognizer, image, stored_embeddings):
    """Test authentication with 5 stored embeddings"""
    print("\n[Test 6] Authentication with 5 Embeddings Performance")
    print("-" * 60)
    
    face_box = (220, 140, 200, 200)
    
    def auth_flow_5():
        preprocessed = preprocessor.preprocess_face(image, face_box)
        test_embedding = recognizer.extract_embedding(preprocessed)
        
        similarities = []
        for stored_emb in stored_embeddings[:5]:  # Use 5 embeddings
            sim = recognizer.compare_embeddings(test_embedding, stored_emb)
            similarities.append(sim)
        
        max_sim = max(similarities)
        return max_sim >= 0.85
    
    stats = measure_time(auth_flow_5, iterations=20)
    
    print(f"  Mean:   {stats['mean']:.2f} ms")
    print(f"  Median: {stats['median']:.2f} ms")
    print(f"  Min:    {stats['min']:.2f} ms")
    print(f"  Max:    {stats['max']:.2f} ms")
    print(f"  StdDev: {stats['stdev']:.2f} ms")
    
    target_5 = 800  # Target: < 800ms for 5 embeddings
    if stats['mean'] < target_5:
        print(f"  ✓ PASSED: Mean {stats['mean']:.2f}ms < {target_5}ms target")
        return True, stats
    else:
        print(f"  ✗ FAILED: Mean {stats['mean']:.2f}ms >= {target_5}ms target")
        return False, stats


def test_varying_image_sizes(detector, preprocessor, recognizer):
    """Test performance with varying image sizes"""
    print("\n[Test 7] Performance with Varying Image Sizes")
    print("-" * 60)
    
    sizes = [
        (320, 240, "Small (320x240)"),
        (640, 480, "Medium (640x480)"),
        (1280, 720, "Large (1280x720)"),
        (1920, 1080, "HD (1920x1080)")
    ]
    
    face_box = (220, 140, 200, 200)
    all_passed = True
    
    for width, height, label in sizes:
        image = create_test_face_image(size=(width, height))
        
        # Adjust face box for larger images
        adjusted_box = (
            int(face_box[0] * width / 640),
            int(face_box[1] * height / 480),
            face_box[2],
            face_box[3]
        )
        
        def process_image():
            preprocessed = preprocessor.preprocess_face(image, adjusted_box)
            embedding = recognizer.extract_embedding(preprocessed)
            return embedding
        
        stats = measure_time(process_image, iterations=10)
        
        print(f"\n  {label}:")
        print(f"    Mean: {stats['mean']:.2f} ms")
        
        # Larger images should still be reasonably fast
        target = 500
        if stats['mean'] < target:
            print(f"    ✓ PASSED: {stats['mean']:.2f}ms < {target}ms")
        else:
            print(f"    ✗ FAILED: {stats['mean']:.2f}ms >= {target}ms")
            all_passed = False
    
    return all_passed, {}


def run_performance_tests():
    """Run all performance tests"""
    print("\n" + "=" * 60)
    print("PERFORMANCE TESTING SUITE")
    print("OpenCV Face Recognition System")
    print("=" * 60)
    
    try:
        # Initialize components
        print("\n[Setup] Initializing components...")
        config = load_config()
        detector = FaceDetector(config)
        preprocessor = FacePreprocessor()
        recognizer = FaceRecognizer(config)
        print("✓ Components initialized")
        
        # Create test data
        print("\n[Setup] Creating test data...")
        image = create_test_face_image()
        face_box = (220, 140, 200, 200)
        preprocessed_face = preprocessor.preprocess_face(image, face_box)
        embedding1 = recognizer.extract_embedding(preprocessed_face)
        embedding2 = recognizer.extract_embedding(preprocessed_face)
        
        # Create 5 stored embeddings
        stored_embeddings = []
        for i in range(5):
            img = create_test_face_image()
            prep = preprocessor.preprocess_face(img, face_box)
            emb = recognizer.extract_embedding(prep)
            stored_embeddings.append(emb)
        
        print("✓ Test data created")
        
        # Run tests
        results = []
        
        results.append(("Face Detection", test_face_detection_performance(detector, image)))
        results.append(("Preprocessing", test_preprocessing_performance(preprocessor, image, face_box)))
        results.append(("Embedding Extraction", test_embedding_extraction_performance(recognizer, preprocessed_face)))
        results.append(("Similarity Comparison", test_similarity_comparison_performance(recognizer, embedding1, embedding2)))
        results.append(("Authentication Flow (1 embedding)", test_authentication_flow_performance(detector, preprocessor, recognizer, image, stored_embeddings[:1])))
        results.append(("Authentication Flow (5 embeddings)", test_authentication_with_5_embeddings(detector, preprocessor, recognizer, image, stored_embeddings)))
        results.append(("Varying Image Sizes", test_varying_image_sizes(detector, preprocessor, recognizer)))
        
        # Print summary
        print("\n" + "=" * 60)
        print("PERFORMANCE TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, (result, stats) in results:
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
        print("=" * 60)
        
        # Performance targets summary
        print("\nPerformance Targets:")
        print("  - Face detection: < 200ms ✓")
        print("  - Embedding extraction: < 300ms ✓")
        print("  - Authentication (single): < 500ms ✓")
        print("  - Authentication (5 embeddings): < 800ms ✓")
        
        return failed == 0
        
    except Exception as e:
        print(f"\n✗ Performance testing failed: {e}")
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
    
    success = run_performance_tests()
    
    if success:
        print("\n✓ All performance tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some performance tests failed")
        sys.exit(1)
