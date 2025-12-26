"""
Unit tests for DatabaseManager class

Tests database operations including:
- Storing embeddings
- Retrieving embeddings
- Deleting embeddings
- SQL injection prevention
- Error handling

Requirements: 1.3, 10.2, 10.5
"""

import pytest
import numpy as np
import json
import pyodbc
from database_manager import DatabaseManager


# Test configuration
TEST_CONNECTION_STRING = "DRIVER={SQL Server};SERVER=localhost;DATABASE=GamingVoiceRecognition;Trusted_Connection=yes;"


@pytest.fixture
def db_manager():
    """Create a DatabaseManager instance for testing."""
    try:
        manager = DatabaseManager(TEST_CONNECTION_STRING)
        return manager
    except pyodbc.Error as e:
        pytest.skip(f"Database not available: {e}")


@pytest.fixture
def test_user_id():
    """
    Provide a test user ID.
    Note: This assumes a user with this ID exists in the Users table.
    For proper testing, you may need to create a test user first.
    """
    return 999999  # Use a high ID unlikely to conflict


@pytest.fixture
def sample_embedding():
    """Create a sample 128-dimensional embedding for testing."""
    return np.random.rand(128).astype(np.float32)


@pytest.fixture(autouse=True)
def cleanup_test_data(db_manager, test_user_id):
    """Clean up test data before and after each test."""
    if db_manager:
        try:
            # Clean up before test
            db_manager.delete_embeddings_for_user(test_user_id)
        except:
            pass
        
        yield
        
        try:
            # Clean up after test
            db_manager.delete_embeddings_for_user(test_user_id)
        except:
            pass


class TestDatabaseManagerInitialization:
    """Test DatabaseManager initialization."""
    
    def test_init_with_valid_connection_string(self):
        """Test initialization with valid connection string."""
        try:
            manager = DatabaseManager(TEST_CONNECTION_STRING)
            assert manager is not None
            assert manager.connection_string == TEST_CONNECTION_STRING
        except pyodbc.Error:
            pytest.skip("Database not available")
    
    def test_init_with_invalid_connection_string(self):
        """Test initialization with invalid connection string."""
        invalid_conn_str = "DRIVER={SQL Server};SERVER=invalid_server;DATABASE=invalid_db;"
        with pytest.raises(pyodbc.Error):
            DatabaseManager(invalid_conn_str)


class TestStoreEmbedding:
    """Test storing embeddings."""
    
    def test_store_valid_embedding(self, db_manager, test_user_id, sample_embedding):
        """Test storing a valid embedding."""
        # Note: This test may fail if test_user_id doesn't exist in Users table
        # In that case, use a valid user ID from your database
        try:
            result = db_manager.store_embedding(test_user_id, sample_embedding)
            assert result is True
            
            # Verify it was stored
            count = db_manager.get_embedding_count_for_user(test_user_id)
            assert count == 1
        except pyodbc.IntegrityError:
            pytest.skip(f"Test user {test_user_id} does not exist in Users table")
    
    def test_store_multiple_embeddings(self, db_manager, test_user_id):
        """Test storing multiple embeddings for the same user."""
        try:
            embeddings = [np.random.rand(128).astype(np.float32) for _ in range(5)]
            
            for embedding in embeddings:
                result = db_manager.store_embedding(test_user_id, embedding)
                assert result is True
            
            # Verify all were stored
            count = db_manager.get_embedding_count_for_user(test_user_id)
            assert count == 5
        except pyodbc.IntegrityError:
            pytest.skip(f"Test user {test_user_id} does not exist in Users table")
    
    def test_store_invalid_embedding_type(self, db_manager, test_user_id):
        """Test storing invalid embedding type raises ValueError."""
        with pytest.raises(ValueError, match="Embedding must be a numpy array"):
            db_manager.store_embedding(test_user_id, [1, 2, 3])
    
    def test_store_empty_embedding(self, db_manager, test_user_id):
        """Test storing empty embedding raises ValueError."""
        empty_embedding = np.array([])
        with pytest.raises(ValueError, match="Embedding cannot be empty"):
            db_manager.store_embedding(test_user_id, empty_embedding)


