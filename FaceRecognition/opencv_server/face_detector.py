"""
Face detection module using OpenCV DNN.
"""
import cv2
import numpy as np
import os
import logging
from typing import List, Tuple, Optional

logger = logging.getLogger(__name__)


class FaceDetector:
    """
    Face detector using OpenCV's DNN-based face detection.
    Uses Caffe model for accurate face detection.
    """
    
    def __init__(self, config: dict):
        """
        Initialize the face detector with DNN model.
        
        Args:
            config: Configuration dictionary containing face_detection settings
            
        Raises:
            FileNotFoundError: If model files are not found
            Exception: If model loading fails
        """
        self.config = config.get('face_detection', {})
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.min_face_size = self.config.get('min_face_size', 80)
        self.model_type = self.config.get('model_type', 'dnn')
        
        # Model paths
        self.prototxt_path = os.path.join('models', 'deploy.prototxt')
        self.model_path = os.path.join('models', 'res10_300x300_ssd_iter_140000.caffemodel')
        
        # Load the DNN model
        self.net = None
        self._load_model()
        
        logger.info(f"FaceDetector initialized with confidence threshold: {self.confidence_threshold}")
    
    def _load_model(self):
        """
        Load the DNN face detection model.
        
        Raises:
            FileNotFoundError: If model files don't exist
            Exception: If model loading fails
        """
        try:
            # Check if model files exist
            if not os.path.exists(self.prototxt_path):
                raise FileNotFoundError(f"Prototxt file not found: {self.prototxt_path}")
            
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Model file not found: {self.model_path}")
            
            # Load the model
            self.net = cv2.dnn.readNetFromCaffe(self.prototxt_path, self.model_path)
            logger.info("DNN face detection model loaded successfully")
            
        except FileNotFoundError as e:
            logger.error(f"Model file not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load face detection model: {e}")
            raise Exception(f"Failed to load face detection model: {e}")
    
    def detect_faces(self, image: np.ndarray) -> List[Tuple[Tuple[int, int, int, int], float]]:
        """
        Detect faces in an image using DNN.
        
        Args:
            image: Input image as numpy array (BGR format)
            
        Returns:
            List of tuples containing ((x, y, w, h), confidence) for each detected face
            where (x, y, w, h) is the bounding box and confidence is the detection score
            
        Raises:
            ValueError: If image is invalid
            Exception: If face detection fails
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid image: image is None or empty")
        
        try:
            # Get image dimensions
            h, w = image.shape[:2]
            
            # Create a blob from the image
            # The model expects 300x300 input with mean subtraction
            blob = cv2.dnn.blobFromImage(
                cv2.resize(image, (300, 300)),
                1.0,
                (300, 300),
                (104.0, 177.0, 123.0)
            )
            
            # Pass the blob through the network
            self.net.setInput(blob)
            detections = self.net.forward()
            
            # Process detections
            faces = []
            for i in range(detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                
                # Filter by confidence threshold
                if confidence > self.confidence_threshold:
                    # Get bounding box coordinates
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (x, y, x2, y2) = box.astype("int")
                    
                    # Convert to (x, y, width, height) format
                    width = x2 - x
                    height = y2 - y
                    
                    # Filter by minimum face size
                    if width >= self.min_face_size and height >= self.min_face_size:
                        # Ensure coordinates are within image bounds
                        x = max(0, x)
                        y = max(0, y)
                        width = min(width, w - x)
                        height = min(height, h - y)
                        
                        faces.append(((x, y, width, height), float(confidence)))
            
            logger.info(f"Detected {len(faces)} face(s) in image")
            return faces
            
        except Exception as e:
            logger.error(f"Face detection failed: {e}")
            raise Exception(f"Face detection failed: {e}")
