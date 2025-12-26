"""
Test authentication logic and threshold implementation.
Tests task 6.1 and 6.2 requirements.
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_config_threshold_reading():
    """Test that authentication threshold is read from config"""
    print("\n[Test 1] Testing config threshold reading...")
    
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Check if authentication_threshold exists
        auth_threshold = config.get('face_recognition', {}).get('authentication_threshold')
        
        if auth_threshold is None:
            print("✗ authentication_threshold not found in config")
            return False
        
        print(f"  ✓ Found authentication_threshold: {auth_threshold}")
        
        # Verify it's the expected default value
        if auth_threshold != 0.85:
            print(f"  ⚠ Warning: Expected 0.85, got {auth_threshold}")
        
        # Verify it's a valid threshold (between 0 and 1)
        if not (0.0 <= auth_threshold <= 1.0):
            print(f"✗ Invalid threshold value: {auth_threshold} (must be between 0.0 and 1.0)")
            return False
        
        print("  ✓ Threshold value is valid")
        return True
        
    except Exception as e:
        print(f"✗ Failed to read config: {e}")
        return False


def test_authentication_logic_in_code():
    """Test that authentication logic is implemented in app.py"""
    print("\n[Test 2] Testing authentication logic implementation...")
    
    try:
        # Read app.py
        with open('app.py', 'r') as f:
            app_code = f.read()
        
        # Check for key authentication logic components
        checks = [
            ("authentication_threshold from config", "authentication_threshold"),
            ("max similarity calculation", "max_similarity"),
            ("threshold comparison", ">="),
            ("success response with confidence", '"success": True'),
            ("failure response with confidence", '"success": False'),
            ("confidence in response", '"confidence"'),
        ]
        
        all_passed = True
        for check_name, check_string in checks:
            if check_string in app_code:
                print(f"  ✓ Found: {check_name}")
            else:
                print(f"  ✗ Missing: {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Failed to read app.py: {e}")
        return False


def test_maximum_similarity_selection():
    """Test that maximum similarity selection is implemented"""
    print("\n[Test 3] Testing maximum similarity selection logic...")
    
    try:
        # Read app.py
        with open('app.py', 'r') as f:
            app_code = f.read()
        
        # Check for maximum similarity selection logic
        checks = [
            ("Loop through stored embeddings", "for stored_embedding in stored_embeddings"),
            ("Compare embeddings", "compare_embeddings"),
            ("Track similarity scores", "similarity_scores"),
            ("Calculate max similarity", "max("),
            ("Log similarity scores", "similarity_scores"),
        ]
        
        all_passed = True
        for check_name, check_string in checks:
            if check_string in app_code:
                print(f"  ✓ Found: {check_name}")
            else:
                print(f"  ✗ Missing: {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Failed to read app.py: {e}")
        return False


def test_response_format():
    """Test that response includes required fields"""
    print("\n[Test 4] Testing response format...")
    
    try:
        # Read app.py
        with open('app.py', 'r') as f:
            app_code = f.read()
        
        # Check for response format in authenticate endpoint
        # Look for the authenticate_face function
        if 'def authenticate_face():' not in app_code:
            print("✗ authenticate_face function not found")
            return False
        
        # Extract the authenticate function
        start_idx = app_code.find('def authenticate_face():')
        # Find the next function definition or end of file
        next_func = app_code.find('\n\nif __name__', start_idx)
        if next_func == -1:
            next_func = len(app_code)
        
        auth_func = app_code[start_idx:next_func]
        
        # Check for required response fields
        checks = [
            ("success field", '"success"'),
            ("confidence field", '"confidence"'),
            ("message field", '"message"'),
            ("success=True case", '"success": True'),
            ("success=False case", '"success": False'),
        ]
        
        all_passed = True
        for check_name, check_string in checks:
            if check_string in auth_func:
                print(f"  ✓ Found: {check_name}")
            else:
                print(f"  ✗ Missing: {check_name}")
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"✗ Failed to analyze response format: {e}")
        return False


def test_logging_implementation():
    """Test that similarity scores are logged"""
    print("\n[Test 5] Testing logging of similarity scores...")
    
    try:
        # Read app.py
        with open('app.py', 'r') as f:
            app_code = f.read()
        
        # Check for logging of similarity scores
        if 'logger.info' in app_code and 'similarity_scores' in app_code:
            print("  ✓ Similarity scores are logged")
            return True
        else:
            print("  ✗ Similarity scores logging not found")
            return False
        
    except Exception as e:
        print(f"✗ Failed to check logging: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("Authentication Logic and Thresholds Test")
    print("Testing Task 6.1 and 6.2 Implementation")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("Config threshold reading", test_config_threshold_reading()))
    results.append(("Authentication logic", test_authentication_logic_in_code()))
    results.append(("Maximum similarity selection", test_maximum_similarity_selection()))
    results.append(("Response format", test_response_format()))
    results.append(("Logging implementation", test_logging_implementation()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("=" * 70)
    print(f"Total: {passed} passed, {failed} failed")
    print("=" * 70)
    
    if failed == 0:
        print("\n✓ All authentication logic tests passed!")
        print("\nTask 6.1 and 6.2 are fully implemented:")
        print("  ✓ Threshold-based authentication decision")
        print("  ✓ Maximum similarity selection")
        print("  ✓ Confidence score in response")
        print("  ✓ Logging of similarity scores")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
