"""
Test script for minimum embeddings requirement enforcement.
Tests that registration requires exactly 5 embeddings.

Requirements: 1.4 - Minimum embeddings per user
"""
import sys
import os
import json
import base64
import cv2
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_test_face_image():
    """Create a test image with a face-like region"""
    # Create a 640x480 BGR image
    image = np.random.randint(100, 150, (480, 640, 3), dtype=np.uint8)
    
    # Add a brighter region to simulate a face
    face_region = np.random.randint(150, 200, (200, 200, 3), dtype=np.uint8)
    image[140:340, 220:420] = face_region
    
    return image


def image_to_base64(image):
    """Convert OpenCV image to base64 string"""
    _, buffer = cv2.imencode('.jpg', image)
    base64_string = base64.b64encode(buffer).decode('utf-8')
    return base64_string


def test_minimum_embeddings_requirement():
    """
    Test that the system enforces minimum embeddings requirement.
    
    Requirements: 1.4 - Store at least 5 face embeddings per user
    """
    print("=" * 80)
    print("MINIMUM EMBEDDINGS REQUIREMENT TEST")
    print("=" * 80)
    print("\nRequirement 1.4: Store at least 5 face embeddings per user")
    print("This test verifies that:")
    print("  1. Registration tracks progress toward 5 embeddings")
    print("  2. Registration is only complete with 5 embeddings")
    print("  3. Authentication requires 5 embeddings")
    print("  4. Validation endpoint correctly checks minimum requirement")
    print("=" * 80)
    
    # Import Flask app
    try:
        from app import app, initialize_components
        print("\n[Setup] Imported Flask app successfully")
    except Exception as e:
        print(f"\n✗ Failed to import Flask app: {e}")
        return False
    
    # Initialize components
    print("[Setup] Initializing components...")
    try:
        if not initialize_components():
            print("✗ Failed to initialize components")
            return False
        print("✓ Components initialized successfully")
    except Exception as e:
        print(f"✗ Failed to initialize components: {e}")
        return False
    
    # Create test client
    app.config['TESTING'] = True
    client = app.test_client()
    
    # Use a test user ID
    test_user_id = 99999
    
    # Clean up any existing embeddings for test user
    print(f"\n[Setup] Cleaning up test user {test_user_id}...")
    try:
        from database_manager import DatabaseManager
        from app import config
        
        db_config = config.get('database', {})
        connection_string = db_config.get('connection_string')
        db_manager = DatabaseManager(connection_string)
        
        db_manager.delete_embeddings_for_user(test_user_id)
        initial_count = db_manager.get_embedding_count_for_user(test_user_id)
        print(f"✓ Test user cleaned up. Initial embeddings: {initial_count}")
        
        if initial_count != 0:
            print(f"✗ Failed to clean up test user. Count should be 0, got {initial_count}")
            return False
            
    except Exception as e:
        print(f"✗ Failed to clean up test user: {e}")
        return False
    
    # Test 1: Register embeddings one by one and track progress
    print("\n" + "=" * 80)
    print("TEST 1: Register embeddings and track progress")
    print("=" * 80)
    
    for i in range(1, 6):  # Register 5 embeddings
        print(f"\n[Test 1.{i}] Registering embedding {i}/5...")
        
        try:
            # Create test image
            test_image = create_test_face_image()
            base64_image = image_to_base64(test_image)
            
            # Send registration request
            response = client.post('/register',
                                  data=json.dumps({
                                      'user_id': test_user_id,
                                      'image': base64_image
                                  }),
                                  content_type='application/json')
            
            data = json.loads(response.data)
            
            print(f"  Status code: {response.status_code}")
            print(f"  Response: {json.dumps(data, indent=2)}")
            
            # Verify response structure
            if response.status_code != 200:
                print(f"✗ Registration failed with status {response.status_code}")
                return False
            
            if not data.get('success'):
                print(f"✗ Registration not successful: {data.get('message')}")
                return False
            
            # Check progress tracking
            embeddings_count = data.get('embeddings_count', 0)
            minimum_required = data.get('minimum_required', 5)
            registration_complete = data.get('registration_complete', False)
            
            print(f"  Progress: {embeddings_count}/{minimum_required}")
            print(f"  Registration complete: {registration_complete}")
            
            # Verify count matches iteration
            if embeddings_count != i:
                print(f"✗ Expected {i} embeddings, got {embeddings_count}")
                return False
            
            # Verify completion status
            expected_complete = (i >= 5)
            if registration_complete != expected_complete:
                print(f"✗ Expected registration_complete={expected_complete}, got {registration_complete}")
                return False
            
            print(f"✓ Embedding {i}/5 registered successfully")
            
        except Exception as e:
            print(f"✗ Registration {i} failed: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    print("\n✓ TEST 1 PASSED: All 5 embeddings registered with correct progress tracking")
    
    # Test 2: Validate registration endpoint
    print("\n" + "=" * 80)
    print("TEST 2: Validate registration endpoint")
    print("=" * 80)
    
    print("\n[Test 2.1] Validating registration for user with 5 embeddings...")
    try:
        response = client.post('/validate_registration',
                              data=json.dumps({
                                  'user_id': test_user_id
                              }),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        print(f"  Status code: {response.status_code}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        if response.status_code != 200:
            print(f"✗ Validation failed with status {response.status_code}")
            return False
        
        if not data.get('valid'):
            print(f"✗ Validation should be true for user with 5 embeddings")
            return False
        
        if data.get('embeddings_count') != 5:
            print(f"✗ Expected 5 embeddings, got {data.get('embeddings_count')}")
            return False
        
        print("✓ Validation passed for user with 5 embeddings")
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 3: Test authentication with sufficient embeddings
    print("\n" + "=" * 80)
    print("TEST 3: Authentication with sufficient embeddings")
    print("=" * 80)
    
    print("\n[Test 3.1] Attempting authentication with 5 embeddings...")
    try:
        test_image = create_test_face_image()
        base64_image = image_to_base64(test_image)
        
        response = client.post('/authenticate',
                              data=json.dumps({
                                  'user_id': test_user_id,
                                  'image': base64_image
                              }),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        print(f"  Status code: {response.status_code}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        # Authentication may succeed or fail based on similarity, but should not
        # return INSUFFICIENT_EMBEDDINGS error
        error_code = data.get('error_code', '')
        if error_code == 'INSUFFICIENT_EMBEDDINGS':
            print(f"✗ Should not get INSUFFICIENT_EMBEDDINGS error with 5 embeddings")
            return False
        
        print("✓ Authentication attempted (no insufficient embeddings error)")
        
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test with insufficient embeddings
    print("\n" + "=" * 80)
    print("TEST 4: Validation and authentication with insufficient embeddings")
    print("=" * 80)
    
    # Create a new test user with only 3 embeddings
    test_user_id_2 = 99998
    
    print(f"\n[Test 4.1] Setting up user {test_user_id_2} with only 3 embeddings...")
    try:
        # Clean up
        db_manager.delete_embeddings_for_user(test_user_id_2)
        
        # Register only 3 embeddings
        for i in range(1, 4):
            test_image = create_test_face_image()
            base64_image = image_to_base64(test_image)
            
            response = client.post('/register',
                                  data=json.dumps({
                                      'user_id': test_user_id_2,
                                      'image': base64_image
                                  }),
                                  content_type='application/json')
            
            if response.status_code != 200:
                print(f"✗ Failed to register embedding {i}")
                return False
        
        count = db_manager.get_embedding_count_for_user(test_user_id_2)
        print(f"✓ User {test_user_id_2} set up with {count} embeddings")
        
        if count != 3:
            print(f"✗ Expected 3 embeddings, got {count}")
            return False
            
    except Exception as e:
        print(f"✗ Setup failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n[Test 4.2] Validating user with only 3 embeddings...")
    try:
        response = client.post('/validate_registration',
                              data=json.dumps({
                                  'user_id': test_user_id_2
                              }),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        print(f"  Status code: {response.status_code}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        if data.get('valid'):
            print(f"✗ Validation should be false for user with only 3 embeddings")
            return False
        
        if data.get('embeddings_count') != 3:
            print(f"✗ Expected 3 embeddings, got {data.get('embeddings_count')}")
            return False
        
        print("✓ Validation correctly failed for user with insufficient embeddings")
        
    except Exception as e:
        print(f"✗ Validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print(f"\n[Test 4.3] Attempting authentication with only 3 embeddings...")
    try:
        test_image = create_test_face_image()
        base64_image = image_to_base64(test_image)
        
        response = client.post('/authenticate',
                              data=json.dumps({
                                  'user_id': test_user_id_2,
                                  'image': base64_image
                              }),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        print(f"  Status code: {response.status_code}")
        print(f"  Response: {json.dumps(data, indent=2)}")
        
        # Should get INSUFFICIENT_EMBEDDINGS error
        error_code = data.get('error_code', '')
        if error_code != 'INSUFFICIENT_EMBEDDINGS':
            print(f"✗ Expected INSUFFICIENT_EMBEDDINGS error, got {error_code}")
            return False
        
        if response.status_code != 400:
            print(f"✗ Expected status 400, got {response.status_code}")
            return False
        
        print("✓ Authentication correctly rejected for insufficient embeddings")
        
    except Exception as e:
        print(f"✗ Authentication test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Clean up test users
    print("\n[Cleanup] Removing test users...")
    try:
        db_manager.delete_embeddings_for_user(test_user_id)
        db_manager.delete_embeddings_for_user(test_user_id_2)
        print("✓ Test users cleaned up")
    except Exception as e:
        print(f"⚠ Warning: Failed to clean up test users: {e}")
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS PASSED")
    print("=" * 80)
    print("\nSummary:")
    print("  ✓ Registration tracks progress toward 5 embeddings")
    print("  ✓ Registration completion status is correct")
    print("  ✓ Validation endpoint correctly checks minimum requirement")
    print("  ✓ Authentication allows users with 5+ embeddings")
    print("  ✓ Authentication rejects users with < 5 embeddings")
    print("\nRequirement 1.4 is fully implemented and tested.")
    print("=" * 80)
    
    return True


if __name__ == '__main__':
    try:
        success = test_minimum_embeddings_requirement()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test suite failed with exception: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
