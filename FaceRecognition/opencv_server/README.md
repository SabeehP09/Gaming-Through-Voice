# OpenCV Face Recognition Server

A Python Flask server providing face detection and recognition capabilities using OpenCV's DNN modules. Delivers iPhone-level accuracy while being completely offline and easy to install without complex C++ compilation requirements.

## Features

- **DNN-based Face Detection**: Uses OpenCV's deep neural network for accurate face detection
- **Face Recognition**: Generates 128-dimensional embeddings using OpenFace model
- **REST API**: Simple HTTP endpoints for registration and authentication
- **Offline Operation**: All processing happens locally, no internet required
- **Easy Installation**: Pure Python with pip-installable dependencies
- **Database Storage**: Stores face embeddings (not raw images) in SQL Server
- **Graceful Degradation**: Continues operation even if face recognition is unavailable
- **Security**: SQL injection prevention, no image persistence, embedding-only storage

## Quick Start

### Prerequisites

- Python 3.8 or higher
- SQL Server 2016 or higher (Express edition works fine)
- Windows 10/11
- Webcam (for face capture)

### Automated Installation (Recommended)

1. **Run the installation script:**
   ```bash
   install_opencv_server.bat
   ```
   This will:
   - Check Python version
   - Create a virtual environment (optional)
   - Install all dependencies
   - Download required models
   - Verify installation

2. **Set up the database:**
   ```bash
   sqlcmd -S localhost -d GamingVoiceRecognition -i setup_database.sql
   ```
   Or run `setup_database.sql` in SQL Server Management Studio (SSMS)

3. **Start the server:**
   ```bash
   start_opencv_server.bat
   ```

That's it! The server will be running on http://127.0.0.1:5000

### Manual Installation

If you prefer manual installation or the automated script fails:

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Download models:**
   ```bash
   python download_models.py
   ```

3. **Verify models:**
   ```bash
   python verify_models.py
   ```

4. **Set up database:**
   ```bash
   sqlcmd -S localhost -d GamingVoiceRecognition -i setup_database.sql
   ```

5. **Start server:**
   ```bash
   python app.py
   ```

## Directory Structure

```
opencv_server/
├── app.py                          # Main Flask application
├── config.json                     # Server configuration
├── requirements.txt                # Python dependencies
├── install_opencv_server.bat       # Automated installation script
├── start_opencv_server.bat         # Server startup script
├── setup_database.sql              # Complete database setup
├── database_schema.sql             # Table creation only
├── database_rollback.sql           # Database cleanup/removal
├── verify_database.sql             # Database verification
├── download_models.py              # Model download script
├── verify_models.py                # Model verification script
├── face_detector.py                # Face detection module
├── face_preprocessor.py            # Face preprocessing module
├── face_recognizer.py              # Face recognition module
├── database_manager.py             # Database operations
├── TROUBLESHOOTING.md              # Troubleshooting guide
├── README.md                       # This file
├── models/                         # Pre-trained models
│   ├── deploy.prototxt
│   ├── res10_300x300_ssd_iter_140000.caffemodel
│   └── openface_nn4.small2.v1.t7
├── logs/                           # Server logs (created at runtime)
│   ├── face_recognition_server.log
│   └── errors.log
└── tests/                          # Test files
    ├── test_face_detection.py
    ├── test_face_recognizer.py
    ├── test_database_manager.py
    └── test_api.py
```

## Configuration

Edit `config.json` to customize server behavior:

```json
{
    "server": {
        "host": "127.0.0.1",      // Server bind address (localhost only for security)
        "port": 5000,              // Server port
        "debug": false             // Debug mode (set to true for development)
    },
    "face_detection": {
        "model_type": "dnn",       // Detection method (dnn recommended)
        "confidence_threshold": 0.7, // Min confidence for detection (0.0-1.0)
        "min_face_size": 80        // Minimum face size in pixels
    },
    "face_recognition": {
        "model_path": "models/openface_nn4.small2.v1.t7",
        "authentication_threshold": 0.85,  // Min similarity for auth (0.85+ recommended)
        "embeddings_per_user": 5   // Number of embeddings to store per user
    },
    "database": {
        "connection_string": "DRIVER={SQL Server};SERVER=localhost;DATABASE=GamingVoiceRecognition;Trusted_Connection=yes;"
    }
}
```

