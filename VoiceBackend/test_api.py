"""
Test script to verify voice authentication API
"""

import requests
import base64
import numpy as np
import soundfile as sf
import io

API_URL = "http://localhost:5000"

def test_health():
    """Test if server is running"""
    print("\n=== Testing Health Endpoint ===")
    try:
        response = requests.get(f"{API_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def create_test_audio():
    """Create a test audio sample"""
    print("\n=== Creating Test Audio ===")
    # Generate 3 seconds of random audio (simulating voice)
    sample_rate = 16000
    duration = 3
    samples = np.random.randn(sample_rate * duration) * 0.1
    
    # Save to WAV format in memory
    buffer = io.BytesIO()
    sf.write(buffer, samples, sample_rate, format='WAV')
    buffer.seek(0)
    audio_bytes = buffer.read()
    
    print(f"Created audio: {len(audio_bytes)} bytes, {duration}s @ {sample_rate}Hz")
    return audio_bytes

def test_enrollment(user_id, audio_bytes):
    """Test user enrollment"""
    print(f"\n=== Testing Enrollment for User {user_id} ===")
    try:
        # Encode audio to base64
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        # Send enrollment request
        response = requests.post(
            f"{API_URL}/auth/enroll",
            json={
                "user_id": user_id,
                "audio_data": audio_base64
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        return result.get('success', False)
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_verification(user_id, audio_bytes):
    """Test user verification"""
    print(f"\n=== Testing Verification for User {user_id} ===")
    try:
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        response = requests.post(
            f"{API_URL}/auth/verify",
            json={
                "user_id": user_id,
                "audio_data": audio_base64,
                "threshold": -50
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        return result.get('verified', False)
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_identification(audio_bytes):
    """Test user identification"""
    print(f"\n=== Testing Identification ===")
    try:
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        
        response = requests.post(
            f"{API_URL}/auth/identify",
            json={
                "audio_data": audio_base64,
                "threshold": -50
            }
        )
        
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Response: {result}")
        
        return result.get('identified', False)
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_system_info():
    """Test system info endpoint"""
    print("\n=== Testing System Info ===")
    try:
        response = requests.get(f"{API_URL}/system/info")
        print(f"Status: {response.status_code}")
        result = response.json()
        print(f"Enrolled users: {result.get('enrolled_users', 0)}")
        print(f"Total commands: {result.get('total_commands', 0)}")
        print(f"Models directory: {result.get('models_directory', 'N/A')}")
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Voice Authentication API Test Suite")
    print("=" * 60)
    
    # Test 1: Health check
    if not test_health():
        print("\n❌ Server is not running!")
        print("Please start: start_server_no_mic.bat")
        return
    
    print("\n✓ Server is running")
    
    # Test 2: System info
    test_system_info()
    
    # Test 3: Create test audio
    audio_bytes = create_test_audio()
    
    # Test 4: Enroll user
    test_user_id = 999  # Test user ID
    enrolled = test_enrollment(test_user_id, audio_bytes)
    
    if enrolled:
        print(f"\n✓ User {test_user_id} enrolled successfully")
        
        # Test 5: Verify same user
        verified = test_verification(test_user_id, audio_bytes)
        if verified:
            print(f"\n✓ User {test_user_id} verified successfully")
        else:
            print(f"\n❌ Verification failed")
        
        # Test 6: Identify user
        identified = test_identification(audio_bytes)
        if identified:
            print(f"\n✓ User identified successfully")
        else:
            print(f"\n❌ Identification failed")
    else:
        print(f"\n❌ Enrollment failed")
    
    # Test 7: Check system info again
    test_system_info()
    
    print("\n" + "=" * 60)
    print("Test Suite Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()
