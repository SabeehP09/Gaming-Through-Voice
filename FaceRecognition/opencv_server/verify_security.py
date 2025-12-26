"""
Security Verification Script

This script verifies that all security measures are properly implemented.

Requirements: 10.1, 10.2, 10.3, 10.4, 10.5
"""

import os
import sys
import inspect
from database_manager import DatabaseManager


def verify_no_image_files():
    """
    Verify that no image files exist in the server directory.
    
    Requirements: 10.1, 10.3
    """
    print("=" * 60)
    print("SECURITY VERIFICATION: No Image Files on Disk")
    print("=" * 60)
    
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    current_dir = os.getcwd()
    image_files_found = []
    
    for root, dirs, files in os.walk(current_dir):
        # Skip certain directories
        if any(skip in root for skip in ['models', 'logs', '.git', '__pycache__', '.pytest_cache']):
            continue
            
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                image_files_found.append(os.path.join(root, file))
    
    if image_files_found:
        print("❌ FAILED: Image files found on disk:")
        for img_file in image_files_found:
            print(f"   - {img_file}")
        return False
    else:
        print("✅ PASSED: No image files found on disk")
        print("   Only embeddings are stored, not raw images")
        return True


def verify_parameterized_queries():
    """
    Verify that all database methods use parameterized queries.
    
    Requirements: 10.2
    """
    print("\n" + "=" * 60)
    print("SECURITY VERIFICATION: Parameterized Queries")
    print("=" * 60)
    
    methods_to_check = [
        'store_embedding',
        'get_embeddings_for_user',
        'delete_embeddings_for_user',
        'get_embedding_count_for_user'
    ]
    
    all_passed = True
    
    for method_name in methods_to_check:
        method = getattr(DatabaseManager, method_name)
        source = inspect.getsource(method)
        
        # Check for parameterized query placeholder
        if '?' in source and 'execute' in source:
            print(f"✅ {method_name}: Uses parameterized queries")
        else:
            print(f"❌ {method_name}: May not use parameterized queries")
            all_passed = False
    
    if all_passed:
        print("\n✅ PASSED: All database methods use parameterized queries")
    else:
        print("\n❌ FAILED: Some methods may not use parameterized queries")
    
    return all_passed


def verify_input_validation():
    """
    Verify that input validation is implemented.
    
    Requirements: 10.2, 10.4
    """
    print("\n" + "=" * 60)
    print("SECURITY VERIFICATION: Input Validation")
    print("=" * 60)
    
    # Check if _validate_user_id method exists
    if hasattr(DatabaseManager, '_validate_user_id'):
        print("✅ User ID validation method exists")
        
        # Check if validation is called in methods
        methods_to_check = [
            'store_embedding',
            'get_embeddings_for_user',
            'delete_embeddings_for_user',
            'get_embedding_count_for_user'
        ]
        
        all_validated = True
        for method_name in methods_to_check:
            method = getattr(DatabaseManager, method_name)
            source = inspect.getsource(method)
            
            if '_validate_user_id' in source:
                print(f"✅ {method_name}: Validates user ID")
            else:
                print(f"❌ {method_name}: Does not validate user ID")
                all_validated = False
        
        if all_validated:
            print("\n✅ PASSED: All methods validate user IDs")
            return True
        else:
            print("\n❌ FAILED: Some methods do not validate user IDs")
            return False
    else:
        print("❌ FAILED: User ID validation method not found")
        return False


def verify_foreign_key_constraint():
    """
    Verify that database schema has foreign key constraint.
    
    Requirements: 10.5
    """
    print("\n" + "=" * 60)
    print("SECURITY VERIFICATION: Foreign Key Constraint")
    print("=" * 60)
    
    schema_file = 'database_schema.sql'
    
    if not os.path.exists(schema_file):
        print(f"❌ FAILED: Schema file not found: {schema_file}")
        return False
    
    with open(schema_file, 'r') as f:
        schema_content = f.read()
    
    # Check for foreign key constraint
    if 'FOREIGN KEY' in schema_content and 'REFERENCES' in schema_content and 'Users' in schema_content:
        print("✅ Foreign key constraint found in schema")
        
        # Check for cascade delete
        if 'ON DELETE CASCADE' in schema_content:
            print("✅ Cascade delete configured")
        else:
            print("⚠️  Warning: Cascade delete not configured")
        
        # Check for index
        if 'INDEX' in schema_content and 'UserId' in schema_content:
            print("✅ Index on UserId found")
        else:
            print("⚠️  Warning: Index on UserId not found")
        
        print("\n✅ PASSED: Foreign key constraint properly configured")
        return True
    else:
        print("❌ FAILED: Foreign key constraint not found in schema")
        return False


def verify_no_image_storage_in_code():
    """
    Verify that code does not write images to disk.
    
    Requirements: 10.1, 10.3
    """
    print("\n" + "=" * 60)
    print("SECURITY VERIFICATION: No Image Storage in Code")
    print("=" * 60)
    
    # Check app.py for image writing operations
    with open('app.py', 'r') as f:
        app_content = f.read()
    
    dangerous_operations = [
        'cv2.imwrite',
        'cv2.imencode',
        'Image.save',
        'open(.*wb)',
    ]
    
    issues_found = []
    for operation in dangerous_operations:
        if operation in app_content:
            issues_found.append(operation)
    
    if issues_found:
        print("❌ FAILED: Potentially dangerous image storage operations found:")
        for issue in issues_found:
            print(f"   - {issue}")
        return False
    else:
        print("✅ PASSED: No image storage operations found in code")
        print("   Images are processed in-memory only")
        return True


def main():
    """
    Run all security verifications.
    """
    print("\n" + "=" * 60)
    print("OPENCV FACE RECOGNITION SECURITY VERIFICATION")
    print("=" * 60)
    print()
    
    results = []
    
    # Run all verification checks
    results.append(("No Image Files", verify_no_image_files()))
    results.append(("Parameterized Queries", verify_parameterized_queries()))
    results.append(("Input Validation", verify_input_validation()))
    results.append(("Foreign Key Constraint", verify_foreign_key_constraint()))
    results.append(("No Image Storage in Code", verify_no_image_storage_in_code()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SECURITY VERIFICATION SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{status}: {check_name}")
    
    print("\n" + "=" * 60)
    print(f"OVERALL: {passed}/{total} checks passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All security verifications passed!")
        print("The system is properly secured against:")
        print("  • Raw image storage")
        print("  • SQL injection attacks")
        print("  • Invalid user ID inputs")
        print("  • Unauthorized data access")
        return 0
    else:
        print(f"\n⚠️  {total - passed} security verification(s) failed")
        print("Please review the failed checks above")
        return 1


if __name__ == '__main__':
    sys.exit(main())