### Configuration Options Explained

**Server Settings:**
- `host`: Always use `127.0.0.1` (localhost) for security. Never expose to external networks.
- `port`: Default is 5000. Change if port is already in use.
- `debug`: Enable for detailed error messages during development. Disable in production.

**Face Detection Settings:**
- `model_type`: Use "dnn" for best accuracy and performance.
- `confidence_threshold`: Higher values (0.8-0.9) reduce false positives but may miss faces. Lower values (0.5-0.7) detect more faces but may have false positives.
- `min_face_size`: Minimum face size in pixels. Increase if detecting too many small/distant faces.

**Face Recognition Settings:**
- `authentication_threshold`: 
  - 0.90+: Very secure, may reject legitimate users
  - 0.85-0.89: Recommended balance of security and convenience
  - 0.80-0.84: More convenient, slightly less secure
  - Below 0.80: Not recommended (security risk)
- `embeddings_per_user`: More embeddings = better accuracy but slower authentication. 5-10 is optimal.

**Database Settings:**
- Update `SERVER` if using a named instance (e.g., `localhost\SQLEXPRESS`)
- For SQL authentication, use: `UID=username;PWD=password;` instead of `Trusted_Connection=yes;`

## API Endpoints

### Health Check
Check if the server is running and models are loaded.

**Request:**
```http
GET /health
```

**Success Response:**
```json
{
    "status": "ok",
    "models_loaded": true,
    "database_connected": true
}
```

**Use Case:** Check server availability before attempting face operations.

---

### Register Face
Register a new face for a user. Captures and stores face embeddings.

**Request:**
```http
POST /register
Content-Type: application/json

{
    "user_id": 123,
    "image": "base64_encoded_image_data"
}
```

**Success Response:**
```json
{
    "success": true,
    "message": "Face registered successfully",
    "embeddings_count": 5
}
```

**Error Responses:**

No face detected:
```json
{
    "success": false,
    "error": "NO_FACE_DETECTED",
    "message": "No face was detected in the image"
}
```

Multiple faces detected:
```json
{
    "success": false,
    "error": "MULTIPLE_FACES",
    "message": "Multiple faces detected. Please ensure only one person is in frame"
}
```

**Notes:**
- Image should be base64-encoded JPEG or PNG
- Only one face should be visible in the image
- Good lighting and clear face visibility improve accuracy
- Typically called 5 times during registration to capture multiple embeddings

---

### Authenticate Face
Authenticate a user by comparing their face against stored embeddings.

**Request:**
```http
POST /authenticate
Content-Type: application/json

{
    "user_id": 123,
    "image": "base64_encoded_image_data"
}
```

**Success Response:**
```json
{
    "success": true,
    "confidence": 0.92,
    "message": "Authentication successful"
}
```

**Failure Response (Low Confidence):**
```json
{
    "success": false,
    "confidence": 0.73,
    "message": "Authentication failed: confidence score below threshold"
}
```

**Error Response (No Embeddings):**
```json
{
    "success": false,
    "error": "NO_EMBEDDINGS",
    "message": "No face embeddings found for this user. Please register first."
}
```

**Notes:**
- Compares against all stored embeddings for the user
- Uses the highest similarity score for authentication decision
- Confidence score indicates how similar the faces are (0.0 to 1.0)
- Threshold is configurable in config.json (default: 0.85)

---

### Example Usage (Python)

```python
import requests
import base64

# Read and encode image
with open("face.jpg", "rb") as f:
    image_data = base64.b64encode(f.read()).decode('utf-8')

# Register face
response = requests.post(
    "http://127.0.0.1:5000/register",
    json={"user_id": 123, "image": image_data}
)
print(response.json())

# Authenticate face
response = requests.post(
    "http://127.0.0.1:5000/authenticate",
    json={"user_id": 123, "image": image_data}
)
print(response.json())
```

