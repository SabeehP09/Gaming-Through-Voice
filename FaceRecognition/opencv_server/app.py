"""
Flask REST API for OpenCV Face Recognition System

This module provides REST API endpoints for face registration and authentication.
It integrates face detection, preprocessing, recognition, and database storage.

Requirements: 6.1, 6.2, 6.3, 6.4, 8.3
"""

import os
import sys
import json
import base64
import logging
from logging.handlers import RotatingFileHandler
from io import BytesIO
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import cv2

# Import our modules
from face_detector import FaceDetector
from face_preprocessor import FacePreprocessor
from face_recognizer import FaceRecognizer
from database_manager import DatabaseManager


def setup_logging():
    """
    Configure comprehensive logging system with file and console handlers.
    
    Creates logs/ directory if it doesn't exist and sets up:
    - Console handler for INFO and above
    - File handler for all logs with rotation
    - Detailed formatting with timestamps
    
    Requirements: 8.3
    """
    # Create logs directory if it doesn't exist
    logs_dir = 'logs'
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)
        print(f"Created logs directory: {logs_dir}")
    
    # Create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Capture all levels
    
    # Remove existing handlers to avoid duplicates
    logger.handlers = []
    
    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    simple_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # File handler for all logs (with rotation)
    log_file = os.path.join(logs_dir, 'face_recognition_server.log')
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # File handler for errors only
    error_log_file = os.path.join(logs_dir, 'errors.log')
    error_handler = RotatingFileHandler(
        error_log_file,
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    return logging.getLogger(__name__)


# Setup logging
logger = setup_logging()
logger.info("="*80)
logger.info("OpenCV Face Recognition Server Starting")
logger.info("="*80)

# Initialize Flask app
app = Flask(__name__)

# Enable CORS for localhost
CORS(app, resources={r"/*": {"origins": ["http://localhost:*", "http://127.0.0.1:*"]}})


@app.before_request
def log_request():
    """
    Log all incoming API requests with timestamp and details.
    
    Requirements: 8.3
    """
    logger.info(f"API Request: {request.method} {request.path} from {request.remote_addr}")
    if request.method in ['POST', 'PUT', 'PATCH']:
        # Log request size but not the actual data (privacy)
        content_length = request.content_length or 0
        logger.debug(f"Request body size: {content_length} bytes")


@app.after_request
def log_response(response):
    """
    Log API response status codes.
    
    Requirements: 8.3
    """
    logger.info(f"API Response: {request.method} {request.path} - Status: {response.status_code}")
    return response

# Global variables for components
config = None
face_detector = None
face_preprocessor = None
face_recognizer = None
database_manager = None
models_loaded = False
database_connected = False


def load_config():
    """Load configuration from config.json"""
    global config
    try:
        config_path = 'config.json'
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            return False
        
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        logger.info("Configuration loaded successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        return False


def initialize_components():
    """Initialize all face recognition components"""
    global face_detector, face_preprocessor, face_recognizer, database_manager
    global models_loaded, database_connected
    
    try:
        # Load configuration
        if not load_config():
            logger.error("Configuration loading failed")
            return False
        
        # Initialize face detector
        logger.info("Initializing face detector...")
        try:
            face_detector = FaceDetector(config)
        except FileNotFoundError as e:
            logger.error(f"Face detection model files not found: {e}")
            logger.error("Please ensure model files are in the models/ directory")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize face detector: {e}", exc_info=True)
            return False
        
        # Initialize face preprocessor
        logger.info("Initializing face preprocessor...")
        try:
            face_preprocessor = FacePreprocessor(target_size=(160, 160))
        except Exception as e:
            logger.error(f"Failed to initialize face preprocessor: {e}", exc_info=True)
            return False
        
        # Initialize face recognizer
        logger.info("Initializing face recognizer...")
        try:
            face_recognizer = FaceRecognizer(config)
        except FileNotFoundError as e:
            logger.error(f"Face recognition model file not found: {e}")
            logger.error("Please ensure openface_nn4.small2.v1.t7 is in the models/ directory")
            return False
        except Exception as e:
            logger.error(f"Failed to initialize face recognizer: {e}", exc_info=True)
            return False
        
        models_loaded = True
        logger.info("All models loaded successfully")
        
        # Initialize database manager
        logger.info("Initializing database manager...")
        db_config = config.get('database', {})
        connection_string = db_config.get('connection_string')
        
        if not connection_string:
            logger.error("Database connection string not found in config")
            return False
        
        try:
            database_manager = DatabaseManager(connection_string)
            database_connected = True
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}", exc_info=True)
            logger.error("Please ensure SQL Server is running and connection string is correct")
            database_connected = False
            # Continue without database - models are still loaded
            logger.warning("Server will run with limited functionality (no database)")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize components: {e}", exc_info=True)
        models_loaded = False
        database_connected = False
        return False


def decode_base64_image(base64_string: str) -> np.ndarray:
    """
    Decode base64 string to OpenCV image (numpy array).
    
    SECURITY: This function decodes images in-memory only. No images are written to disk.
    Requirements: 10.1, 10.3 - No raw images stored
    
    Args:
        base64_string: Base64 encoded image string
        
    Returns:
        Image as numpy array in BGR format
        
    Raises:
        ValueError: If decoding fails
    """
    try:
        # Remove data URL prefix if present
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        
        # Decode base64 to bytes
        image_bytes = base64.b64decode(base64_string)
        
        # Convert bytes to numpy array
        nparr = np.frombuffer(image_bytes, np.uint8)
        
        # SECURITY: Decode image in-memory only - never write to disk
        # Requirements: 10.1, 10.3
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Failed to decode image")
        
        # Clear sensitive data from memory
        del image_bytes
        del nparr
        
        return image
        
    except Exception as e:
        logger.error(f"Failed to decode base64 image: {e}")
        raise ValueError(f"Failed to decode base64 image: {e}")


def verify_no_image_files():
    """
    SECURITY: Verify that no image files are stored on disk.
    This function checks for common image file extensions in the working directory.
    
    Requirements: 10.1, 10.3 - No raw images stored
    
    Returns:
        bool: True if no image files found, False otherwise
    """
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff']
    current_dir = os.getcwd()
    
    # Check for image files (excluding models directory)
    for root, dirs, files in os.walk(current_dir):
        # Skip models directory and logs directory
        if 'models' in root or 'logs' in root or '.git' in root or '__pycache__' in root:
            continue
            
        for file in files:
            if any(file.lower().endswith(ext) for ext in image_extensions):
                logger.warning(f"SECURITY WARNING: Image file found on disk: {os.path.join(root, file)}")
                return False
    
    return True


@app.route('/health', methods=['GET'])
def health_check():
    """
    Health check endpoint to verify server status.
    
    Returns:
        JSON response with server status, models_loaded, and database_connected
        
    Requirements: 6.1, 6.2
    """
    try:
        response = {
            "status": "ok",
            "models_loaded": models_loaded,
            "database_connected": database_connected,
            "security_verified": verify_no_image_files()  # SECURITY: Verify no images on disk
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.route('/register', methods=['POST'])
def register_face():
    """
    Register face endpoint for storing face embeddings.
    
    Accepts JSON with user_id and base64 image, detects face, extracts embedding,
    and stores in database. Tracks progress toward minimum embeddings requirement.
    
    Request JSON:
        {
            "user_id": int,
            "image": "base64_encoded_image_string"
        }
    
    Response JSON:
        {
            "success": bool,
            "message": str,
            "embeddings_count": int,
            "minimum_required": int,
            "registration_complete": bool
        }
    
    Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.3, 6.4
    """
    try:
        # Check if components are initialized
        if not models_loaded or not database_connected:
            return jsonify({
                "success": False,
                "error_code": "SERVER_NOT_READY",
                "message": "Server components not initialized"
            }), 503
        
        # Parse request JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "error_code": "INVALID_REQUEST",
                "message": "Request body must be JSON"
            }), 400
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({
                "success": False,
                "error_code": "MISSING_USER_ID",
                "message": "user_id is required"
            }), 400
        
        if 'image' not in data:
            return jsonify({
                "success": False,
                "error_code": "MISSING_IMAGE",
                "message": "image is required"
            }), 400
        
        # SECURITY: Validate and sanitize user_id input
        # Requirements: 10.2 - SQL injection prevention
        try:
            user_id = int(data['user_id'])
            if user_id <= 0:
                return jsonify({
                    "success": False,
                    "error_code": "INVALID_USER_ID",
                    "message": "user_id must be a positive integer"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "error_code": "INVALID_USER_ID",
                "message": "user_id must be a valid integer"
            }), 400
        
        base64_image = data['image']
        
        # SECURITY: Validate image data type
        if not isinstance(base64_image, str):
            return jsonify({
                "success": False,
                "error_code": "INVALID_IMAGE",
                "message": "image must be a base64 string"
            }), 400
        
        # Decode base64 image
        try:
            image = decode_base64_image(base64_image)
        except ValueError as e:
            return jsonify({
                "success": False,
                "error_code": "INVALID_IMAGE",
                "message": f"Failed to decode image: {str(e)}"
            }), 400
        
        # Detect faces
        try:
            faces = face_detector.detect_faces(image)
        except ValueError as e:
            logger.error(f"Invalid image for face detection: {e}")
            return jsonify({
                "success": False,
                "error_code": "INVALID_IMAGE_DATA",
                "message": f"Invalid image data: {str(e)}"
            }), 400
        except Exception as e:
            logger.error(f"Face detection failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error_code": "FACE_DETECTION_FAILED",
                "message": f"Face detection failed: {str(e)}"
            }), 500
        
        if len(faces) == 0:
            logger.warning("No face detected in registration image")
            return jsonify({
                "success": False,
                "error_code": "NO_FACE_DETECTED",
                "message": "No face detected in image. Please ensure your face is clearly visible and well-lit."
            }), 400
        
        if len(faces) > 1:
            logger.warning(f"Multiple faces detected ({len(faces)}) in registration image")
            return jsonify({
                "success": False,
                "error_code": "MULTIPLE_FACES_DETECTED",
                "message": f"Multiple faces detected ({len(faces)}). Please ensure only one face is visible in the frame."
            }), 400
        
        # Use the first detected face
        face_box, confidence = faces[0]
        logger.info(f"Face detected with confidence: {confidence:.2f}")
        
        # Preprocess face
        try:
            preprocessed_face = face_preprocessor.preprocess_face(image, face_box)
        except Exception as e:
            logger.error(f"Face preprocessing failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error_code": "PREPROCESSING_FAILED",
                "message": f"Face preprocessing failed: {str(e)}"
            }), 500
        
        # Extract embedding
        try:
            embedding = face_recognizer.extract_embedding(preprocessed_face)
        except ValueError as e:
            logger.error(f"Invalid face image for embedding extraction: {e}")
            return jsonify({
                "success": False,
                "error_code": "INVALID_FACE_IMAGE",
                "message": f"Invalid face image: {str(e)}"
            }), 400
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error_code": "EMBEDDING_EXTRACTION_FAILED",
                "message": f"Embedding extraction failed: {str(e)}"
            }), 500
        
        # Store embedding in database
        try:
            database_manager.store_embedding(user_id, embedding)
        except ValueError as e:
            logger.error(f"Invalid embedding data: {e}")
            return jsonify({
                "success": False,
                "error_code": "INVALID_EMBEDDING",
                "message": f"Invalid embedding data: {str(e)}"
            }), 400
        except Exception as e:
            logger.error(f"Database storage failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "error_code": "DATABASE_ERROR",
                "message": f"Failed to store embedding in database: {str(e)}"
            }), 500
        
        # Get total embeddings count for user
        embeddings_count = database_manager.get_embedding_count_for_user(user_id)
        
        # Get minimum required embeddings from config
        # Requirements: 1.4 - Minimum embeddings per user
        minimum_required = config.get('face_recognition', {}).get('embeddings_per_user', 5)
        registration_complete = embeddings_count >= minimum_required
        
        logger.info(f"Successfully registered face for user {user_id}. "
                   f"Total embeddings: {embeddings_count}/{minimum_required}. "
                   f"Registration complete: {registration_complete}")
        
        return jsonify({
            "success": True,
            "message": f"Face registered successfully. Progress: {embeddings_count}/{minimum_required} images.",
            "embeddings_count": embeddings_count,
            "minimum_required": minimum_required,
            "registration_complete": registration_complete
        }), 200
        
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "error_code": "INTERNAL_ERROR",
            "message": f"Registration failed: {str(e)}"
        }), 500


