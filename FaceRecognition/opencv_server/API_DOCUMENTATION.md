# Flask REST API Documentation

## Overview

This Flask REST API provides face recognition services for user registration and authentication. It uses OpenCV DNN models for face detection and recognition.

## Base URL

```
http://127.0.0.1:5000
```

## Endpoints

### 1. Health Check

Check if the server is running and components are initialized.

**Endpoint:** `GET /health`

**Response:**
```json
{
    "status": "ok",
    "models_loaded": true,
    "database_connected": true
}
```

**Status Codes:**
- `200 OK`: Server is healthy
- `500 Internal Server Error`: Server error

---

### 2. Register Face

Register a user's face by storing face embeddings in the database.

**Endpoint:** `POST /register`

**Request Body:**
```json
{
    "user_id": 123,
    "image": "base64_encoded_image_string"
}
```

**Parameters:**
- `user_id` (integer, required): The ID of the user to register
- `image` (string, required): Base64-encoded image (JPEG, PNG, etc.)

**Success Response:**
```json
{
    "success": true,
    "message": "Face registered successfully",
    "embeddings_count": 5
}
```

**Error Responses:**

*No face detected:*
```json
{
    "success": false,
    "error_code": "NO_FACE_DETECTED",
    "message": "No face detected in image. Please ensure your face is clearly visible."
}
```

*Invalid image:*
```json
{
    "success": false,
    "error_code": "INVALID_IMAGE",
    "message": "Failed to decode image: ..."
}
```

*Missing fields:*
```json
{
    "success": false,
    "error_code": "MISSING_USER_ID",
    "message": "user_id is required"
}
```

**Status Codes:**
- `200 OK`: Registration successful
- `400 Bad Request`: Invalid request (missing fields, invalid image, no face detected)
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Server components not initialized

---

### 3. Authenticate Face

Authenticate a user by comparing their face against stored embeddings.

**Endpoint:** `POST /authenticate`

**Request Body:**
```json
{
    "user_id": 123,
    "image": "base64_encoded_image_string"
}
```

**Parameters:**
- `user_id` (integer, required): The ID of the user to authenticate
- `image` (string, required): Base64-encoded image (JPEG, PNG, etc.)

**Success Response:**
```json
{
    "success": true,
    "confidence": 0.92,
    "message": "Authentication successful. Confidence: 92.00%"
}
```

**Failure Response (Low Confidence):**
```json
{
    "success": false,
    "confidence": 0.65,
    "message": "Authentication failed. Confidence too low: 65.00% (threshold: 85.00%)"
}
```

**Error Responses:**

*No face detected:*
```json
{
    "success": false,
    "confidence": 0.0,
    "error_code": "NO_FACE_DETECTED",
    "message": "No face detected in image. Please ensure your face is clearly visible."
}
```

*No embeddings found:*
```json
{
    "success": false,
    "confidence": 0.0,
    "error_code": "NO_EMBEDDINGS_FOUND",
    "message": "No face embeddings found for this user. Please register first."
}
```

**Status Codes:**
- `200 OK`: Authentication successful
- `401 Unauthorized`: Authentication failed (confidence below threshold)
- `400 Bad Request`: Invalid request (missing fields, invalid image, no face detected)
- `404 Not Found`: No embeddings found for user
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Server components not initialized

---

## Error Codes

| Error Code | Description |
|------------|-------------|
| `SERVER_NOT_READY` | Server components not initialized |
| `INVALID_REQUEST` | Request body is not valid JSON |
| `MISSING_USER_ID` | user_id field is missing |
| `MISSING_IMAGE` | image field is missing |
| `INVALID_IMAGE` | Failed to decode base64 image |
| `NO_FACE_DETECTED` | No face detected in the image |
| `NO_EMBEDDINGS_FOUND` | No face embeddings stored for user |
| `INTERNAL_ERROR` | Internal server error |

---

## Image Format

Images should be base64-encoded. The API accepts common image formats (JPEG, PNG, BMP, etc.).

