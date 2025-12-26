# OpenCV Face Recognition Server - Troubleshooting Guide

This guide helps resolve common installation and runtime issues with the OpenCV Face Recognition Server.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [Model Download Issues](#model-download-issues)
3. [Database Connection Issues](#database-connection-issues)
4. [Server Startup Issues](#server-startup-issues)
5. [Runtime Errors](#runtime-errors)
6. [Performance Issues](#performance-issues)

---

## Installation Issues

### Python Not Found

**Error:** `'python' is not recognized as an internal or external command`

**Solution:**
1. Install Python 3.8 or higher from https://www.python.org/
2. During installation, check "Add Python to PATH"
3. Restart your command prompt after installation
4. Verify: `python --version`

### Python Version Too Old

**Error:** `Python 3.8 or higher is required`

**Solution:**
1. Download the latest Python from https://www.python.org/
2. Install it (you can have multiple Python versions)
3. Use `py -3.8` or `py -3.9` instead of `python` if needed

### pip Install Fails

**Error:** `Failed to install dependencies`

**Solutions:**

**Option 1: Upgrade pip**
```bash
python -m pip install --upgrade pip
```

**Option 2: Install packages individually**
```bash
pip install flask==2.3.0
pip install flask-cors==4.0.0
pip install opencv-python==4.8.0.74
pip install opencv-contrib-python==4.8.0.74
pip install numpy==1.24.3
pip install pyodbc==4.0.39
```

**Option 3: Use a different package index**
```bash
pip install -r requirements.txt --index-url https://pypi.org/simple
```

**Option 4: Install without version constraints**
```bash
pip install flask flask-cors opencv-python opencv-contrib-python numpy pyodbc
```

### Virtual Environment Creation Fails

**Error:** `Failed to create virtual environment`

**Solution:**
1. Install venv module: `python -m pip install virtualenv`
2. Or skip virtual environment and install globally
3. Or use conda: `conda create -n opencv_server python=3.9`

### OpenCV Import Error

**Error:** `ImportError: DLL load failed while importing cv2`

**Solutions:**

**Option 1: Install Visual C++ Redistributable**
- Download from: https://aka.ms/vs/17/release/vc_redist.x64.exe
- Install and restart

**Option 2: Reinstall OpenCV**
```bash
pip uninstall opencv-python opencv-contrib-python
pip install opencv-python opencv-contrib-python
```

**Option 3: Use opencv-python-headless**
```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

---

## Model Download Issues

### Models Fail to Download

**Error:** `Failed to download [model_name]`

**Solutions:**

**Option 1: Check internet connection**
- Ensure you have a stable internet connection
- Try disabling VPN or proxy temporarily

**Option 2: Download manually**

Download these files and place them in the `models/` directory:

1. **deploy.prototxt**
   - URL: https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt

2. **res10_300x300_ssd_iter_140000.caffemodel**
   - URL: https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel

3. **openface_nn4.small2.v1.t7**
   - URL: https://storage.cmusatyalab.org/openface-models/nn4.small2.v1.t7

**Option 3: Use alternative download method**
```bash
cd models
curl -O https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt
```

### Models Directory Not Found

**Error:** `models directory not found`

**Solution:**
```bash
mkdir models
cd models
# Download models manually as described above
```

---

## Database Connection Issues

### SQL Server Not Found

**Error:** `[Microsoft][ODBC Driver Manager] Data source name not found`

**Solutions:**

**Option 1: Install SQL Server**
- Download SQL Server Express from Microsoft
- Or use SQL Server LocalDB

**Option 2: Update connection string in config.json**
```json
{
    "database": {
        "connection_string": "DRIVER={SQL Server};SERVER=.\\SQLEXPRESS;DATABASE=GamingVoiceRecognition;Trusted_Connection=yes;"
    }
}
```

**Option 3: Use SQL Server authentication**
```json
{
    "database": {
        "connection_string": "DRIVER={SQL Server};SERVER=localhost;DATABASE=GamingVoiceRecognition;UID=your_username;PWD=your_password;"
    }
}
```

### Database Does Not Exist

**Error:** `Cannot open database "GamingVoiceRecognition"`

**Solution:**
1. Open SQL Server Management Studio (SSMS)
2. Create the database:
   ```sql
   CREATE DATABASE GamingVoiceRecognition;
   ```
3. Run the setup script: `setup_database.sql`

### ODBC Driver Not Found

**Error:** `[Microsoft][ODBC Driver Manager] Driver not found`

**Solution:**
1. Download ODBC Driver for SQL Server:
   - https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
2. Install the driver
3. Update connection string to match installed driver:
   ```
   DRIVER={ODBC Driver 17 for SQL Server};...
   ```

### FaceEmbeddings Table Missing

**Error:** `Invalid object name 'FaceEmbeddings'`

**Solution:**
1. Run the database setup script:
   ```bash
   sqlcmd -S localhost -d GamingVoiceRecognition -i setup_database.sql
   ```
2. Or execute the SQL manually in SSMS

---

## Server Startup Issues

### Port Already in Use

**Error:** `Address already in use` or `Port 5000 is already in use`

**Solutions:**

**Option 1: Kill the process using port 5000**
```bash
netstat -ano | findstr :5000
taskkill /PID [process_id] /F
```

**Option 2: Change the port in config.json**
```json
{
    "server": {
        "port": 5001
    }
}
```

### Flask Not Found

**Error:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
1. Activate virtual environment if you created one:
   ```bash
   venv\Scripts\activate.bat
   ```
2. Or reinstall Flask:
   ```bash
   pip install flask
   ```

### Config File Not Found

**Error:** `config.json not found`

**Solution:**
1. Ensure you're running the server from the `opencv_server` directory
2. Or create a default config.json (see config.json.example)

---

## Runtime Errors

### No Face Detected

**Error:** `No face detected in image`

**Causes & Solutions:**

1. **Poor lighting**
   - Ensure good lighting on your face
   - Avoid backlighting

2. **Face too small**
   - Move closer to the camera
   - Adjust `min_face_size` in config.json

3. **Face partially obscured**
   - Remove glasses, hats, or masks
   - Ensure full face is visible

4. **Camera angle**
   - Face the camera directly
   - Avoid extreme angles

### Multiple Faces Detected

**Error:** `Multiple faces detected`

**Solution:**
- Ensure only one person is in frame during registration/authentication
- Remove photos or posters with faces from background

### Low Confidence Score

**Issue:** Authentication fails with low confidence

**Solutions:**

1. **Re-register with better images**
   - Good lighting
   - Clear face visibility
   - Multiple angles

2. **Adjust threshold in config.json**
   ```json
   {
       "face_recognition": {
           "authentication_threshold": 0.80
       }
   }
   ```
   Note: Lower threshold = less secure but more convenient

3. **Register more embeddings**
   - Increase `embeddings_per_user` in config.json
   - Re-register to capture more face samples

### Model Loading Error

**Error:** `Failed to load model`

**Solutions:**

1. **Verify model files exist**
   ```bash
   dir models
   ```

2. **Re-download models**
   ```bash
   python download_models.py
   ```

3. **Check file permissions**
   - Ensure models directory is readable

---

## Performance Issues

### Slow Face Detection

**Issue:** Detection takes more than 500ms

**Solutions:**

1. **Reduce image size**
   - Images are automatically resized to 640x480
   - Ensure webcam isn't capturing at 4K

2. **Use GPU acceleration** (if available)
   - Install CUDA-enabled OpenCV
   - Update code to use GPU backend

3. **Adjust confidence threshold**
   ```json
   {
       "face_detection": {
           "confidence_threshold": 0.8
       }
   }
   ```
   Higher threshold = faster but may miss faces

### High Memory Usage

**Issue:** Server uses too much memory

**Solutions:**

1. **Limit concurrent requests**
   - Add request queuing
   - Process one request at a time

2. **Clear image data after processing**
   - Already implemented in current code
   - Verify no memory leaks

3. **Restart server periodically**
   - Set up automatic restart schedule

### Database Query Slow

**Issue:** Authentication takes too long

**Solutions:**

1. **Verify index exists**
   ```sql
   SELECT * FROM sys.indexes WHERE name = 'IX_FaceEmbeddings_UserId';
   ```

2. **Limit embeddings per user**
   - Keep to 5-10 embeddings maximum
   - Delete old embeddings periodically

3. **Optimize connection pooling**
   - Use connection pooling in pyodbc

---

## Getting More Help

If you're still experiencing issues:

1. **Check the logs**
   - Server logs are in `logs/face_recognition_server.log`
   - Error logs are in `logs/errors.log`

2. **Enable debug mode**
   - Set `"debug": true` in config.json
   - Restart server and check detailed output

3. **Test individual components**
   - Run `test_face_detection.py`
   - Run `test_face_recognizer.py`
   - Run `test_database_manager.py`

4. **Verify system requirements**
   - Python 3.8+
   - Windows 10/11
   - SQL Server 2016+
   - 4GB RAM minimum
   - Webcam with 720p resolution

5. **Contact support**
   - Include error messages
   - Include relevant log files
   - Describe steps to reproduce

---

## Common Error Codes

| Error Code | Meaning | Solution |
|------------|---------|----------|
| NO_FACE_DETECTED | No face found in image | Improve lighting, face camera |
| MULTIPLE_FACES | More than one face detected | Ensure only one person in frame |
| MODEL_LOAD_ERROR | Failed to load ML model | Re-download models |
| DATABASE_ERROR | Database connection failed | Check SQL Server, connection string |
| INVALID_IMAGE | Image data is corrupted | Check webcam, retry capture |
| LOW_CONFIDENCE | Similarity score too low | Re-register or adjust threshold |
| NO_EMBEDDINGS | User has no stored embeddings | Complete registration first |

---

## Prevention Tips

1. **Regular maintenance**
   - Keep Python packages updated
   - Backup database regularly
   - Monitor log files

2. **Good registration practices**
   - Register in good lighting
   - Capture multiple angles
   - Re-register if appearance changes significantly

3. **Security considerations**
   - Keep authentication threshold at 0.85 or higher
   - Monitor failed authentication attempts
   - Regularly review stored embeddings

4. **Performance optimization**
   - Keep embeddings count reasonable (5-10 per user)
   - Clean up old/unused embeddings
   - Monitor server resource usage
