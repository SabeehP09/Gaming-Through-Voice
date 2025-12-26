"""
Face recognition module using OpenCV DNN for embedding extraction and comparison.
"""
import cv2
import numpy as np
import os
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class FaceRecognizer:
    """
    Face recognizer using OpenCV's DNN-based face recognition.
    Uses OpenFace model to extract 128-dimensional embeddings and compare them.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the face recognizer with OpenFace model.
        
        Args:
            config: Configuration dictionary containing face_recognition settings
            
        Raises:
            FileNotFoundError: If model file is not found
            Exception: If model loading fails
        """
        self.config = config.get('face_recognition', {})
        self.model_path = self.config.get('model_path', 'models/openface_nn4.small2.v1.t7')
        self.authentication_threshold = self.config.get('authentication_threshold', 0.85)
        
        # Load the OpenFace model
        self.model = None
        self._load_model()
        
        logger.info(f"FaceRecognizer initialized with threshold: {self.authentication_threshold}")
    
    def _load_model(self):
        """
        Load the OpenFace face recognition model.
        
        Raises:
            FileNotFoundError: If model file doesn't exist
            Exception: If model loading fails
        """
        try:
            # Check if model file exists
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            # Load the OpenFace model using Torch backend
            self.model = cv2.dnn.readNetFromTorch(self.model_path)
            logger.info(f"OpenFace model loaded successfully from {self.model_path}")
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load face recognition model: {e}")
            raise Exception(f"Failed to load face recognition model: {e}")
    
    def extract_embedding(self, face_image: np.ndarray) -> np.ndarray:
        """
        Extract 128-dimensional face embedding from a preprocessed face image.
        
        Args:
            face_image: Preprocessed face image as numpy array (normalized, 160x160, BGR)
            
        Returns:
            128-dimensional feature vector as numpy array
            
        Raises:
            ValueError: If face_image is invalid
            Exception: If embedding extraction fails
        """
        if face_image is None or face_image.size == 0:
            raise ValueError("Invalid face image: face_image is None or empty")
        
        try:
            # Create a blob from the face image
            # OpenFace model expects 96x96 input, but we'll use 160x160 and let it resize
            blob = cv2.dnn.blobFromImage(
                face_image,
                1.0 / 255.0,  # Scale factor (already normalized, but ensure [0,1])
                (96, 96),      # Target size for OpenFace
                (0, 0, 0),     # Mean subtraction (already normalized)
                swapRB=False,  # Don't swap R and B channels
                crop=False
            )
            
            # Pass the blob through the network
            self.model.setInput(blob)
            embedding = self.model.forward()
            
            # Flatten to 1D array
            embedding = embedding.flatten()
            
            # Verify embedding dimension
            if embedding.shape[0] != 128:
                raise Exception(f"Unexpected embedding dimension: {embedding.shape[0]}, expected 128")
            
            logger.debug(f"Extracted embedding with shape: {embedding.shape}")
            return embedding
            
        except ValueError as e:
            logger.error(f"Invalid input for embedding extraction: {e}")
            raise
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}")
            raise Exception(f"Embedding extraction failed: {e}")
    
    def compare_embeddings(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compare two face embeddings using cosine similarity.
        
        Cosine similarity measures the cosine of the angle between two vectors.
        Returns a value between -1 and 1, but we normalize to [0, 1] range where:
        - 1.0 means identical faces
        - 0.0 means completely different faces
        
        Args:
            embedding1: First 128-dimensional embedding
            embedding2: Second 128-dimensional embedding
            
        Returns:
            Similarity score between 0.0 and 1.0
            
        Raises:
            ValueError: If embeddings are invalid or have different dimensions
        """
        if embedding1 is None or embedding2 is None:
            raise ValueError("Embeddings cannot be None")
        
        if embedding1.size == 0 or embedding2.size == 0:
            raise ValueError("Embeddings cannot be empty")
        
        if embedding1.shape != embedding2.shape:
            raise ValueError(
                f"Embedding dimensions must match: {embedding1.shape} vs {embedding2.shape}"
            )
        
        if embedding1.shape[0] != 128:
            raise ValueError(f"Expected 128-dimensional embeddings, got {embedding1.shape[0]}")
        
        try:
            # Calculate cosine similarity
            # cosine_similarity = (A · B) / (||A|| * ||B||)
            dot_product = np.dot(embedding1, embedding2)
            norm1 = np.linalg.norm(embedding1)
            norm2 = np.linalg.norm(embedding2)
            
            # Avoid division by zero
            if norm1 == 0 or norm2 == 0:
                logger.warning("One or both embeddings have zero norm")
                return 0.0
            
            cosine_similarity = dot_product / (norm1 * norm2)
            
            # Normalize from [-1, 1] to [0, 1] range
            # cosine_similarity of 1 -> similarity of 1.0
            # cosine_similarity of -1 -> similarity of 0.0
            similarity = (cosine_similarity + 1.0) / 2.0
            
            # Clamp to [0, 1] range to handle floating point errors
            similarity = np.clip(similarity, 0.0, 1.0)
            
            logger.debug(f"Cosine similarity: {cosine_similarity:.4f}, Normalized: {similarity:.4f}")
            return float(similarity)
            
        except Exception as e:
            logger.error(f"Embedding comparison failed: {e}")
            raise Exception(f"Embedding comparison failed: {e}")