@app.route('/validate_registration', methods=['POST'])
def validate_registration():
    """
    Validate that a user has completed registration with minimum required embeddings.
    
    Request JSON:
        {
            "user_id": int
        }
    
    Response JSON:
        {
            "valid": bool,
            "embeddings_count": int,
            "minimum_required": int,
            "message": str
        }
    
    Requirements: 1.4 - Minimum embeddings per user
    """
    try:
        # Check if components are initialized
        if not database_connected:
            return jsonify({
                "valid": False,
                "embeddings_count": 0,
                "minimum_required": 5,
                "error_code": "SERVER_NOT_READY",
                "message": "Database not connected"
            }), 503
        
        # Parse request JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                "valid": False,
                "embeddings_count": 0,
                "minimum_required": 5,
                "error_code": "INVALID_REQUEST",
                "message": "Request body must be JSON"
            }), 400
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({
                "valid": False,
                "embeddings_count": 0,
                "minimum_required": 5,
                "error_code": "MISSING_USER_ID",
                "message": "user_id is required"
            }), 400
        
        # SECURITY: Validate and sanitize user_id input
        try:
            user_id = int(data['user_id'])
            if user_id <= 0:
                return jsonify({
                    "valid": False,
                    "embeddings_count": 0,
                    "minimum_required": 5,
                    "error_code": "INVALID_USER_ID",
                    "message": "user_id must be a positive integer"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "valid": False,
                "embeddings_count": 0,
                "minimum_required": 5,
                "error_code": "INVALID_USER_ID",
                "message": "user_id must be a valid integer"
            }), 400
        
        # Get embeddings count
        try:
            embeddings_count = database_manager.get_embedding_count_for_user(user_id)
        except Exception as e:
            logger.error(f"Failed to get embeddings count for user {user_id}: {e}", exc_info=True)
            return jsonify({
                "valid": False,
                "embeddings_count": 0,
                "minimum_required": 5,
                "error_code": "DATABASE_ERROR",
                "message": f"Failed to retrieve embeddings count: {str(e)}"
            }), 500
        
        # Get minimum required from config
        minimum_required = config.get('face_recognition', {}).get('embeddings_per_user', 5)
        
        # Check if user has met minimum requirement
        valid = embeddings_count >= minimum_required
        
        if valid:
            message = f"Registration complete: {embeddings_count} embeddings stored (minimum: {minimum_required})"
        else:
            message = f"Registration incomplete: {embeddings_count}/{minimum_required} embeddings stored"
        
        logger.info(f"Validation check for user {user_id}: {message}")
        
        return jsonify({
            "valid": valid,
            "embeddings_count": embeddings_count,
            "minimum_required": minimum_required,
            "message": message
        }), 200
        
    except Exception as e:
        logger.error(f"Validation failed: {e}", exc_info=True)
        return jsonify({
            "valid": False,
            "embeddings_count": 0,
            "minimum_required": 5,
            "error_code": "INTERNAL_ERROR",
            "message": f"Validation failed: {str(e)}"
        }), 500


