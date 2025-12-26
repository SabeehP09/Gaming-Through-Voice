# OpenCV Face Recognition Models

This directory contains the pre-trained models required for face detection and recognition.

## Models

### 1. deploy.prototxt
- **Purpose**: Configuration file for DNN-based face detection
- **Source**: OpenCV repository
- **Description**: Defines the network architecture for the Caffe face detector

### 2. res10_300x300_ssd_iter_140000.caffemodel
- **Purpose**: Pre-trained weights for DNN face detection
- **Source**: OpenCV 3rd party models
- **Description**: SSD (Single Shot Detector) model trained for face detection
- **Input Size**: 300x300 pixels
- **Confidence Threshold**: 0.7 (configurable in config.json)

### 3. openface_nn4.small2.v1.t7
- **Purpose**: Face recognition and embedding extraction
- **Source**: OpenFace project (CMU)
- **Description**: Neural network that generates 128-dimensional face embeddings
- **Input Size**: 96x96 pixels (aligned face)
- **Output**: 128-dimensional feature vector

## Setup

Models are automatically downloaded when you run:
```bash
python download_models.py
```

## Verification

To verify that all models are present and can be loaded:
```bash
python verify_models.py
```

## Manual Download

If automatic download fails, you can manually download the models:

1. **deploy.prototxt**
   - URL: https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt

2. **res10_300x300_ssd_iter_140000.caffemodel**
   - URL: https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel

3. **openface_nn4.small2.v1.t7**
   - URL: https://storage.cmusatyalab.org/openface-models/nn4.small2.v1.t7

Place all downloaded files in this directory.
