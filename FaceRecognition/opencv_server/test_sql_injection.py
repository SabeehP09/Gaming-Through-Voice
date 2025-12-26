"""
Test SQL Injection Prevention

This test file verifies that the database manager properly prevents SQL injection attacks
by testing with malicious inputs.

Requirements: 10.2 - SQL injection prevention
"""

import pytest
import numpy as np
from unittest.mock import Mock, patch
from database_manager import DatabaseManager


# Mock connection string for testing
TEST_CONNECTION_STRING = "DRIVER={SQL Server};SERVER=localhost;DATABASE=GamingVoiceRecognition;Trusted_Connection=yes;"


class TestSQLInjectionPrevention:
    """
    Test suite for SQL injection prevention.
    
    Requirements: 10.2
    """
    
    @patch('database_manager.pyodbc.connect')
    def test_malicious_user_id_string(self, mock_connect):
        """
        Test that string-based SQL injection attempts are rejected.
        
        Requirements: 10.2
        """
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager(TEST_CONNECTION_STRING)
        
        # Attempt SQL injection with string
        malicious_user_id = "1; DROP TABLE FaceEmbeddings; --"
        embedding = np.random.rand(128).astype(np.float32)
        
        # Should raise ValueError due to type validation
        with pytest.raises(ValueError, match="User ID must be an integer"):
            db.store_embedding(malicious_user_id, embedding)
    
    @patch('database_manager.pyodbc.connect')
    def test_malicious_user_id_negative(self, mock_connect):
        """
        Test that negative user IDs are rejected.
        
        Requirements: 10.2
        """
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager(TEST_CONNECTION_STRING)
        
        # Attempt with negative user ID
        malicious_user_id = -1
        embedding = np.random.rand(128).astype(np.float32)
        
        # Should raise ValueError due to validation
        with pytest.raises(ValueError, match="User ID must be positive"):
            db.store_embedding(malicious_user_id, embedding)
    
    @patch('database_manager.pyodbc.connect')
    def test_malicious_user_id_zero(self, mock_connect):
        """
        Test that zero user ID is rejected.
        
        Requirements: 10.2
        """
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager(TEST_CONNECTION_STRING)
        
        # Attempt with zero user ID
        malicious_user_id = 0
        embedding = np.random.rand(128).astype(np.float32)
        
        # Should raise ValueError due to validation
        with pytest.raises(ValueError, match="User ID must be positive"):
            db.store_embedding(malicious_user_id, embedding)
    
    @patch('database_manager.pyodbc.connect')
    def test_malicious_user_id_overflow(self, mock_connect):
        """
        Test that extremely large user IDs are rejected (overflow attack).
        
        Requirements: 10.2
        """
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager(TEST_CONNECTION_STRING)
        
        # Attempt with overflow user ID
        malicious_user_id = 9999999999999999999
        embedding = np.random.rand(128).astype(np.float32)
        
        # Should raise ValueError due to validation
        with pytest.raises(ValueError, match="exceeds maximum allowed value"):
            db.store_embedding(malicious_user_id, embedding)
    
    @patch('database_manager.pyodbc.connect')
    def test_malicious_user_id_get_embeddings(self, mock_connect):
        """
        Test that SQL injection attempts in get_embeddings are rejected.
        
        Requirements: 10.2
        """
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager(TEST_CONNECTION_STRING)
        
        # Attempt SQL injection in get operation
        malicious_user_id = "1 OR 1=1"
        
        # Should raise ValueError due to type validation
        with pytest.raises(ValueError, match="User ID must be an integer"):
            db.get_embeddings_for_user(malicious_user_id)
    
    @patch('database_manager.pyodbc.connect')
    def test_malicious_user_id_delete_embeddings(self, mock_connect):
        """
        Test that SQL injection attempts in delete_embeddings are rejected.
        
        Requirements: 10.2
        """
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager(TEST_CONNECTION_STRING)
        
        # Attempt SQL injection in delete operation
        malicious_user_id = "1; DELETE FROM Users; --"
        
        # Should raise ValueError due to type validation
        with pytest.raises(ValueError, match="User ID must be an integer"):
            db.delete_embeddings_for_user(malicious_user_id)
    
    @patch('database_manager.pyodbc.connect')
    def test_valid_user_id_accepted(self, mock_connect):
        """
        Test that valid user IDs are accepted (positive test).
        
        Requirements: 10.2
        """
        # Mock database connection
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        
        db = DatabaseManager(TEST_CONNECTION_STRING)
        
        # Valid user ID should pass validation
        valid_user_id = 42
        
        # This should not raise an error during validation
        # (may fail at database level if user doesn't exist, but that's expected)
        try:
            db._validate_user_id(valid_user_id)
        except ValueError:
            pytest.fail("Valid user ID was rejected")
    
    def test_parameterized_query_usage(self):
        """
        Verify that parameterized queries are used (code inspection test).
        
        This test verifies that the database manager uses parameterized queries
        by checking the query strings contain '?' placeholders.
        
        Requirements: 10.2
        """
        import inspect
        
        # Get source code of store_embedding method
        source = inspect.getsource(DatabaseManager.store_embedding)
        
        # Verify parameterized query is used (contains ?)
        assert '?' in source, "store_embedding should use parameterized queries with '?' placeholders"
        assert 'VALUES (?, ?, ?)' in source, "store_embedding should use parameterized INSERT"
        
        # Get source code of get_embeddings_for_user method
        source = inspect.getsource(DatabaseManager.get_embeddings_for_user)
        
        # Verify parameterized query is used
        assert '?' in source, "get_embeddings_for_user should use parameterized queries"
        assert 'WHERE UserId = ?' in source, "get_embeddings_for_user should use parameterized WHERE clause"
        
        # Get source code of delete_embeddings_for_user method
        source = inspect.getsource(DatabaseManager.delete_embeddings_for_user)
        
        # Verify parameterized query is used
        assert '?' in source, "delete_embeddings_for_user should use parameterized queries"
        assert 'WHERE UserId = ?' in source, "delete_embeddings_for_user should use parameterized WHERE clause"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
