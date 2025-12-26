# OpenCV Face Recognition Server - Quick Setup Guide

This guide will help you set up the OpenCV face recognition server in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- SQL Server with `GamingVoiceRecognition` database
- Internet connection (for initial model download only)

## Step-by-Step Setup

### Step 1: Install Python Dependencies (2 minutes)

Open a terminal in the `FaceRecognition/opencv_server` directory and run:

```bash
pip install -r requirements.txt
```

**What this installs:**
- Flask - Web server framework
- OpenCV - Computer vision library
- NumPy - Numerical computing
- pyodbc - Database connectivity

### Step 2: Download Models (1 minute)

The models are already downloaded! Verify they're present:

```bash
python verify_models.py
```

You should see:
```
✓ OpenCV version: 4.x.x
✓ DNN Face Detector Config (deploy.prototxt)
✓ DNN Face Detector Model (res10_300x300_ssd_iter_140000.caffemodel)
✓ Face Recognition Model (openface_nn4.small2.v1.t7)
✓ DNN face detector loaded successfully
✓ Face recognition model loaded successfully
✓ All checks passed! Models are ready to use.
```

### Step 3: Set Up Database (1 minute)

Run the database schema script to create the `FaceEmbeddings` table:

**Option A: Using SQL Server Management Studio (SSMS)**
1. Open SSMS
2. Connect to your SQL Server
3. Open `database_schema.sql`
4. Execute the script (F5)

**Option B: Using sqlcmd**
```bash
sqlcmd -S localhost -d GamingVoiceRecognition -i database_schema.sql
```

**Verify the database:**
```bash
sqlcmd -S localhost -d GamingVoiceRecognition -i verify_database.sql
```

### Step 4: Configure Server (Optional)

The default configuration should work for most setups. If needed, edit `config.json`:

```json
{
    "server": {
        "host": "127.0.0.1",
        "port": 5000
    },
    "face_detection": {
        "confidence_threshold": 0.7
    },
    "face_recognition": {
        "authentication_threshold": 0.85
    }
}
```

### Step 5: Test the Setup

Once the server is implemented (in later tasks), you'll start it with:

```bash
python server.py
```

And test with:
```bash
curl http://localhost:5000/health
```

## Verification Checklist

- [ ] Python dependencies installed (`pip list | grep opencv`)
- [ ] All 3 model files present in `models/` directory
- [ ] Models can be loaded by OpenCV (`python verify_models.py`)
- [ ] `FaceEmbeddings` table created in database
- [ ] Database has foreign key to `Users` table
- [ ] Indexes created on `UserId` and `CreatedDate`

## Troubleshooting

### "No module named 'cv2'"
```bash
pip install opencv-python opencv-contrib-python
```

### "Models not found"
```bash
python download_models.py
```

### "Database connection failed"
- Verify SQL Server is running
- Check database name: `GamingVoiceRecognition`
- Update connection string in `config.json` if needed

### "Port 5000 already in use"
- Change port in `config.json` to 5001 or another available port
- Update C# application to use the new port

## Next Steps

After completing this setup:
1. Implement the face detection module (Task 2)
2. Implement the face recognition module (Task 3)
3. Implement the Flask REST API (Task 5)
4. Integrate with C# application (Task 8)

## File Structure

```
opencv_server/
├── config.json                 ✓ Configuration
├── requirements.txt            ✓ Dependencies
├── database_schema.sql         ✓ Database setup
├── verify_database.sql         ✓ Database verification
├── download_models.py          ✓ Model downloader
├── verify_models.py            ✓ Model verification
├── models/                     ✓ Pre-trained models
│   ├── deploy.prototxt         ✓ DNN config
│   ├── res10_300x300_ssd_iter_140000.caffemodel  ✓ DNN weights
│   └── openface_nn4.small2.v1.t7  ✓ Face recognition
└── README.md                   ✓ Documentation
```

## Support

If you encounter issues:
1. Check the main README.md for detailed documentation
2. Run verification scripts to identify the problem
3. Review error messages carefully
4. Ensure all prerequisites are met

---

**Setup Status: Infrastructure Complete ✓**

You're ready to proceed with implementing the face detection and recognition modules!