@app.route('/authenticate', methods=['POST'])
def authenticate_face():
    """
    Authenticate face endpoint for verifying user identity.
    
    Accepts JSON with user_id and base64 image, detects face, extracts embedding,
    compares against stored embeddings, and returns authentication result.
    
    Request JSON:
        {
            "user_id": int,
            "image": "base64_encoded_image_string"
        }
    
    Response JSON:
        {
            "success": bool,
            "confidence": float (0.0 to 1.0),
            "message": str
        }
    
    Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 6.2, 6.3, 6.4
    """
    try:
        # Check if components are initialized
        if not models_loaded or not database_connected:
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "SERVER_NOT_READY",
                "message": "Server components not initialized"
            }), 503
        
        # Parse request JSON
        data = request.get_json()
        
        if not data:
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INVALID_REQUEST",
                "message": "Request body must be JSON"
            }), 400
        
        # Validate required fields
        if 'user_id' not in data:
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "MISSING_USER_ID",
                "message": "user_id is required"
            }), 400
        
        if 'image' not in data:
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "MISSING_IMAGE",
                "message": "image is required"
            }), 400
        
        # SECURITY: Validate and sanitize user_id input
        # Requirements: 10.2 - SQL injection prevention
        try:
            user_id = int(data['user_id'])
            if user_id <= 0:
                return jsonify({
                    "success": False,
                    "confidence": 0.0,
                    "error_code": "INVALID_USER_ID",
                    "message": "user_id must be a positive integer"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INVALID_USER_ID",
                "message": "user_id must be a valid integer"
            }), 400
        
        base64_image = data['image']
        
        # SECURITY: Validate image data type
        if not isinstance(base64_image, str):
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INVALID_IMAGE",
                "message": "image must be a base64 string"
            }), 400
        
        # Decode base64 image
        try:
            image = decode_base64_image(base64_image)
        except ValueError as e:
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INVALID_IMAGE",
                "message": f"Failed to decode image: {str(e)}"
            }), 400
        
        # Detect faces
        try:
            faces = face_detector.detect_faces(image)
        except ValueError as e:
            logger.error(f"Invalid image for face detection: {e}")
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INVALID_IMAGE_DATA",
                "message": f"Invalid image data: {str(e)}"
            }), 400
        except Exception as e:
            logger.error(f"Face detection failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "FACE_DETECTION_FAILED",
                "message": f"Face detection failed: {str(e)}"
            }), 500
        
        if len(faces) == 0:
            logger.warning(f"No face detected in authentication image for user {user_id}")
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "NO_FACE_DETECTED",
                "message": "No face detected in image. Please ensure your face is clearly visible and well-lit."
            }), 400
        
        if len(faces) > 1:
            logger.warning(f"Multiple faces detected ({len(faces)}) in authentication image for user {user_id}")
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "MULTIPLE_FACES_DETECTED",
                "message": f"Multiple faces detected ({len(faces)}). Please ensure only one face is visible in the frame."
            }), 400
        
        # Use the first detected face
        face_box, confidence = faces[0]
        logger.info(f"Face detected with confidence: {confidence:.2f}")
        
        # Preprocess face
        try:
            preprocessed_face = face_preprocessor.preprocess_face(image, face_box)
        except Exception as e:
            logger.error(f"Face preprocessing failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "PREPROCESSING_FAILED",
                "message": f"Face preprocessing failed: {str(e)}"
            }), 500
        
        # Extract embedding
        try:
            current_embedding = face_recognizer.extract_embedding(preprocessed_face)
        except ValueError as e:
            logger.error(f"Invalid face image for embedding extraction: {e}")
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INVALID_FACE_IMAGE",
                "message": f"Invalid face image: {str(e)}"
            }), 400
        except Exception as e:
            logger.error(f"Embedding extraction failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "EMBEDDING_EXTRACTION_FAILED",
                "message": f"Embedding extraction failed: {str(e)}"
            }), 500
        
        # Retrieve all stored embeddings for user
        try:
            stored_embeddings = database_manager.get_embeddings_for_user(user_id)
        except Exception as e:
            logger.error(f"Failed to retrieve embeddings for user {user_id}: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "DATABASE_ERROR",
                "message": f"Failed to retrieve stored embeddings: {str(e)}"
            }), 500
        
        if len(stored_embeddings) == 0:
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "NO_EMBEDDINGS_FOUND",
                "message": "No face embeddings found for this user. Please register first."
            }), 404
        
        # ENFORCEMENT: Requirements 1.4 - Check minimum embeddings requirement
        minimum_required = config.get('face_recognition', {}).get('embeddings_per_user', 5)
        if len(stored_embeddings) < minimum_required:
            logger.warning(f"User {user_id} has insufficient embeddings: {len(stored_embeddings)}/{minimum_required}")
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INSUFFICIENT_EMBEDDINGS",
                "message": f"Registration incomplete. Only {len(stored_embeddings)} out of {minimum_required} required face images registered. Please complete registration first."
            }), 400
        
        # Compare against all stored embeddings and get maximum similarity
        max_similarity = 0.0
        similarity_scores = []
        
        try:
            for stored_embedding in stored_embeddings:
                similarity = face_recognizer.compare_embeddings(current_embedding, stored_embedding)
                similarity_scores.append(similarity)
                max_similarity = max(max_similarity, similarity)
            
            logger.info(f"Authentication attempt for user {user_id}: "
                       f"Compared against {len(stored_embeddings)} embeddings. "
                       f"Similarity scores: {[f'{s:.3f}' for s in similarity_scores]}, "
                       f"Max: {max_similarity:.3f}")
        except ValueError as e:
            logger.error(f"Invalid embeddings for comparison: {e}")
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "INVALID_EMBEDDING",
                "message": f"Invalid embedding data: {str(e)}"
            }), 500
        except Exception as e:
            logger.error(f"Embedding comparison failed: {e}", exc_info=True)
            return jsonify({
                "success": False,
                "confidence": 0.0,
                "error_code": "COMPARISON_FAILED",
                "message": f"Embedding comparison failed: {str(e)}"
            }), 500
        
        # Get authentication threshold from config
        auth_threshold = config.get('face_recognition', {}).get('authentication_threshold', 0.85)
        
        # Check if max similarity exceeds threshold
        if max_similarity >= auth_threshold:
            logger.info(f"Authentication SUCCESS for user {user_id}: "
                       f"confidence={max_similarity:.2%} (threshold={auth_threshold:.2%})")
            return jsonify({
                "success": True,
                "confidence": float(max_similarity),
                "message": f"Authentication successful. Confidence: {max_similarity:.2%}"
            }), 200
        else:
            logger.info(f"Authentication FAILED for user {user_id}: "
                       f"confidence={max_similarity:.2%} (threshold={auth_threshold:.2%})")
            return jsonify({
                "success": False,
                "confidence": float(max_similarity),
                "message": f"Authentication failed. Confidence too low: {max_similarity:.2%} (threshold: {auth_threshold:.2%})"
            }), 401
        
    except Exception as e:
        logger.error(f"Authentication failed: {e}", exc_info=True)
        return jsonify({
            "success": False,
            "confidence": 0.0,
            "error_code": "INTERNAL_ERROR",
            "message": f"Authentication failed: {str(e)}"
        }), 500


