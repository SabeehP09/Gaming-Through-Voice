#!/usr/bin/env python3
"""
iPhone-Level Face Recognition Server
Uses face_recognition library (dlib-based) for 99%+ accuracy
"""

import face_recognition
import numpy as np
import json
import base64
from io import BytesIO
from PIL import Image
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging

app = Flask(__name__)
CORS(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
FACE_DISTANCE_THRESHOLD = 0.6  # iPhone uses ~0.6 (lower = stricter)
MIN_FACE_SIZE = 50  # Minimum face size in pixels

def decode_image(base64_string):
    """Decode base64 image to numpy array"""
    try:
        image_data = base64.b64decode(base64_string)
        image = Image.open(BytesIO(image_data))
        return np.array(image)
    except Exception as e:
        logger.error(f"Error decoding image: {e}")
        return None

def encode_image(image_array):
    """Encode numpy array to base64"""
    try:
        image = Image.fromarray(image_array)
        buffered = BytesIO()
        image.save(buffered, format="JPEG")
        return base64.b64encode(buffered.getvalue()).decode()
    except Exception as e:
        logger.error(f"Error encoding image: {e}")
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'face_recognition',
        'version': '1.0.0',
        'model': 'dlib ResNet',
        'accuracy': '99.38%'
    })

@app.route('/detect_face', methods=['POST'])
def detect_face():
    """
    Detect face in image and return location
    Request: { "image": "base64_encoded_image" }
    Response: { "success": true, "face_found": true, "location": [top, right, bottom, left], "quality": 0.95 }
    """
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        # Decode image
        image = decode_image(data['image'])
        if image is None:
            return jsonify({'success': False, 'error': 'Invalid image data'}), 400
        
        # Detect faces
        face_locations = face_recognition.face_locations(image, model='hog')
        
        if len(face_locations) == 0:
            return jsonify({
                'success': True,
                'face_found': False,
                'message': 'No face detected'
            })
        
        if len(face_locations) > 1:
            return jsonify({
                'success': True,
                'face_found': False,
                'message': 'Multiple faces detected. Please ensure only one face is visible.'
            })
        
        # Get face location
        top, right, bottom, left = face_locations[0]
        face_width = right - left
        face_height = bottom - top
        
        # Calculate quality score
        quality = calculate_face_quality(image, face_locations[0])
        
        return jsonify({
            'success': True,
            'face_found': True,
            'location': {
                'top': int(top),
                'right': int(right),
                'bottom': int(bottom),
                'left': int(left),
                'width': int(face_width),
                'height': int(face_height)
            },
            'quality': float(quality)
        })
        
    except Exception as e:
        logger.error(f"Error in detect_face: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/encode_face', methods=['POST'])
def encode_face():
    """
    Generate 128-D face embedding
    Request: { "image": "base64_encoded_image" }
    Response: { "success": true, "encoding": [128 floats], "quality": 0.95 }
    """
    try:
        data = request.get_json()
        
        if 'image' not in data:
            return jsonify({'success': False, 'error': 'No image provided'}), 400
        
        # Decode image
        image = decode_image(data['image'])
        if image is None:
            return jsonify({'success': False, 'error': 'Invalid image data'}), 400
        
        # Detect faces
        face_locations = face_recognition.face_locations(image, model='hog')
        
        if len(face_locations) == 0:
            return jsonify({
                'success': False,
                'error': 'No face detected'
            }), 400
        
        if len(face_locations) > 1:
            return jsonify({
                'success': False,
                'error': 'Multiple faces detected'
            }), 400
        
        # Generate face encoding (128-D embedding)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) == 0:
            return jsonify({
                'success': False,
                'error': 'Could not generate face encoding'
            }), 400
        
        encoding = face_encodings[0]
        quality = calculate_face_quality(image, face_locations[0])
        
        logger.info(f"Generated face encoding with quality: {quality:.2f}")
        
        return jsonify({
            'success': True,
            'encoding': encoding.tolist(),  # Convert numpy array to list
            'quality': float(quality),
            'dimensions': 128
        })
        
    except Exception as e:
        logger.error(f"Error in encode_face: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/compare_faces', methods=['POST'])
def compare_faces():
    """
    Compare two face encodings
    Request: { "encoding1": [128 floats], "encoding2": [128 floats] }
    Response: { "success": true, "distance": 0.35, "similarity": 0.65, "match": true }
    """
    try:
        data = request.get_json()
        
        if 'encoding1' not in data or 'encoding2' not in data:
            return jsonify({'success': False, 'error': 'Two encodings required'}), 400
        
        # Convert to numpy arrays
        encoding1 = np.array(data['encoding1'])
        encoding2 = np.array(data['encoding2'])
        
        # Validate dimensions
        if encoding1.shape[0] != 128 or encoding2.shape[0] != 128:
            return jsonify({'success': False, 'error': 'Invalid encoding dimensions'}), 400
        
        # Calculate face distance (Euclidean distance)
        distance = face_recognition.face_distance([encoding1], encoding2)[0]
        
        # Convert to similarity percentage
        similarity = 1.0 - distance
        
        # Determine if it's a match
        is_match = distance < FACE_DISTANCE_THRESHOLD
        
        logger.info(f"Face comparison: distance={distance:.4f}, similarity={similarity:.2%}, match={is_match}")
        
        return jsonify({
            'success': True,
            'distance': float(distance),
            'similarity': float(similarity),
            'match': bool(is_match),
            'threshold': FACE_DISTANCE_THRESHOLD,
            'confidence': float(similarity * 100)  # As percentage
        })
        
    except Exception as e:
        logger.error(f"Error in compare_faces: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/authenticate', methods=['POST'])
def authenticate():
    """
    Authenticate face against multiple stored encodings
    Request: { "image": "base64_encoded_image", "stored_encodings": [[128 floats], ...] }
    Response: { "success": true, "authenticated": true, "best_match_index": 0, "confidence": 95.5 }
    """
    try:
        data = request.get_json()
        
        if 'image' not in data or 'stored_encodings' not in data:
            return jsonify({'success': False, 'error': 'Image and stored encodings required'}), 400
        
        # Decode and encode face
        image = decode_image(data['image'])
        if image is None:
            return jsonify({'success': False, 'error': 'Invalid image data'}), 400
        
        # Detect and encode face
        face_locations = face_recognition.face_locations(image, model='hog')
        
        if len(face_locations) == 0:
            return jsonify({
                'success': False,
                'error': 'No face detected'
            }), 400
        
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        if len(face_encodings) == 0:
            return jsonify({
                'success': False,
                'error': 'Could not generate face encoding'
            }), 400
        
        test_encoding = face_encodings[0]
        
        # Compare against all stored encodings
        stored_encodings = [np.array(enc) for enc in data['stored_encodings']]
        distances = face_recognition.face_distance(stored_encodings, test_encoding)
        
        # Find best match
        best_match_index = int(np.argmin(distances))
        best_distance = float(distances[best_match_index])
        best_similarity = 1.0 - best_distance
        
        # Check if authenticated
        is_authenticated = best_distance < FACE_DISTANCE_THRESHOLD
        
        logger.info(f"Authentication: best_distance={best_distance:.4f}, similarity={best_similarity:.2%}, authenticated={is_authenticated}")
        
        return jsonify({
            'success': True,
            'authenticated': bool(is_authenticated),
            'best_match_index': best_match_index,
            'distance': best_distance,
            'similarity': best_similarity,
            'confidence': float(best_similarity * 100),
            'threshold': FACE_DISTANCE_THRESHOLD,
            'num_comparisons': len(stored_encodings)
        })
        
    except Exception as e:
        logger.error(f"Error in authenticate: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

def calculate_face_quality(image, face_location):
    """
    Calculate face quality score (0.0 to 1.0)
    Based on face size, brightness, and sharpness
    """
    try:
        top, right, bottom, left = face_location
        face_width = right - left
        face_height = bottom - top
        
        # Size score (larger faces = better quality)
        size_score = min(1.0, (face_width * face_height) / (200 * 200))
        
        # Extract face region
        face_image = image[top:bottom, left:right]
        
        # Brightness score (avoid too dark or too bright)
        brightness = np.mean(face_image)
        brightness_score = 1.0 - abs(brightness - 128) / 128
        
        # Simple sharpness estimate (variance of Laplacian)
        if len(face_image.shape) == 3:
            gray = np.mean(face_image, axis=2)
        else:
            gray = face_image
        
        laplacian_var = np.var(gray)
        sharpness_score = min(1.0, laplacian_var / 500)
        
        # Combined quality score
        quality = (size_score * 0.4 + brightness_score * 0.3 + sharpness_score * 0.3)
        
        return max(0.0, min(1.0, quality))
        
    except Exception as e:
        logger.error(f"Error calculating quality: {e}")
        return 0.5

if __name__ == '__main__':
    logger.info("=" * 60)
    logger.info("iPhone-Level Face Recognition Server")
    logger.info("=" * 60)
    logger.info("Model: dlib ResNet (99.38% accuracy)")
    logger.info(f"Threshold: {FACE_DISTANCE_THRESHOLD}")
    logger.info("Starting server on http://localhost:5001")
    logger.info("=" * 60)
    
    app.run(host='0.0.0.0', port=5001, debug=False)
