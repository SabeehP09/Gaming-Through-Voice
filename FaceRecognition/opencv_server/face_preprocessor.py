"""
Face preprocessing module for alignment and normalization.
"""
import cv2
import numpy as np
import logging
from typing import Tuple

logger = logging.getLogger(__name__)


class FacePreprocessor:
    """
    Face preprocessor for extracting, aligning, and normalizing face regions.
    Prepares faces for embedding extraction.
    """
    
    def __init__(self, target_size: Tuple[int, int] = (160, 160), 
                 enable_histogram_equalization: bool = True):
        """
        Initialize the face preprocessor.
        
        Args:
            target_size: Target size for aligned faces (width, height)
            enable_histogram_equalization: Whether to apply histogram equalization for lighting normalization
        """
        self.target_size = target_size
        self.enable_histogram_equalization = enable_histogram_equalization
        logger.info(f"FacePreprocessor initialized with target size: {target_size}, "
                   f"histogram equalization: {enable_histogram_equalization}")
    
    def extract_face_region(self, image: np.ndarray, box: Tuple[int, int, int, int], 
                           padding: float = 0.2) -> np.ndarray:
        """
        Extract face region from image with padding.
        
        Args:
            image: Input image as numpy array (BGR format)
            box: Bounding box as (x, y, width, height)
            padding: Padding factor (0.2 = 20% padding on each side)
            
        Returns:
            Extracted face region as numpy array
            
        Raises:
            ValueError: If image or box is invalid
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid image: image is None or empty")
        
        x, y, w, h = box
        
        if w <= 0 or h <= 0:
            raise ValueError(f"Invalid bounding box dimensions: width={w}, height={h}")
        
        # Calculate padding
        pad_w = int(w * padding)
        pad_h = int(h * padding)
        
        # Calculate padded coordinates
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(image.shape[1], x + w + pad_w)
        y2 = min(image.shape[0], y + h + pad_h)
        
        # Extract face region
        face_region = image[y1:y2, x1:x2]
        
        if face_region.size == 0:
            raise ValueError("Extracted face region is empty")
        
        logger.debug(f"Extracted face region: {face_region.shape}")
        return face_region
    
    def align_face(self, face_region: np.ndarray) -> np.ndarray:
        """
        Align and normalize face for embedding extraction.
        
        This method:
        1. Resizes face to target size (160x160)
        2. Converts to grayscale
        3. Applies histogram equalization for lighting normalization
        4. Converts back to BGR (3 channels) for model compatibility
        5. Normalizes pixel values to [0, 1] range
        
        Args:
            face_region: Face region as numpy array
            
        Returns:
            Aligned and normalized face as numpy array
            
        Raises:
            ValueError: If face_region is invalid
        """
        if face_region is None or face_region.size == 0:
            raise ValueError("Invalid face region: face_region is None or empty")
        
        try:
            # Resize to target size
            resized = cv2.resize(face_region, self.target_size, interpolation=cv2.INTER_AREA)
            
            # Convert to grayscale for histogram equalization
            if len(resized.shape) == 3:
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
            else:
                gray = resized
            
            # Apply histogram equalization for lighting normalization
            equalized = cv2.equalizeHist(gray)
            
            # Convert back to BGR (3 channels) for model compatibility
            # Most face recognition models expect 3-channel input
            bgr = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
            
            # Normalize pixel values to [0, 1] range
            normalized = bgr.astype(np.float32) / 255.0
            
            logger.debug(f"Aligned face shape: {normalized.shape}, dtype: {normalized.dtype}")
            return normalized
            
        except Exception as e:
            logger.error(f"Face alignment failed: {e}")
            raise ValueError(f"Face alignment failed: {e}")
    
    def preprocess_face(self, image: np.ndarray, box: Tuple[int, int, int, int]) -> np.ndarray:
        """
        Complete preprocessing pipeline: extract, align, and normalize.
        
        Args:
            image: Input image as numpy array (BGR format)
            box: Bounding box as (x, y, width, height)
            
        Returns:
            Preprocessed face ready for embedding extraction
            
        Raises:
            ValueError: If preprocessing fails
        """
        try:
            # Extract face region with padding
            face_region = self.extract_face_region(image, box)
            
            # Align and normalize
            aligned_face = self.align_face(face_region)
            
            return aligned_face
            
        except Exception as e:
            logger.error(f"Face preprocessing failed: {e}")
            raise ValueError(f"Face preprocessing failed: {e}")
