"""
Script to download required OpenCV models for face detection and recognition.
"""
import os
import urllib.request
import sys

# Model URLs
MODELS = {
    'deploy.prototxt': 'https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt',
    'res10_300x300_ssd_iter_140000.caffemodel': 'https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel',
    'openface_nn4.small2.v1.t7': 'https://storage.cmusatyalab.org/openface-models/nn4.small2.v1.t7'
}

def download_file(url, destination):
    """Download a file from URL to destination."""
    print(f"Downloading {os.path.basename(destination)}...")
    try:
        urllib.request.urlretrieve(url, destination)
        print(f"✓ Successfully downloaded {os.path.basename(destination)}")
        return True
    except Exception as e:
        print(f"✗ Failed to download {os.path.basename(destination)}: {e}")
        return False

def main():
    # Get the models directory path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    models_dir = os.path.join(script_dir, 'models')
    
    # Create models directory if it doesn't exist
    os.makedirs(models_dir, exist_ok=True)
    
    print("=" * 60)
    print("OpenCV Face Recognition Models Downloader")
    print("=" * 60)
    print()
    
    success_count = 0
    total_count = len(MODELS)
    
    for filename, url in MODELS.items():
        destination = os.path.join(models_dir, filename)
        
        # Check if file already exists
        if os.path.exists(destination):
            print(f"✓ {filename} already exists, skipping...")
            success_count += 1
            continue
        
        # Download the file
        if download_file(url, destination):
            success_count += 1
        print()
    
    print("=" * 60)
    print(f"Download Summary: {success_count}/{total_count} models ready")
    print("=" * 60)
    
    if success_count == total_count:
        print("\n✓ All models downloaded successfully!")
        return 0
    else:
        print(f"\n✗ {total_count - success_count} model(s) failed to download.")
        print("Please check your internet connection and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
