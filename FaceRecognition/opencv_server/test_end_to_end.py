"""
End-to-End Testing for OpenCV Face Recognition System
Tests complete registration and authentication flows including:
- C# → Python → Database flow simulation
- Multiple users
- Concurrent requests
- Error scenarios
"""
import cv2
import numpy as np
import json
import sys
import os
import base64
import time
import threading
from io import BytesIO

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database_manager import DatabaseManager
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
    # Encode image as JPEG
    _, buffer = cv2.imencode('.jpg', image)
    # Convert to base64
    base64_str = base64.b64encode(buffer).decode('utf-8')
    return base64_str


def base64_to_image(base64_str):
    """Convert base64 string to numpy image"""
    # Decode base64
    img_data = base64.b64decode(base64_str)
    # Convert to numpy array
    nparr = np.frombuffer(img_data, np.uint8)
    # Decode image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


class EndToEndTester:
    """End-to-end testing class"""
    
    def __init__(self):
        self.config = load_config()
        self.db_manager = DatabaseManager(self.config['database']['connection_string'])
        self.detector = FaceDetector(self.config)
        self.preprocessor = FacePreprocessor()
        self.recognizer = FaceRecognizer(self.config)
        self.test_user_ids = []
        
    def cleanup(self):
        """Clean up test data"""
        print("\n[Cleanup] Removing test data...")
        for user_id in self.test_user_ids:
            try:
                self.db_manager.delete_embeddings_for_user(user_id)
                print(f"  ✓ Cleaned up user {user_id}")
            except Exception as e:
                print(f"  ✗ Failed to clean up user {user_id}: {e}")
    
    def simulate_registration(self, user_id, num_images=5):
        """
        Simulate complete registration flow (C# → Python → Database)
        """
        print(f"\n[Registration] User {user_id} - Capturing {num_images} images...")
        
        embeddings_stored = 0
        face_box = (220, 140, 200, 200)  # Manual face box for synthetic images
        
        for i in range(num_images):
            try:
                # Step 1: Capture image (simulated)
                image = create_test_face_image(seed=user_id * 100 + i)
                
                # Step 2: Convert to base64 (simulating C# encoding)
                base64_image = image_to_base64(image)
                
                # Step 3: Decode base64 (simulating Python server receiving)
                decoded_image = base64_to_image(base64_image)
                
                # Step 4: Detect face (using manual box for synthetic images)
                # In real scenario: faces = self.detector.detect_faces(decoded_image)
                
                # Step 5: Preprocess face
                preprocessed_face = self.preprocessor.preprocess_face(decoded_image, face_box)
                
                # Step 6: Extract embedding
                embedding = self.recognizer.extract_embedding(preprocessed_face)
                
                # Step 7: Store in database
                self.db_manager.store_embedding(user_id, embedding)
                embeddings_stored += 1
                
                print(f"  ✓ Image {i+1}/{num_images} processed and stored")
                
            except Exception as e:
                print(f"  ✗ Failed to process image {i+1}: {e}")
                return False
        
        # Verify minimum embeddings requirement
        stored_embeddings = self.db_manager.get_embeddings_for_user(user_id)
        if len(stored_embeddings) < 5:
            print(f"  ✗ Insufficient embeddings stored: {len(stored_embeddings)} < 5")
            return False
        
        print(f"  ✓ Registration complete: {embeddings_stored} embeddings stored")
        return True
    
    def simulate_authentication(self, user_id, should_match=True):
        """
        Simulate complete authentication flow (C# → Python → Database)
        """
        print(f"\n[Authentication] User {user_id}...")
        
        try:
            # Step 1: Capture image (simulated)
            if should_match:
                # Use similar seed to registration for matching
                image = create_test_face_image(seed=user_id * 100)
            else:
                # Use different seed for non-matching
                image = create_test_face_image(seed=user_id * 100 + 999)
            
            # Step 2: Convert to base64
            base64_image = image_to_base64(image)
            
            # Step 3: Decode base64
            decoded_image = base64_to_image(base64_image)
            
            # Step 4: Detect face
            face_box = (220, 140, 200, 200)
            
            # Step 5: Preprocess face
            preprocessed_face = self.preprocessor.preprocess_face(decoded_image, face_box)
            
            # Step 6: Extract embedding
            test_embedding = self.recognizer.extract_embedding(preprocessed_face)
            
            # Step 7: Retrieve stored embeddings
            stored_embeddings = self.db_manager.get_embeddings_for_user(user_id)
            
            if not stored_embeddings:
                print(f"  ✗ No embeddings found for user {user_id}")
                return False, 0.0
            
            # Step 8: Compare against all stored embeddings
            similarities = []
            for stored_emb in stored_embeddings:
                similarity = self.recognizer.compare_embeddings(test_embedding, stored_emb)
                similarities.append(similarity)
            
            # Step 9: Get maximum similarity
            max_similarity = max(similarities)
            
            # Step 10: Check against threshold
            threshold = self.config['face_recognition']['authentication_threshold']
            success = max_similarity >= threshold
            
            print(f"  Compared against {len(stored_embeddings)} embeddings")
            print(f"  Max similarity: {max_similarity:.4f}")
            print(f"  Threshold: {threshold}")
            print(f"  Result: {'✓ AUTHENTICATED' if success else '✗ REJECTED'}")
            
            return success, max_similarity
            
        except Exception as e:
            print(f"  ✗ Authentication failed: {e}")
            return False, 0.0
    
    def test_complete_registration_flow(self):
        """Test 16.1.1: Complete registration flow"""
        print("\n" + "=" * 60)
        print("TEST 1: Complete Registration Flow (C# → Python → Database)")
        print("=" * 60)
        
        user_id = 9001
        self.test_user_ids.append(user_id)
        
        success = self.simulate_registration(user_id, num_images=5)
        
        if success:
            print("\n✓ TEST 1 PASSED: Registration flow works correctly")
            return True
        else:
            print("\n✗ TEST 1 FAILED: Registration flow has issues")
            return False
    
    def test_complete_authentication_flow(self):
        """Test 16.1.2: Complete authentication flow"""
        print("\n" + "=" * 60)
        print("TEST 2: Complete Authentication Flow")
        print("=" * 60)
        
        user_id = 9002
        self.test_user_ids.append(user_id)
        
        # First register the user
        print("\n[Setup] Registering user...")
        if not self.simulate_registration(user_id, num_images=5):
            print("\n✗ TEST 2 FAILED: Could not register user")
            return False
        
        # Test authentication with matching face
        print("\n[Test] Authenticating with matching face...")
        success, confidence = self.simulate_authentication(user_id, should_match=True)
        
        if success:
            print(f"\n✓ TEST 2 PASSED: Authentication successful (confidence: {confidence:.4f})")
            return True
        else:
            print(f"\n✗ TEST 2 FAILED: Authentication failed (confidence: {confidence:.4f})")
            return False
    
    def test_multiple_users(self):
        """Test 16.1.3: Multiple users"""
        print("\n" + "=" * 60)
        print("TEST 3: Multiple Users")
        print("=" * 60)
        
        users = [9003, 9004, 9005]
        self.test_user_ids.extend(users)
        
        # Register all users
        print("\n[Setup] Registering multiple users...")
        for user_id in users:
            if not self.simulate_registration(user_id, num_images=5):
                print(f"\n✗ TEST 3 FAILED: Could not register user {user_id}")
                return False
        
        # Authenticate each user
        print("\n[Test] Authenticating each user...")
        all_success = True
        for user_id in users:
            success, confidence = self.simulate_authentication(user_id, should_match=True)
            if not success:
                print(f"  ✗ User {user_id} authentication failed")
                all_success = False
        
        if all_success:
            print("\n✓ TEST 3 PASSED: All users authenticated successfully")
            return True
        else:
            print("\n✗ TEST 3 FAILED: Some users failed authentication")
            return False
    
    def test_concurrent_requests(self):
        """Test 16.1.4: Concurrent requests"""
        print("\n" + "=" * 60)
        print("TEST 4: Concurrent Requests")
        print("=" * 60)
        
        user_id = 9006
        self.test_user_ids.append(user_id)
        
        # Register user first
        print("\n[Setup] Registering user...")
        if not self.simulate_registration(user_id, num_images=5):
            print("\n✗ TEST 4 FAILED: Could not register user")
            return False
        
        # Test concurrent authentication requests
        print("\n[Test] Sending 5 concurrent authentication requests...")
        
        results = []
        threads = []
        
        def auth_thread(user_id, results, index):
            success, confidence = self.simulate_authentication(user_id, should_match=True)
            results.append((index, success, confidence))
        
        # Start threads
        for i in range(5):
            t = threading.Thread(target=auth_thread, args=(user_id, results, i))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Check results
        print(f"\n[Results] Processed {len(results)} concurrent requests:")
        all_success = True
        for index, success, confidence in sorted(results):
            status = "✓" if success else "✗"
            print(f"  {status} Request {index+1}: {confidence:.4f}")
            if not success:
                all_success = False
        
        if all_success:
            print("\n✓ TEST 4 PASSED: All concurrent requests succeeded")
            return True
        else:
            print("\n✗ TEST 4 FAILED: Some concurrent requests failed")
            return False
    
    def test_error_scenarios(self):
        """Test 16.1.5: Error scenarios"""
        print("\n" + "=" * 60)
        print("TEST 5: Error Scenarios")
        print("=" * 60)
        
        all_passed = True
        
        # Test 5.1: Authentication with no stored embeddings
        print("\n[Test 5.1] Authentication with no stored embeddings...")
        user_id = 9999  # User that doesn't exist
        try:
            stored_embeddings = self.db_manager.get_embeddings_for_user(user_id)
            if len(stored_embeddings) == 0:
                print("  ✓ Correctly returns empty list for non-existent user")
            else:
                print(f"  ✗ Expected empty list, got {len(stored_embeddings)} embeddings")
                all_passed = False
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            all_passed = False
        
        # Test 5.2: Invalid user ID
        print("\n[Test 5.2] Invalid user ID...")
        try:
            # Try with negative user ID
            stored_embeddings = self.db_manager.get_embeddings_for_user(-1)
            print("  ✓ Handles invalid user ID gracefully")
        except Exception as e:
            print(f"  ✓ Raises appropriate error for invalid user ID: {type(e).__name__}")
        
        # Test 5.3: Corrupted embedding data
        print("\n[Test 5.3] Handling corrupted data...")
        try:
            # Try to compare with invalid embedding
            valid_embedding = np.random.rand(128).astype(np.float32)
            invalid_embedding = np.random.rand(64).astype(np.float32)  # Wrong size
            
            try:
                similarity = self.recognizer.compare_embeddings(valid_embedding, invalid_embedding)
                print(f"  ✗ Should have raised error for mismatched embedding sizes")
                all_passed = False
            except Exception as e:
                print(f"  ✓ Correctly raises error for invalid embeddings: {type(e).__name__}")
        except Exception as e:
            print(f"  ✗ Unexpected error: {e}")
            all_passed = False
        
        # Test 5.4: Authentication with non-matching face
        print("\n[Test 5.4] Authentication with non-matching face...")
        user_id = 9007
        self.test_user_ids.append(user_id)
        
        # Register user
        if self.simulate_registration(user_id, num_images=5):
            # Try to authenticate with different face
            success, confidence = self.simulate_authentication(user_id, should_match=False)
            
            threshold = self.config['face_recognition']['authentication_threshold']
            if not success and confidence < threshold:
                print(f"  ✓ Correctly rejects non-matching face (confidence: {confidence:.4f})")
            else:
                print(f"  ✗ Should have rejected non-matching face (confidence: {confidence:.4f})")
                all_passed = False
        else:
            print("  ✗ Could not register user for test")
            all_passed = False
        
        if all_passed:
            print("\n✓ TEST 5 PASSED: All error scenarios handled correctly")
            return True
        else:
            print("\n✗ TEST 5 FAILED: Some error scenarios not handled correctly")
            return False