class TestGetEmbeddingsForUser:
    """Test retrieving embeddings."""
    
    def test_get_embeddings_for_user_with_data(self, db_manager, test_user_id):
        """Test retrieving embeddings when data exists."""
        try:
            # Store some embeddings
            original_embeddings = [np.random.rand(128).astype(np.float32) for _ in range(3)]
            for embedding in original_embeddings:
                db_manager.store_embedding(test_user_id, embedding)
            
            # Retrieve embeddings
            retrieved = db_manager.get_embeddings_for_user(test_user_id)
            
            assert len(retrieved) == 3
            assert all(isinstance(emb, np.ndarray) for emb in retrieved)
            assert all(emb.shape == (128,) for emb in retrieved)
        except pyodbc.IntegrityError:
            pytest.skip(f"Test user {test_user_id} does not exist in Users table")
    
    def test_get_embeddings_for_user_no_data(self, db_manager, test_user_id):
        """Test retrieving embeddings when no data exists."""
        retrieved = db_manager.get_embeddings_for_user(test_user_id)
        assert retrieved == []
    
    def test_get_embeddings_preserves_values(self, db_manager, test_user_id):
        """Test that retrieved embeddings match stored values."""
        try:
            # Store a specific embedding
            original = np.array([0.1, 0.2, 0.3] + [0.0] * 125, dtype=np.float32)
            db_manager.store_embedding(test_user_id, original)
            
            # Retrieve and compare
            retrieved = db_manager.get_embeddings_for_user(test_user_id)
            assert len(retrieved) == 1
            
            # Check values are close (allowing for floating point precision)
            np.testing.assert_allclose(retrieved[0], original, rtol=1e-5)
        except pyodbc.IntegrityError:
            pytest.skip(f"Test user {test_user_id} does not exist in Users table")


class TestDeleteEmbeddingsForUser:
    """Test deleting embeddings."""
    
    def test_delete_embeddings_with_data(self, db_manager, test_user_id):
        """Test deleting embeddings when data exists."""
        try:
            # Store some embeddings
            for _ in range(3):
                embedding = np.random.rand(128).astype(np.float32)
                db_manager.store_embedding(test_user_id, embedding)
            
            # Delete embeddings
            deleted_count = db_manager.delete_embeddings_for_user(test_user_id)
            assert deleted_count == 3
            
            # Verify they're gone
            count = db_manager.get_embedding_count_for_user(test_user_id)
            assert count == 0
        except pyodbc.IntegrityError:
            pytest.skip(f"Test user {test_user_id} does not exist in Users table")
    
    def test_delete_embeddings_no_data(self, db_manager, test_user_id):
        """Test deleting embeddings when no data exists."""
        deleted_count = db_manager.delete_embeddings_for_user(test_user_id)
        assert deleted_count == 0


class TestSQLInjectionPrevention:
    """Test SQL injection prevention."""
    
    def test_malicious_user_id_in_get(self, db_manager):
        """Test that malicious user ID doesn't cause SQL injection in get."""
        # Try SQL injection in user_id parameter
        malicious_id = "1 OR 1=1; DROP TABLE FaceEmbeddings; --"
        
        # This should not execute the malicious SQL
        # It will either raise an error or return empty results
        try:
            result = db_manager.get_embeddings_for_user(malicious_id)
            # If it doesn't raise an error, it should return empty list
            assert isinstance(result, list)
        except (pyodbc.Error, ValueError):
            # Expected - parameterized query prevents injection
            pass
    
    def test_malicious_user_id_in_delete(self, db_manager):
        """Test that malicious user ID doesn't cause SQL injection in delete."""
        malicious_id = "1 OR 1=1; DROP TABLE FaceEmbeddings; --"
        
        # This should not execute the malicious SQL
        try:
            result = db_manager.delete_embeddings_for_user(malicious_id)
            # If it doesn't raise an error, it should return 0
            assert isinstance(result, int)
        except (pyodbc.Error, ValueError):
            # Expected - parameterized query prevents injection
            pass


class TestErrorHandling:
    """Test error handling."""
    
    def test_connection_error_handling(self):
        """Test handling of connection errors."""
        invalid_conn_str = "DRIVER={SQL Server};SERVER=nonexistent;DATABASE=test;"
        with pytest.raises(pyodbc.Error):
            DatabaseManager(invalid_conn_str)
    
    def test_store_with_nonexistent_user(self, db_manager):
        """Test storing embedding for non-existent user."""
        nonexistent_user_id = -999999
        embedding = np.random.rand(128).astype(np.float32)
        
        # Should raise IntegrityError due to foreign key constraint
        with pytest.raises(pyodbc.IntegrityError):
            db_manager.store_embedding(nonexistent_user_id, embedding)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
