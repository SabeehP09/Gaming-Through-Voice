"""
Simple verification script for Flask API structure.
Checks that all endpoints are defined and imports work.
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def verify_api_structure():
    """Verify that the Flask API is properly structured"""
    print("=" * 60)
    print("Flask API Structure Verification")
    print("=" * 60)
    
    # Test 1: Import Flask app
    print("\n[Test 1] Importing Flask app...")
    try:
        from app import app
        print("✓ Flask app imported successfully")
    except Exception as e:
        print(f"✗ Failed to import Flask app: {e}")
        return False
    
    # Test 2: Check endpoints exist
    print("\n[Test 2] Checking endpoints...")
    try:
        rules = list(app.url_map.iter_rules())
        endpoints = [rule.rule for rule in rules]
        
        print(f"  Found {len(endpoints)} endpoints:")
        for endpoint in endpoints:
            print(f"    - {endpoint}")
        
        # Check required endpoints
        required_endpoints = ['/health', '/register', '/authenticate']
        for required in required_endpoints:
            if required in endpoints:
                print(f"  ✓ {required} endpoint exists")
            else:
                print(f"  ✗ {required} endpoint missing")
                return False
        
    except Exception as e:
        print(f"✗ Failed to check endpoints: {e}")
        return False
    
    # Test 3: Check endpoint methods
    print("\n[Test 3] Checking endpoint methods...")
    try:
        for rule in app.url_map.iter_rules():
            if rule.rule in ['/health', '/register', '/authenticate']:
                methods = ', '.join(rule.methods - {'HEAD', 'OPTIONS'})
                print(f"  {rule.rule}: {methods}")
                
                if rule.rule == '/health' and 'GET' not in rule.methods:
                    print(f"  ✗ /health should support GET")
                    return False
                
                if rule.rule in ['/register', '/authenticate'] and 'POST' not in rule.methods:
                    print(f"  ✗ {rule.rule} should support POST")
                    return False
        
        print("✓ All endpoint methods correct")
        
    except Exception as e:
        print(f"✗ Failed to check methods: {e}")
        return False
    
    # Test 4: Check imports
    print("\n[Test 4] Checking module imports...")
    try:
        from app import (
            face_detector, face_preprocessor, face_recognizer, 
            database_manager, decode_base64_image
        )
        print("✓ All required imports available")
    except Exception as e:
        print(f"✗ Failed to import modules: {e}")
        return False
    
    # Test 5: Check helper functions
    print("\n[Test 5] Checking helper functions...")
    try:
        from app import load_config, initialize_components, decode_base64_image
        print("✓ Helper functions defined:")
        print("  - load_config")
        print("  - initialize_components")
        print("  - decode_base64_image")
    except Exception as e:
        print(f"✗ Failed to check helper functions: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("API structure verification completed successfully! ✓")
    print("=" * 60)
    print("\nSummary:")
    print("  - Flask app structure: ✓")
    print("  - Required endpoints: ✓")
    print("  - Endpoint methods: ✓")
    print("  - Module imports: ✓")
    print("  - Helper functions: ✓")
    print("=" * 60)
    
    return True


if __name__ == "__main__":
    # Run verification
    success = verify_api_structure()
    
    if success:
        print("\n✓ Flask API structure is correct!")
        print("\nNext steps:")
        print("  1. Install flask-cors: pip install flask-cors")
        print("  2. Start the server: python app.py")
        print("  3. Test with real images using a client")
        sys.exit(0)
    else:
        print("\n✗ Flask API structure verification failed")
        sys.exit(1)