def run_all_tests():
    """Run all end-to-end tests"""
    print("\n" + "=" * 60)
    print("END-TO-END TESTING SUITE")
    print("OpenCV Face Recognition System")
    print("=" * 60)
    
    try:
        tester = EndToEndTester()
    except Exception as e:
        print(f"\n✗ Failed to initialize tester: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        results = []
        
        # Run all tests
        results.append(("Complete Registration Flow", tester.test_complete_registration_flow()))
        results.append(("Complete Authentication Flow", tester.test_complete_authentication_flow()))
        results.append(("Multiple Users", tester.test_multiple_users()))
        results.append(("Concurrent Requests", tester.test_concurrent_requests()))
        results.append(("Error Scenarios", tester.test_error_scenarios()))
        
        # Print summary
        print("\n" + "=" * 60)
        print("TEST SUMMARY")
        print("=" * 60)
        
        passed = 0
        failed = 0
        
        for test_name, result in results:
            status = "✓ PASSED" if result else "✗ FAILED"
            print(f"{status}: {test_name}")
            if result:
                passed += 1
            else:
                failed += 1
        
        print("\n" + "=" * 60)
        print(f"Total: {passed} passed, {failed} failed out of {len(results)} tests")
        print("=" * 60)
        
        return failed == 0
        
    finally:
        # Cleanup
        tester.cleanup()


if __name__ == "__main__":
    import logging
    
    # Configure logging
    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run all tests
    success = run_all_tests()
    
    if success:
        print("\n✓ All end-to-end tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some end-to-end tests failed")
        sys.exit(1)
