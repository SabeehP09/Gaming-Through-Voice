"""
Comprehensive Voice System Test Script
Tests all API endpoints and voice authentication functionality
"""

import requests
import json
import base64
import numpy as np
import soundfile as sf
import io
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:5000"
TEST_USER_ID = 9999  # Use high ID to avoid conflicts

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_test(name):
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}TEST: {name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")

def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")

def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")

def print_info(message):
    print(f"{Colors.YELLOW}ℹ️  {message}{Colors.END}")

def generate_test_audio(duration=3.0, sample_rate=16000):
    """Generate synthetic audio for testing"""
    # Generate a simple sine wave with some variation
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Mix multiple frequencies to simulate voice
    audio = (
        0.3 * np.sin(2 * np.pi * 200 * t) +  # Base frequency
        0.2 * np.sin(2 * np.pi * 400 * t) +  # Harmonic
        0.1 * np.sin(2 * np.pi * 600 * t) +  # Harmonic
        0.05 * np.random.randn(len(t))       # Noise
    )
    
    # Normalize
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    return audio.astype(np.float32), sample_rate

def audio_to_base64(audio_data, sample_rate):
    """Convert audio numpy array to base64 WAV"""
    buffer = io.BytesIO()
    sf.write(buffer, audio_data, sample_rate, format='WAV', subtype='PCM_16')
    buffer.seek(0)
    wav_bytes = buffer.read()
    return base64.b64encode(wav_bytes).decode('utf-8')

def test_health_check():
    """Test 1: Health Check"""
    print_test("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Server is healthy")
            print_info(f"Status: {data.get('status')}")
            print_info(f"Services: {json.dumps(data.get('services'), indent=2)}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check error: {str(e)}")
        return False

def test_system_info():
    """Test 2: System Info"""
    print_test("System Info")
    
    try:
        response = requests.get(f"{BASE_URL}/system/info", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("System info retrieved")
            print_info(f"Version: {data.get('version')}")
            print_info(f"Microphone: {data.get('microphone_available')}")
            print_info(f"Enrolled Users: {data.get('enrolled_users')}")
            return True
        else:
            print_error(f"System info failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"System info error: {str(e)}")
        return False

def test_voice_enrollment():
    """Test 3: Voice Enrollment"""
    print_test("Voice Enrollment")
    
    try:
        # Generate test audio
        print_info("Generating test audio (3 seconds)...")
        audio_data, sample_rate = generate_test_audio(duration=3.0)
        audio_base64 = audio_to_base64(audio_data, sample_rate)
        
        print_info(f"Audio size: {len(audio_base64)} bytes (base64)")
        
        # Enroll user
        payload = {
            "user_id": TEST_USER_ID,
            "audio_data": audio_base64
        }
        
        print_info(f"Enrolling user {TEST_USER_ID}...")
        response = requests.post(f"{BASE_URL}/auth/enroll", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success(f"User {TEST_USER_ID} enrolled successfully")
                print_info(f"Message: {data.get('message')}")
                return True, audio_data, sample_rate
            else:
                print_error(f"Enrollment failed: {data.get('message')}")
                return False, None, None
        else:
            print_error(f"Enrollment request failed: {response.status_code}")
            print_error(f"Response: {response.text}")
            return False, None, None
    except Exception as e:
        print_error(f"Enrollment error: {str(e)}")
        return False, None, None

def test_voice_verification(original_audio, sample_rate):
    """Test 4: Voice Verification"""
    print_test("Voice Verification")
    
    try:
        # Use same audio for verification
        print_info("Using same audio for verification...")
        audio_base64 = audio_to_base64(original_audio, sample_rate)
        
        payload = {
            "user_id": TEST_USER_ID,
            "audio_data": audio_base64
        }
        
        print_info(f"Verifying user {TEST_USER_ID}...")
        response = requests.post(f"{BASE_URL}/auth/verify", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            verified = data.get('verified', False)
            confidence = data.get('confidence', 0)
            
            if verified:
                print_success(f"User verified! Confidence: {confidence:.2f}%")
                return True
            else:
                print_error(f"Verification failed. Confidence: {confidence:.2f}%")
                return False
        else:
            print_error(f"Verification request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Verification error: {str(e)}")
        return False

def test_voice_identification(original_audio, sample_rate):
    """Test 5: Voice Identification"""
    print_test("Voice Identification")
    
    try:
        # Use same audio for identification
        print_info("Using same audio for identification...")
        audio_base64 = audio_to_base64(original_audio, sample_rate)
        
        payload = {
            "audio_data": audio_base64
        }
        
        print_info("Identifying user from voice...")
        response = requests.post(f"{BASE_URL}/auth/identify", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                identified_user = data.get('user_id')
                confidence = data.get('confidence', 0)
                
                # Convert to string for comparison (API returns string)
                if str(identified_user) == str(TEST_USER_ID):
                    print_success(f"User correctly identified as {identified_user}")
                    print_info(f"Confidence: {confidence:.2f}%")
                    return True
                else:
                    print_error(f"Wrong user identified: {identified_user} (expected {TEST_USER_ID})")
                    return False
            else:
                print_error(f"Identification failed: {data.get('message')}")
                return False
        else:
            print_error(f"Identification request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Identification error: {str(e)}")
        return False

def test_different_audio_verification():
    """Test 6: Different Audio (Should Fail or Low Confidence)"""
    print_test("Different Audio Verification (Negative Test)")
    
    try:
        # Generate different audio with completely different characteristics
        print_info("Generating different audio...")
        t = np.linspace(0, 2.0, int(16000 * 2.0))
        # Use very different frequencies and patterns
        audio_data = (
            0.4 * np.sin(2 * np.pi * 150 * t) +
            0.3 * np.sin(2 * np.pi * 350 * t) +
            0.2 * np.random.randn(len(t))
        )
        audio_data = audio_data / np.max(np.abs(audio_data)) * 0.7
        audio_data = audio_data.astype(np.float32)
        sample_rate = 16000
        audio_base64 = audio_to_base64(audio_data, sample_rate)
        
        payload = {
            "user_id": TEST_USER_ID,
            "audio_data": audio_base64
        }
        
        print_info(f"Verifying with different audio...")
        response = requests.post(f"{BASE_URL}/auth/verify", json=payload, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            verified = data.get('verified', False)
            confidence = data.get('confidence', 0)
            
            print_info(f"Verified: {verified}, Confidence: {confidence:.2f}%")
            
            if not verified or confidence < 70:
                print_success("System correctly rejected different audio")
                return True
            else:
                print_error(f"System incorrectly accepted different audio (confidence: {confidence:.2f}%)")
                return False
        else:
            print_error(f"Verification request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Different audio test error: {str(e)}")
        return False

def test_commands_list():
    """Test 7: List Commands"""
    print_test("List Commands")
    
    try:
        response = requests.get(f"{BASE_URL}/commands/list", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            commands = data.get('commands', [])
            print_success(f"Retrieved {len(commands)} commands")
            if isinstance(commands, list) and len(commands) > 0:
                # Show first 5 commands
                for i, cmd in enumerate(commands[:5]):
                    print_info(f"  {i+1}. {cmd}")
            return True
        else:
            print_error(f"List commands failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"List commands error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_cleanup():
    """Test 8: Cleanup - Delete Test User"""
    print_test("Cleanup - Delete Test User")
    
    try:
        print_info(f"Deleting user {TEST_USER_ID}...")
        response = requests.delete(f"{BASE_URL}/auth/delete/{TEST_USER_ID}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print_success(f"User {TEST_USER_ID} deleted successfully")
                return True
            else:
                print_error(f"Delete failed: {data.get('message')}")
                return False
        else:
            print_error(f"Delete request failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Cleanup error: {str(e)}")
        return False

def run_all_tests():
    """Run all tests"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}🎤 VOICE AUTHENTICATION SYSTEM TEST SUITE{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.YELLOW}Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.END}")
    print(f"{Colors.YELLOW}Server: {BASE_URL}{Colors.END}")
    
    results = []
    
    # Test 1: Health Check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: System Info
    results.append(("System Info", test_system_info()))
    
    # Test 3: Voice Enrollment
    enrollment_result, audio_data, sample_rate = test_voice_enrollment()
    results.append(("Voice Enrollment", enrollment_result))
    
    if enrollment_result and audio_data is not None:
        # Test 4: Voice Verification
        results.append(("Voice Verification", test_voice_verification(audio_data, sample_rate)))
        
        # Test 5: Voice Identification
        results.append(("Voice Identification", test_voice_identification(audio_data, sample_rate)))
        
        # Test 6: Different Audio
        results.append(("Different Audio Test", test_different_audio_verification()))
    else:
        print_error("Skipping verification tests due to enrollment failure")
    
    # Test 7: List Commands
    results.append(("List Commands", test_commands_list()))
    
    # Test 8: Cleanup
    results.append(("Cleanup", test_cleanup()))
    
    # Summary
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}📊 TEST SUMMARY{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}✅ PASSED{Colors.END}" if result else f"{Colors.RED}❌ FAILED{Colors.END}"
        print(f"{test_name:.<40} {status}")
    
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    percentage = (passed / total * 100) if total > 0 else 0
    
    if passed == total:
        print(f"{Colors.GREEN}🎉 ALL TESTS PASSED! ({passed}/{total}) - {percentage:.1f}%{Colors.END}")
    else:
        print(f"{Colors.YELLOW}⚠️  SOME TESTS FAILED: {passed}/{total} passed - {percentage:.1f}%{Colors.END}")
    
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        exit(1)
    except Exception as e:
        print(f"\n{Colors.RED}Fatal error: {str(e)}{Colors.END}")
        exit(1)