### Example Usage (C#)

```csharp
using System;
using System.Net.Http;
using System.Text;
using Newtonsoft.Json;

var client = new HttpClient();
var payload = new {
    user_id = 123,
    image = Convert.ToBase64String(imageBytes)
};

var json = JsonConvert.SerializeObject(payload);
var content = new StringContent(json, Encoding.UTF8, "application/json");

var response = await client.PostAsync(
    "http://127.0.0.1:5000/authenticate",
    content
);

var result = await response.Content.ReadAsStringAsync();
Console.WriteLine(result);
```

## Database Schema

The `FaceEmbeddings` table stores face recognition data:

| Column | Type | Description |
|--------|------|-------------|
| EmbeddingId | INT | Primary key (auto-increment) |
| UserId | INT | Foreign key to Users table |
| EmbeddingVector | NVARCHAR(MAX) | JSON array of 128 floats |
| CreatedDate | DATETIME | Timestamp of creation |
| LastUsedDate | DATETIME | Last time embedding was used for authentication |

**Indexes:**
- `IX_FaceEmbeddings_UserId` - Fast user lookup during authentication
- `IX_FaceEmbeddings_CreatedDate` - Temporal queries and cleanup
- `IX_FaceEmbeddings_LastUsedDate` - Identify stale embeddings

**Foreign Keys:**
- `FK_FaceEmbeddings_Users` - Links to Users table with CASCADE DELETE

**Stored Procedures:**
- `sp_GetUserEmbeddingCount` - Get count of embeddings for a user
- `sp_DeleteOldEmbeddings` - Clean up old/unused embeddings
- `sp_GetFaceRecognitionStats` - Get system-wide statistics

**Views:**
- `vw_UsersWithFaceRecognition` - List users with face recognition enabled

### Database Maintenance

**View statistics:**
```sql
EXEC sp_GetFaceRecognitionStats;
```

**Check user embeddings:**
```sql
EXEC sp_GetUserEmbeddingCount @UserId = 123;
```

**Clean up old embeddings (older than 1 year):**
```sql
EXEC sp_DeleteOldEmbeddings @DaysOld = 365;
```

**View users with face recognition:**
```sql
SELECT * FROM vw_UsersWithFaceRecognition;
```

**Manual cleanup:**
```sql
-- Delete all embeddings for a user
DELETE FROM FaceEmbeddings WHERE UserId = 123;

-- Delete embeddings older than 6 months
DELETE FROM FaceEmbeddings 
WHERE CreatedDate < DATEADD(MONTH, -6, GETDATE());
```

## Security

### Data Protection
- **No Image Storage**: Only numerical embeddings (128-dimensional vectors) are stored, never raw images
- **One-Way Transformation**: Embeddings cannot be reverse-engineered to reconstruct faces
- **Immediate Cleanup**: Images are deleted from memory immediately after processing
- **Database Encryption**: Use SQL Server encryption at rest for additional security

### SQL Injection Prevention
- **Parameterized Queries**: All database operations use parameterized queries exclusively
- **Input Validation**: User IDs and all inputs are validated before processing
- **No String Concatenation**: Never concatenate user input into SQL queries

### Network Security
- **Localhost Only**: Server binds to 127.0.0.1 by default (not accessible from network)
- **No External Exposure**: Never expose port 5000 to external networks
- **CORS Restrictions**: CORS is configured for localhost only

### Authentication Security
- **High Threshold**: Default threshold of 0.85 prevents false positives
- **Multiple Embeddings**: Comparing against multiple embeddings improves security
- **Logging**: All authentication attempts are logged for audit purposes

### Best Practices
1. Keep `authentication_threshold` at 0.85 or higher
2. Never expose the server to external networks
3. Regularly review authentication logs
4. Delete embeddings for inactive users
5. Use SQL Server authentication in production (not Trusted_Connection)
6. Enable database encryption at rest
7. Regularly backup the database

## Troubleshooting

