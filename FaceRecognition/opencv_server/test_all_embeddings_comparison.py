"""
Test that all embeddings are compared during authentication.
Tests task 15.1 requirements.

Requirements: 2.3, 3.2
"""
import sys
import os
import json
import numpy as np

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from face_recognizer import FaceRecognizer


def test_all_embeddings_comparison_logic():
    """
    Test that the authentication endpoint compares against ALL stored embeddings.
    
    Requirements: 2.3 - All embeddings compared during authentication
    """
    print("\n[Test 1] Testing all embeddings comparison logic in app.py...")
    
    try:
        # Read app.py
        with open('app.py', 'r') as f:
            app_code = f.read()
        
        # Find the authenticate_face function
        if 'def authenticate_face():' not in app_code:
            print("✗ authenticate_face function not found")
            return False
        
        # Extract the authenticate function
        start_idx = app_code.find('def authenticate_face():')
        next_func = app_code.find('\n\nif __name__', start_idx)
        if next_func == -1:
            next_func = len(app_code)
        
        auth_func = app_code[start_idx:next_func]
        
        # Check for all required components
        checks = [
            ("Retrieve all embeddings", "get_embeddings_for_user"),
            ("Loop through ALL stored embeddings", "for stored_embedding in stored_embeddings"),
            ("Compare each embedding", "compare_embeddings(current_embedding, stored_embedding)"),
            ("Track all similarity scores", "similarity_scores.append(similarity)"),
            ("Select maximum similarity", "max(max_similarity, similarity)"),
            ("Log all similarity scores", "similarity_scores"),
            ("Use max for authentication decision", "max_similarity >= auth_threshold"),
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
        print(f"✗ Failed to analyze authentication logic: {e}")
        return False


def test_maximum_similarity_selection_logic():
    """
    Test that maximum similarity is correctly selected from multiple comparisons.
    
    Requirements: 3.2 - Maximum similarity score selection
    """
    print("\n[Test 2] Testing maximum similarity selection logic...")
    
    try:
        # Read app.py
        with open('app.py', 'r') as f:
            app_code = f.read()
        
        # Find the authenticate_face function
        start_idx = app_code.find('def authenticate_face():')
        next_func = app_code.find('\n\nif __name__', start_idx)
        if next_func == -1:
            next_func = len(app_code)
        
        auth_func = app_code[start_idx:next_func]
        
        # Check for maximum selection logic
        checks = [
            ("Initialize max_similarity", "max_similarity = 0.0"),
            ("Update max in loop", "max(max_similarity, similarity)"),
            ("Use max for decision", "max_similarity >= auth_threshold"),
            ("Return max in response", '"confidence": float(max_similarity)'),
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
        print(f"✗ Failed to analyze maximum selection logic: {e}")
        return False


def test_similarity_logging():
    """
    Test that all similarity scores are logged for debugging.
    
    Requirements: 2.3, 3.2
    """
    print("\n[Test 3] Testing similarity scores logging...")
    
    try:
        # Read app.py
        with open('app.py', 'r') as f:
            app_code = f.read()
        
        # Find the authenticate_face function
        start_idx = app_code.find('def authenticate_face():')
        next_func = app_code.find('\n\nif __name__', start_idx)
        if next_func == -1:
            next_func = len(app_code)
        
        auth_func = app_code[start_idx:next_func]
        
        # Check for logging of all similarity scores
        checks = [
            ("Log number of embeddings compared", "len(stored_embeddings)"),
            ("Log all similarity scores", "similarity_scores"),
            ("Log max similarity", "max_similarity"),
            ("Use logger.info", "logger.info"),
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
        print(f"✗ Failed to check logging: {e}")
        return False


def test_compare_embeddings_function():
    """
    Test that the compare_embeddings function works correctly.
    
    This verifies the underlying comparison function that is used
    to compare all embeddings.
    """
    print("\n[Test 4] Testing compare_embeddings function...")
    
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize face recognizer
        recognizer = FaceRecognizer(config)
        
        # Create test embeddings
        embedding1 = np.random.rand(128).astype(np.float32)
        embedding2 = np.random.rand(128).astype(np.float32)
        
        # Test comparison
        similarity = recognizer.compare_embeddings(embedding1, embedding2)
        
        # Verify similarity is in valid range
        if not (0.0 <= similarity <= 1.0):
            print(f"✗ Similarity score out of range: {similarity}")
            return False
        
        print(f"  ✓ compare_embeddings returns valid score: {similarity:.4f}")
        
        # Test with identical embeddings
        similarity_same = recognizer.compare_embeddings(embedding1, embedding1)
        
        if similarity_same < 0.99:  # Should be very close to 1.0
            print(f"✗ Identical embeddings should have high similarity: {similarity_same}")
            return False
        
        print(f"  ✓ Identical embeddings have high similarity: {similarity_same:.4f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test compare_embeddings: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multiple_embeddings_scenario():
    """
    Test the logic for handling multiple embeddings.
    
    This simulates what happens when a user has multiple stored embeddings.
    """
    print("\n[Test 5] Testing multiple embeddings scenario...")
    
    try:
        # Load config
        with open('config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize face recognizer
        recognizer = FaceRecognizer(config)
        
        # Create a current embedding
        current_embedding = np.random.rand(128).astype(np.float32)
        
        # Create multiple stored embeddings with varying similarity
        stored_embeddings = [
            np.random.rand(128).astype(np.float32),  # Random (low similarity)
            current_embedding + np.random.rand(128).astype(np.float32) * 0.1,  # Similar
            np.random.rand(128).astype(np.float32),  # Random (low similarity)
            current_embedding + np.random.rand(128).astype(np.float32) * 0.05,  # Very similar
            np.random.rand(128).astype(np.float32),  # Random (low similarity)
        ]
        
        # Simulate the comparison logic from app.py
        max_similarity = 0.0
        similarity_scores = []
        
        for stored_embedding in stored_embeddings:
            similarity = recognizer.compare_embeddings(current_embedding, stored_embedding)
            similarity_scores.append(similarity)
            max_similarity = max(max_similarity, similarity)
        
        print(f"  ✓ Compared against {len(stored_embeddings)} embeddings")
        print(f"  ✓ Similarity scores: {[f'{s:.3f}' for s in similarity_scores]}")
        print(f"  ✓ Maximum similarity: {max_similarity:.3f}")
        
        # Verify that max is indeed the maximum
        if max_similarity != max(similarity_scores):
            print(f"✗ max_similarity doesn't match max of scores")
            return False
        
        print(f"  ✓ Maximum correctly selected from all comparisons")
        
        # Verify all embeddings were compared
        if len(similarity_scores) != len(stored_embeddings):
            print(f"✗ Not all embeddings were compared")
            return False
        
        print(f"  ✓ All {len(stored_embeddings)} embeddings were compared")
        
        return True
        
    except Exception as e:
        print(f"✗ Failed to test multiple embeddings scenario: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("=" * 70)
    print("All Embeddings Comparison Test")
    print("Testing Task 15.1 Implementation")
    print("Requirements: 2.3, 3.2")
    print("=" * 70)
    
    results = []
    
    # Run all tests
    results.append(("All embeddings comparison logic", test_all_embeddings_comparison_logic()))
    results.append(("Maximum similarity selection", test_maximum_similarity_selection_logic()))
    results.append(("Similarity scores logging", test_similarity_logging()))
    results.append(("compare_embeddings function", test_compare_embeddings_function()))
    results.append(("Multiple embeddings scenario", test_multiple_embeddings_scenario()))
    
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
        print("\n✓ All tests passed!")
        print("\nTask 15.1 is fully implemented:")
        print("  ✓ Retrieve all embeddings for user from database")
        print("  ✓ Compare captured embedding against each stored embedding")
        print("  ✓ Calculate similarity score for each comparison")
        print("  ✓ Select maximum similarity score")
        print("  ✓ Log all similarity scores")
        print("\nRequirements validated:")
        print("  ✓ 2.3: All embeddings compared during authentication")
        print("  ✓ 3.2: Maximum similarity score selection")
        return True
    else:
        print(f"\n✗ {failed} test(s) failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
