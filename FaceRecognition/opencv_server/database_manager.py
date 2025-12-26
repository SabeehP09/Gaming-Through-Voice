"""
Database Manager for Face Recognition System

This module handles all database operations for storing and retrieving
face embeddings. It uses parameterized queries to prevent SQL injection
and provides a clean interface for embedding management.

Requirements: 1.3, 10.2, 10.5
"""

import pyodbc
import json
import logging
from typing import List, Optional
from datetime import datetime
import numpy as np


class DatabaseManager:
    """
    Manages database operations for face embeddings.
    
    This class provides methods to:
    - Store face embeddings for users
    - Retrieve all embeddings for a specific user
    - Delete embeddings for a user
    
    All database operations use parameterized queries to prevent SQL injection.
    """
    
    def __init__(self, connection_string: str):
        """
        Initialize the DatabaseManager with a connection string.
        
        Args:
            connection_string: SQL Server connection string from config
            
        Raises:
            pyodbc.Error: If connection to database fails
        """
        self.connection_string = connection_string
        self.logger = logging.getLogger(__name__)
        
        # Test the connection on initialization
        try:
            conn = self._get_connection()
            conn.close()
            self.logger.info("Database connection established successfully")
        except pyodbc.Error as e:
            self.logger.error(f"Failed to connect to database: {e}")
            raise
    
    def _get_connection(self) -> pyodbc.Connection:
        """
        Create and return a new database connection.
        
        Returns:
            pyodbc.Connection: Active database connection
            
        Raises:
            pyodbc.Error: If connection fails
        """
        return pyodbc.connect(self.connection_string)
    
    def _validate_user_id(self, user_id: int) -> None:
        """
        SECURITY: Validate user ID to prevent SQL injection and invalid inputs.
        
        Args:
            user_id: The user ID to validate
            
        Raises:
            ValueError: If user_id is invalid
            
        Requirements: 10.2 - SQL injection prevention
        """
        if not isinstance(user_id, int):
            raise ValueError(f"User ID must be an integer, got {type(user_id)}")
        
        if user_id <= 0:
            raise ValueError(f"User ID must be positive, got {user_id}")
        
        # Additional check: user_id should be reasonable (prevent overflow attacks)
        if user_id > 2147483647:  # Max INT in SQL Server
            raise ValueError(f"User ID exceeds maximum allowed value: {user_id}")
    
    def store_embedding(self, user_id: int, embedding: np.ndarray) -> bool:
        """
        Store a face embedding for a user in the database.
        
        The embedding is stored as a JSON array of floats. This method uses
        parameterized queries to prevent SQL injection attacks.
        
        SECURITY: Uses parameterized queries and input validation to prevent SQL injection.
        
        Args:
            user_id: The ID of the user (must exist in Users table)
            embedding: 128-dimensional numpy array representing the face
            
        Returns:
            bool: True if storage was successful, False otherwise
            
        Raises:
            ValueError: If embedding is not a valid numpy array or user_id is invalid
            pyodbc.Error: If database operation fails
            
        Requirements: 1.3, 10.2, 10.5
        """
        # SECURITY: Validate user_id to prevent SQL injection
        # Requirements: 10.2
        self._validate_user_id(user_id)
        
        # Validate embedding
        if not isinstance(embedding, np.ndarray):
            raise ValueError("Embedding must be a numpy array")
        
        if embedding.size == 0:
            raise ValueError("Embedding cannot be empty")
        
        # Convert numpy array to JSON string
        embedding_json = json.dumps(embedding.tolist())
        
        # Use parameterized query to prevent SQL injection
        query = """
            INSERT INTO FaceEmbeddings (UserId, EmbeddingVector, CreatedDate)
            VALUES (?, ?, ?)
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Execute with parameters
            cursor.execute(query, (user_id, embedding_json, datetime.now()))
            conn.commit()
            
            cursor.close()
            conn.close()
            
            self.logger.info(f"Successfully stored embedding for user {user_id}")
            return True
            
        except pyodbc.Error as e:
            self.logger.error(f"Failed to store embedding for user {user_id}: {e}")
            raise
    
    def get_embeddings_for_user(self, user_id: int) -> List[np.ndarray]:
        """
        Retrieve all face embeddings for a specific user.
        
        This method uses parameterized queries to prevent SQL injection.
        
        SECURITY: Uses parameterized queries and input validation to prevent SQL injection.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            List[np.ndarray]: List of embeddings (128-dimensional numpy arrays)
                             Returns empty list if no embeddings found
            
        Raises:
            ValueError: If user_id is invalid
            pyodbc.Error: If database operation fails
            
        Requirements: 1.3, 10.2, 10.5
        """
        # SECURITY: Validate user_id to prevent SQL injection
        # Requirements: 10.2
        self._validate_user_id(user_id)
        
        # Use parameterized query to prevent SQL injection
        query = """
            SELECT EmbeddingVector
            FROM FaceEmbeddings
            WHERE UserId = ?
            ORDER BY CreatedDate DESC
        """
        
        embeddings = []
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Execute with parameter
            cursor.execute(query, (user_id,))
            
            # Fetch all results
            rows = cursor.fetchall()
            
            for row in rows:
                # Parse JSON string back to numpy array
                embedding_list = json.loads(row[0])
                embedding = np.array(embedding_list, dtype=np.float32)
                embeddings.append(embedding)
            
            cursor.close()
            conn.close()
            
            self.logger.info(f"Retrieved {len(embeddings)} embeddings for user {user_id}")
            return embeddings
            
        except pyodbc.Error as e:
            self.logger.error(f"Failed to retrieve embeddings for user {user_id}: {e}")
            raise
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"Failed to parse embedding data for user {user_id}: {e}")
            raise
    
    def delete_embeddings_for_user(self, user_id: int) -> int:
        """
        Delete all face embeddings for a specific user.
        
        This method uses parameterized queries to prevent SQL injection.
        Useful for user data removal and privacy compliance.
        
        SECURITY: Uses parameterized queries and input validation to prevent SQL injection.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            int: Number of embeddings deleted
            
        Raises:
            ValueError: If user_id is invalid
            pyodbc.Error: If database operation fails
            
        Requirements: 1.3, 10.2, 10.5
        """
        # SECURITY: Validate user_id to prevent SQL injection
        # Requirements: 10.2
        self._validate_user_id(user_id)
        
        # Use parameterized query to prevent SQL injection
        query = """
            DELETE FROM FaceEmbeddings
            WHERE UserId = ?
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            # Execute with parameter
            cursor.execute(query, (user_id,))
            rows_affected = cursor.rowcount
            conn.commit()
            
            cursor.close()
            conn.close()
            
            self.logger.info(f"Deleted {rows_affected} embeddings for user {user_id}")
            return rows_affected
            
        except pyodbc.Error as e:
            self.logger.error(f"Failed to delete embeddings for user {user_id}: {e}")
            raise
    
    def get_embedding_count_for_user(self, user_id: int) -> int:
        """
        Get the count of embeddings stored for a user.
        
        This is a helper method useful for validation and testing.
        
        SECURITY: Uses parameterized queries and input validation to prevent SQL injection.
        
        Args:
            user_id: The ID of the user
            
        Returns:
            int: Number of embeddings stored for the user
            
        Raises:
            ValueError: If user_id is invalid
            pyodbc.Error: If database operation fails
        """
        # SECURITY: Validate user_id to prevent SQL injection
        # Requirements: 10.2
        self._validate_user_id(user_id)
        
        query = """
            SELECT COUNT(*)
            FROM FaceEmbeddings
            WHERE UserId = ?
        """
        
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(query, (user_id,))
            count = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            return count
            
        except pyodbc.Error as e:
            self.logger.error(f"Failed to get embedding count for user {user_id}: {e}")
            raise
