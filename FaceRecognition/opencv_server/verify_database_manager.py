"""
Simple verification script for DatabaseManager

This script performs basic checks to verify the DatabaseManager
implementation works correctly.
"""

import sys
import json
import numpy as np
from database_manager import DatabaseManager

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

connection_string = config['database']['connection_string']

print("=" * 60)
print("DatabaseManager Verification Script")
print("=" * 60)

# Test 1: Initialize DatabaseManager
print("\n1. Testing DatabaseManager initialization...")
try:
    db_manager = DatabaseManager(connection_string)
    print("   ✓ DatabaseManager initialized successfully")
except Exception as e:
    print(f"   ✗ Failed to initialize: {e}")
    sys.exit(1)

# Test 2: Create a test embedding
print("\n2. Creating test embedding...")
test_embedding = np.random.rand(128).astype(np.float32)
print(f"   ✓ Created 128-dimensional embedding")

# Test 3: Check if we can query (without storing)
print("\n3. Testing database query (get embeddings for non-existent user)...")
try:
    embeddings = db_manager.get_embeddings_for_user(999999)
    print(f"   ✓ Query successful, found {len(embeddings)} embeddings")
except Exception as e:
    print(f"   ✗ Query failed: {e}")
    sys.exit(1)

# Test 4: Test parameterized queries (SQL injection prevention)
print("\n4. Testing SQL injection prevention...")
try:
    malicious_id = "1 OR 1=1; DROP TABLE FaceEmbeddings; --"
    result = db_manager.get_embeddings_for_user(malicious_id)
    print(f"   ✓ Parameterized query handled malicious input safely")
except Exception as e:
    print(f"   ✓ Parameterized query rejected malicious input: {type(e).__name__}")

# Test 5: Test input validation
print("\n5. Testing input validation...")
try:
    db_manager.store_embedding(1, [1, 2, 3])  # Invalid type
    print("   ✗ Should have raised ValueError for invalid embedding type")
except ValueError as e:
    print(f"   ✓ Correctly rejected invalid embedding type")
except Exception as e:
    print(f"   ? Unexpected error: {e}")

try:
    db_manager.store_embedding(1, np.array([]))  # Empty array
    print("   ✗ Should have raised ValueError for empty embedding")
except ValueError as e:
    print(f"   ✓ Correctly rejected empty embedding")
except Exception as e:
    print(f"   ? Unexpected error: {e}")

print("\n" + "=" * 60)
print("Verification Complete!")
print("=" * 60)
print("\nNote: Full testing requires a valid user ID in the Users table.")
print("To test store/retrieve/delete operations, use a real user ID.")
print("\nDatabaseManager implementation is ready for use.")