if __name__ == '__main__':
    # Initialize components on startup
    logger.info("="*80)
    logger.info("INITIALIZING OPENCV FACE RECOGNITION SERVER")
    logger.info("="*80)
    logger.info(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"OpenCV version: {cv2.__version__}")
    logger.info(f"Working directory: {os.getcwd()}")
    
    if not initialize_components():
        logger.error("="*80)
        logger.error("FAILED TO INITIALIZE SERVER COMPONENTS")
        logger.error("="*80)
        logger.error("Server startup aborted. Please check the error messages above.")
        sys.exit(1)
    
    logger.info("="*80)
    logger.info("SERVER INITIALIZATION COMPLETE")
    logger.info("="*80)
    logger.info(f"Models loaded: {models_loaded}")
    logger.info(f"Database connected: {database_connected}")
    
    # Get server configuration
    server_config = config.get('server', {})
    host = server_config.get('host', '127.0.0.1')
    port = server_config.get('port', 5000)
    debug = server_config.get('debug', False)
    
    # Start Flask server
    logger.info("="*80)
    logger.info("STARTING FLASK SERVER")
    logger.info("="*80)
    logger.info(f"Host: {host}")
    logger.info(f"Port: {port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Server URL: http://{host}:{port}")
    logger.info("="*80)
    logger.info("Server is ready to accept requests")
    logger.info("="*80)
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("="*80)
        logger.info("Server shutdown requested by user")
        logger.info("="*80)
    except Exception as e:
        logger.error("="*80)
        logger.error(f"Server crashed with error: {e}")
        logger.error("="*80)
        logger.error("Stack trace:", exc_info=True)
        sys.exit(1)