For detailed troubleshooting, see [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Quick Fixes

**Models Not Found:**
```bash
python download_models.py
python verify_models.py
```

**Database Connection Failed:**
- Verify SQL Server is running
- Check connection string in config.json
- Ensure database exists: `GamingVoiceRecognition`
- Run `setup_database.sql` to create tables

**OpenCV Import Error:**
```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python opencv-contrib-python
```

**Port Already in Use:**
```bash
# Find process using port 5000
netstat -ano | findstr :5000

# Kill the process (replace PID with actual process ID)
taskkill /PID [PID] /F

# Or change port in config.json
```

**Python Not Found:**
- Install Python 3.8+ from https://www.python.org/
- Ensure "Add Python to PATH" was checked during installation
- Restart command prompt after installation

**No Face Detected:**
- Ensure good lighting
- Face the camera directly
- Move closer to camera
- Remove glasses/hats if possible
- Check that webcam is working

**Low Confidence Score:**
- Re-register with better quality images
- Ensure consistent lighting between registration and authentication
- Adjust `authentication_threshold` in config.json (carefully!)

## Testing

### Running Tests

**All tests:**
```bash
pytest
```

**Specific test file:**
```bash
pytest test_face_detection.py
pytest test_face_recognizer.py
pytest test_database_manager.py
pytest test_api.py
```

**With verbose output:**
```bash
pytest -v
```

**With coverage:**
```bash
pytest --cov=. --cov-report=html
```

### Manual Testing

**Test face detection:**
```bash
python test_face_detection.py
```

**Test API endpoints:**
```bash
python test_api.py
```

**Test database connection:**
```bash
python verify_database_manager.py
```

## Development

### Project Structure

- `app.py` - Main Flask application and API endpoints
- `face_detector.py` - Face detection using DNN
- `face_preprocessor.py` - Face preprocessing and alignment
- `face_recognizer.py` - Face recognition and embedding extraction
- `database_manager.py` - Database operations
- `config.json` - Configuration file

### Adding New Features

1. **New API Endpoint:**
   - Add route in `app.py`
   - Follow existing error handling patterns
   - Add tests in `test_api.py`

2. **New Face Processing:**
   - Add methods to appropriate module (detector/preprocessor/recognizer)
   - Add unit tests
   - Update documentation

3. **Database Changes:**
   - Update `database_schema.sql`
   - Update `database_manager.py`
   - Create migration script
   - Update tests

### Logging

Logs are written to:
- Console (stdout)
- `logs/face_recognition_server.log` (all logs)
- `logs/errors.log` (errors only)

**Log levels:**
- DEBUG: Detailed information for debugging
- INFO: General information about operations
- WARNING: Warning messages (non-critical issues)
- ERROR: Error messages (operation failures)

**Enable debug logging:**
Set `"debug": true` in config.json

## Performance

### Expected Performance

On modern hardware (Intel i5/i7, 8GB RAM):
- Face detection: < 200ms per image
- Embedding extraction: < 300ms per face
- Authentication (single embedding): < 500ms total
- Authentication (5 embeddings): < 800ms total
- Registration (5 images): < 3 seconds total

### Performance Optimization

**Image Size:**
- Images are automatically resized to 640x480 for processing
- Larger images take longer to process
- Webcam resolution affects capture time

**Model Loading:**
- Models are loaded once at startup and cached in memory
- First request may be slower due to model initialization

**Database:**
- Indexes on UserId ensure fast lookups
- Keep embeddings per user reasonable (5-10)
- Use connection pooling for concurrent requests

**GPU Acceleration (Optional):**
If you have an NVIDIA GPU with CUDA:
```bash
pip uninstall opencv-python
pip install opencv-python-headless
# Install CUDA-enabled OpenCV separately
```

Then update code to use GPU backend:
```python
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
```

### Monitoring Performance

**Enable timing logs:**
Set `"debug": true` in config.json to see detailed timing information.

**Check response times:**
```python
import time
start = time.time()
response = requests.post("http://127.0.0.1:5000/authenticate", json=payload)
print(f"Response time: {time.time() - start:.2f}s")
```

## System Requirements

### Minimum Requirements
- **OS**: Windows 10 or higher
- **Python**: 3.8 or higher
- **RAM**: 4GB
- **Storage**: 500MB for models and dependencies
- **Database**: SQL Server 2016 or higher (Express edition works)
- **Webcam**: 720p resolution

### Recommended Requirements
- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.9 or 3.10
- **RAM**: 8GB or more
- **Storage**: 1GB free space
- **Database**: SQL Server 2019 or higher
- **Webcam**: 1080p resolution
- **Processor**: Intel i5 or equivalent

### Supported Platforms
- ✅ Windows 10/11
- ⚠️ Linux (untested but should work with minor modifications)
- ⚠️ macOS (untested but should work with minor modifications)

## Integration with C# Application

The C# WPF application communicates with this server via HTTP.

### C# Service Class

See `Services/FaceRecognitionService_OpenCV.cs` in the main application.

**Key methods:**
- `RegisterFaceAsync(int userId, string username)` - Register user's face
- `AuthenticateFaceAsync(int userId)` - Authenticate user by face
- `CheckServerHealth()` - Check if server is running

### Workflow

**Registration:**
1. User clicks "Register Face" in C# app
2. C# captures 5 images from webcam
3. Each image is sent to `/register` endpoint
4. Server extracts embeddings and stores in database
5. C# displays success/error message

**Authentication:**
1. User clicks "Face Login" in C# app
2. C# captures single image from webcam
3. Image is sent to `/authenticate` endpoint
4. Server compares against stored embeddings
5. C# receives result and logs user in (or shows error)

**Health Check:**
1. C# app checks `/health` endpoint on startup
2. If server is down, face features are disabled
3. User can still use password authentication

## Frequently Asked Questions

**Q: Can I use this without SQL Server?**
A: Currently, SQL Server is required. You could modify `database_manager.py` to use SQLite or PostgreSQL.

**Q: Does this work offline?**
A: Yes! All processing happens locally. No internet connection required after initial setup.

**Q: How secure is face recognition?**
A: With threshold 0.85+, it's very secure. However, it's not foolproof. Consider using it alongside passwords for critical systems.

**Q: Can someone authenticate with my photo?**
A: Basic photo attacks may work. For production systems, implement liveness detection (not included in this version).

**Q: How many users can this handle?**
A: Tested with hundreds of users. Performance depends on embeddings per user and database performance.

**Q: Can I use this commercially?**
A: Check the licenses of OpenCV and the OpenFace model. This code is part of an educational project.

**Q: Why OpenCV instead of dlib?**
A: OpenCV is easier to install (no C++ compilation), has better Windows support, and provides similar accuracy.

**Q: Can I train my own face recognition model?**
A: Yes, but it requires significant ML expertise and training data. The included OpenFace model works well for most use cases.

**Q: How do I update the models?**
A: Download new models and place them in the `models/` directory. Update paths in `config.json`.

**Q: Can I run multiple instances?**
A: Yes, but use different ports. Update `config.json` for each instance.

## Changelog

### Version 1.0.0 (Current)
- Initial release
- DNN-based face detection
- OpenFace face recognition
- REST API with Flask
- SQL Server database storage
- Automated installation scripts
- Comprehensive documentation

## Contributing

This is part of the Gaming Through Voice Recognition System project.

**To contribute:**
1. Test the system and report bugs
2. Suggest improvements
3. Add new features (with tests)
4. Improve documentation

## Support

**Documentation:**
- README.md (this file)
- TROUBLESHOOTING.md (detailed troubleshooting)
- API_DOCUMENTATION.md (API reference)
- SECURITY_IMPLEMENTATION.md (security details)

**Getting Help:**
1. Check TROUBLESHOOTING.md
2. Review logs in `logs/` directory
3. Run verification scripts
4. Check configuration in config.json

## License

Part of the Gaming Through Voice Recognition System project.

## Acknowledgments

- **OpenCV**: Computer vision library
- **OpenFace**: Face recognition model
- **Flask**: Web framework
- **dlib**: Inspiration for face recognition approach

---

**Last Updated**: December 2024  
**Version**: 1.0.0  
**Status**: Production Ready
