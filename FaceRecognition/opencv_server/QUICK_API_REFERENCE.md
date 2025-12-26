# Quick API Reference

## Start Server
```bash
cd FaceRecognition/opencv_server
python app.py
```

Server runs on: `http://127.0.0.1:5000`

## Endpoints

### Health Check
```bash
curl http://127.0.0.1:5000/health
```

### Register Face
```bash
curl -X POST http://127.0.0.1:5000/register \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "image": "BASE64_IMAGE_HERE"}'
```

### Authenticate Face
```bash
curl -X POST http://127.0.0.1:5000/authenticate \
  -H "Content-Type: application/json" \
  -d '{"user_id": 123, "image": "BASE64_IMAGE_HERE"}'
```

## Python Client Example

```python
import requests
import base64
import cv2

# Read and encode image
image = cv2.imread('face.jpg')
_, buffer = cv2.imencode('.jpg', image)
base64_image = base64.b64encode(buffer).decode('utf-8')

# Register
response = requests.post('http://127.0.0.1:5000/register', json={
    'user_id': 123,
    'image': base64_image
})
print(response.json())

# Authenticate
response = requests.post('http://127.0.0.1:5000/authenticate', json={
    'user_id': 123,
    'image': base64_image
})
print(response.json())
```

## C# Client Example

```csharp
using System;
using System.Net.Http;
using System.Text;
using System.Drawing;
using System.IO;
using Newtonsoft.Json;

// Convert image to base64
Bitmap image = new Bitmap("face.jpg");
using (MemoryStream ms = new MemoryStream())
{
    image.Save(ms, System.Drawing.Imaging.ImageFormat.Jpeg);
    string base64Image = Convert.ToBase64String(ms.ToArray());
    
    // Register
    var client = new HttpClient();
    var payload = new { user_id = 123, image = base64Image };
    var json = JsonConvert.SerializeObject(payload);
    var content = new StringContent(json, Encoding.UTF8, "application/json");
    
    var response = await client.PostAsync("http://127.0.0.1:5000/register", content);
    var result = await response.Content.ReadAsStringAsync();
    Console.WriteLine(result);
}
```

## Response Examples

### Success
```json
{
    "success": true,
    "message": "Face registered successfully",
    "embeddings_count": 5
}
```

### Authentication Success
```json
{
    "success": true,
    "confidence": 0.92,
    "message": "Authentication successful. Confidence: 92.00%"
}
```

### Error
```json
{
    "success": false,
    "error_code": "NO_FACE_DETECTED",
    "message": "No face detected in image. Please ensure your face is clearly visible."
}
```

## Common Error Codes

- `NO_FACE_DETECTED` - No face found in image
- `NO_EMBEDDINGS_FOUND` - User not registered
- `MISSING_USER_ID` - user_id field missing
- `MISSING_IMAGE` - image field missing
- `INVALID_IMAGE` - Cannot decode base64 image
- `SERVER_NOT_READY` - Components not initialized

## Configuration

Edit `config.json`:
```json
{
    "face_recognition": {
        "authentication_threshold": 0.85
    }
}
```

Lower threshold = easier to authenticate (less secure)
Higher threshold = harder to authenticate (more secure)

## Troubleshooting

**Port already in use:**
```bash
# Change port in config.json
"server": { "port": 5001 }
```

**Models not found:**
```bash
python download_models.py
```

**Database connection failed:**
- Check SQL Server is running
- Verify connection string in config.json

## Testing

```bash
# Verify API structure
python verify_api.py

# Test endpoints (requires database)
python test_api.py
```

## Files

- `app.py` - Main Flask application
- `config.json` - Configuration
- `API_DOCUMENTATION.md` - Full documentation
- `TASK_5_COMPLETE.md` - Implementation summary
