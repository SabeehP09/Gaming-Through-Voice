"""Simple test to debug the API"""
import requests
import json
import base64
import numpy as np
import soundfile as sf
import io

BASE_URL = "http://localhost:5000"
TEST_USER_ID = 9999

def generate_test_audio(duration=3.0, sample_rate=16000):
    """Generate synthetic audio"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = (
        0.3 * np.sin(2 * np.pi * 200 * t) +
        0.2 * np.sin(2 * np.pi * 400 * t) +
        0.1 * np.sin(2 * np.pi * 600 * t) +
        0.05 * np.random.randn(len(t))
    )
    audio = audio / np.max(np.abs(audio)) * 0.8
    return audio.astype(np.float32), sample_rate

def audio_to_base64(audio_data, sample_rate):
    """Convert audio to base64 WAV"""
    buffer = io.BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV', subtype='PCM_16')
    buffer.seek(0)
    wav_bytes = buffer.read()
    return base64.b64encode(wav_bytes).decode('utf-8')

print("1. Generating audio...")
audio_data, sample_rate = generate_test_audio(duration=3.0)
audio_base64 = audio_to_base64(audio_data, sample_rate)
print(f"   Audio size: {len(audio_base64)} bytes")

print("\n2. Enrolling user...")
response = requests.post(f"{BASE_URL}/auth/enroll", json={
    "user_id": TEST_USER_ID,
    "audio_data": audio_base64
})
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json()}")

print("\n3. Verifying user...")
response = requests.post(f"{BASE_URL}/auth/verify", json={
    "user_id": TEST_USER_ID,
    "audio_data": audio_base64
})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   Response: {response.json()}")
else:
    print(f"   Error: {response.text}")

print("\n4. Identifying user...")
response = requests.post(f"{BASE_URL}/auth/identify", json={
    "audio_data": audio_base64
})
print(f"   Status: {response.status_code}")
if response.status_code == 200:
    print(f"   Response: {response.json()}")
else:
    print(f"   Error: {response.text}")

print("\n5. Deleting user...")
response = requests.delete(f"{BASE_URL}/auth/delete/{TEST_USER_ID}")
print(f"   Status: {response.status_code}")
print(f"   Response: {response.json() if response.status_code == 200 else response.text}")
