"""
Test Runner for OpenCV Face Recognition System
Runs all unit tests and reports results
"""
import subprocess
import sys
import os

# List of test files to run (excluding database tests that require connection)
TEST_FILES = [
    'test_face_detection.py',
    'test_face_recognizer.py',
    'test_authentication_logic.py',
    'test_error_handling.py',
    'test_sql_injection.py',
    'test_all_embeddings_comparison.py',
    'test_minimum_embeddings_simple.py',
    'test_integration.py',
    'test_e2e_no_db.py',
]

def run_test_file(test_file):
    """Run a single test file and return success status"""
    print(f"\n{'=' * 60}")
    print(f"Running: {test_file}")
    print('=' * 60)
    
    try:
        result = subprocess.run(
            [sys.executable, test_file],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=False,
            timeout=30
        )
        
        success = result.returncode == 0
        if success:
            print(f"✓ {test_file} PASSED")
        else:
            print(f"✗ {test_file} FAILED (exit code: {result.returncode})")
        
        return success
        
    except subprocess.TimeoutExpired:
        print(f"✗ {test_file} TIMEOUT")
        return False
    except Exception as e:
        print(f"✗ {test_file} ERROR: {e}")
        return False


def main():
    """Run all tests and report summary"""
    print("\n" + "=" * 60)
    print("UNIT TEST SUITE")
    print("OpenCV Face Recognition System")
    print("=" * 60)
    
    results = {}
    
    for test_file in TEST_FILES:
        test_path = os.path.join(os.path.dirname(__file__), test_file)
        if os.path.exists(test_path):
            results[test_file] = run_test_file(test_file)
        else:
            print(f"⚠ {test_file} not found, skipping")
            results[test_file] = None
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_file, result in results.items():
        if result is True:
            print(f"✓ PASSED: {test_file}")
        elif result is False:
            print(f"✗ FAILED: {test_file}")
        else:
            print(f"⚠ SKIPPED: {test_file}")
    
    print("\n" + "=" * 60)
    print(f"Total: {passed} passed, {failed} failed, {skipped} skipped")
    print("=" * 60)
    
    # Note about database tests
    print("\nNote: Database-dependent tests (test_database_manager.py,")
    print("test_database_manager_manual.py) require active database connection")
    print("and were not included in this automated run.")
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