**Example (Python):**
```python
import base64
import cv2

# Read image
image = cv2.imread('face.jpg')

# Encode to JPEG
_, buffer = cv2.imencode('.jpg', image)

# Convert to base64
base64_string = base64.b64encode(buffer).decode('utf-8')
```

**Example (C#):**
```csharp
using System;
using System.Drawing;
using System.IO;

// Load image
Bitmap image = new Bitmap("face.jpg");

// Convert to base64
using (MemoryStream ms = new MemoryStream())
{
    image.Save(ms, System.Drawing.Imaging.ImageFormat.Jpeg);
    byte[] imageBytes = ms.ToArray();
    string base64String = Convert.ToBase64String(imageBytes);
}
```

---

## Configuration

The server reads configuration from `config.json`:

```json
{
    "server": {
        "host": "127.0.0.1",
        "port": 5000,
        "debug": false
    },
    "face_detection": {
        "model_type": "dnn",
        "confidence_threshold": 0.7,
        "min_face_size": 80
    },
    "face_recognition": {
        "model_path": "models/openface_nn4.small2.v1.t7",
        "authentication_threshold": 0.85,
        "embeddings_per_user": 5
    },
    "database": {
        "connection_string": "DRIVER={SQL Server};SERVER=localhost;DATABASE=GamingVoiceRecognition;Trusted_Connection=yes;"
    }
}
```

---

## Starting the Server

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure models are downloaded:
```bash
python download_models.py
```

3. Start the server:
```bash
python app.py
```

The server will start on `http://127.0.0.1:5000`

---

## CORS

The API has CORS enabled for localhost origins:
- `http://localhost:*`
- `http://127.0.0.1:*`

This allows the C# WPF application to make requests from localhost.

---

## Logging

The server logs all requests, face detection results, authentication attempts, and errors.

Log format:
```
2024-01-15 10:30:00 - app - INFO - Face detected with confidence: 0.95
2024-01-15 10:30:01 - app - INFO - Successfully registered face for user 123. Total embeddings: 5
```

---

## Testing

Run the verification script to check API structure:
```bash
python verify_api.py
```

Run the API test (requires database connection):
```bash
python test_api.py
```

---

## Requirements Validation

This API implementation satisfies the following requirements:

- **Requirement 6.1**: REST API endpoint for face registration at POST /register ✓
- **Requirement 6.2**: REST API endpoint for face authentication at POST /authenticate ✓
- **Requirement 6.3**: Accepts base64-encoded image data in JSON format ✓
- **Requirement 6.4**: Returns JSON responses with success status and similarity scores ✓
- **Requirement 1.1**: Captures face images for registration ✓
- **Requirement 1.2**: Detects faces and extracts descriptors ✓
- **Requirement 1.3**: Stores descriptors in database ✓
- **Requirement 1.5**: Displays error if no face detected ✓
- **Requirement 2.1-2.6**: Complete authentication workflow ✓

---

## Security Considerations

1. **Localhost Only**: Server binds to 127.0.0.1 by default
2. **SQL Injection Prevention**: Uses parameterized queries
3. **No Image Storage**: Only embeddings are stored, not raw images
4. **Input Validation**: All inputs are validated before processing
5. **Error Handling**: Comprehensive error handling with descriptive messages

---

## Performance

Typical response times:
- Health check: < 10ms
- Face registration: 200-500ms per image
- Face authentication: 300-800ms (depending on number of stored embeddings)

---

## Troubleshooting

**Server won't start:**
- Check if port 5000 is already in use
- Verify all dependencies are installed
- Check if models are downloaded

**"Models not loaded":**
- Run `python download_models.py`
- Verify models exist in `models/` directory

**"Database not connected":**
- Check SQL Server is running
- Verify connection string in config.json
- Ensure FaceEmbeddings table exists

**"No face detected":**
- Ensure face is clearly visible
- Check lighting conditions
- Face should be at least 80x80 pixels
- Try adjusting confidence_threshold in config

---

## Support

For issues or questions, refer to:
- `README.md` - General setup guide
- `SETUP_GUIDE.md` - Detailed setup instructions
- `IMPLEMENTATION_STATUS.md` - Current implementation status
