import os
import zipfile
import urllib.request

model_url = "https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip"
model_zip = "vosk-model-small-en-us-0.15.zip"
model_dir = "vosk-model-small-en-us-0.15"

if not os.path.exists(model_dir):
    print("Downloading Vosk model...")
    urllib.request.urlretrieve(model_url, model_zip)
    print("Extracting model...")
    with zipfile.ZipFile(model_zip, 'r') as zip_ref:
        zip_ref.extractall(".")
    os.remove(model_zip)
    print("Model downloaded and extracted successfully!")
else:
    print("Model already exists!")
