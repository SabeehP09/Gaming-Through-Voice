"""
Robust Speaker Verification System
Uses multiple discriminative features to distinguish speakers
Designed to work with real microphone recordings
"""

import numpy as np
import librosa
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import euclidean_distances
import pickle
import os
import hashlib

class RobustSpeakerVerification:
    """
    Robust speaker verification that actually works
    Uses multiple voice characteristics to create unique fingerprints
    """
    
    def __init__(self, models_dir='voice_models_robust'):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        # STRICT threshold for normalized features
        # Lower = more strict (fewer false accepts, more false rejects)
        # Higher = more relaxed (more false accepts, fewer false rejects)
        self.DISTANCE_THRESHOLD = 0.35  # Stricter threshold for better accuracy
        
        print("✓ Robust Speaker Verification System initialized")
        print(f"  Models directory: {models_dir}")
        print(f"  Distance threshold: {self.DISTANCE_THRESHOLD} (normalized)")
    
    def extract_voice_fingerprint(self, audio_data, sample_rate=16000):
        """
        Extract comprehensive voice fingerprint
        Returns a unique signature for each speaker
        """
        try:
            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Normalize
            audio_data = audio_data / (np.max(np.abs(audio_data)) + 1e-8)
            
            features = []
            
            # 1. Pitch characteristics (fundamental frequency)
            pitches, magnitudes = librosa.piptrack(
                y=audio_data, sr=sample_rate, 
                fmin=50, fmax=500, threshold=0.1
            )
            
            pitch_values = []
            for t in range(pitches.shape[1]):
                index = magnitudes[:, t].argmax()
                pitch = pitches[index, t]
                if pitch > 0:
                    pitch_values.append(pitch)
            
            if len(pitch_values) > 10:
                features.extend([
                    np.mean(pitch_values),
                    np.std(pitch_values),
                    np.median(pitch_values),
                    np.percentile(pitch_values, 25),
                    np.percentile(pitch_values, 75),
                    np.max(pitch_values) - np.min(pitch_values)
                ])
            else:
                features.extend([0] * 6)
            
            # 2. Formant frequencies (vocal tract shape)
            # Use LPC to estimate formants
            from scipy.signal import lfilter
            
            # Pre-emphasis
            pre_emphasis = 0.97
            emphasized = np.append(audio_data[0], audio_data[1:] - pre_emphasis * audio_data[:-1])
            
            # Frame the signal
            frame_size = int(0.025 * sample_rate)
            frame_stride = int(0.01 * sample_rate)
            
            frames = []
            for i in range(0, len(emphasized) - frame_size, frame_stride):
                frames.append(emphasized[i:i+frame_size])
            
            if len(frames) > 0:
                # Get formants from middle frames
                mid_frame = frames[len(frames)//2]
                
                # Simple formant estimation using spectral peaks
                fft = np.fft.rfft(mid_frame * np.hamming(len(mid_frame)))
                magnitude = np.abs(fft)
                freqs = np.fft.rfftfreq(len(mid_frame), 1/sample_rate)
                
                # Find peaks (formants)
                from scipy.signal import find_peaks
                peaks, _ = find_peaks(magnitude, height=np.max(magnitude)*0.1, distance=20)
                
                formant_freqs = freqs[peaks][:4]  # First 4 formants
                
                while len(formant_freqs) < 4:
                    formant_freqs = np.append(formant_freqs, 0)
                
                features.extend(formant_freqs[:4])
            else:
                features.extend([0] * 4)
            
            # 3. Spectral characteristics
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            spectral_flatness = librosa.feature.spectral_flatness(y=audio_data)[0]
            
            features.extend([
                np.mean(spectral_centroids),
                np.std(spectral_centroids),
                np.mean(spectral_rolloff),
                np.std(spectral_rolloff),
                np.mean(spectral_bandwidth),
                np.std(spectral_bandwidth),
                np.mean(spectral_flatness),
                np.std(spectral_flatness)
            ])
            
            # 4. MFCC (voice timbre)
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=20)
            
            features.extend([
                np.mean(mfccs, axis=1).tolist(),
                np.std(mfccs, axis=1).tolist(),
                np.max(mfccs, axis=1).tolist(),
                np.min(mfccs, axis=1).tolist()
            ])
            
            # Flatten nested lists
            flat_features = []
            for f in features:
                if isinstance(f, (list, np.ndarray)):
                    flat_features.extend(f)
                else:
                    flat_features.append(f)
            
            # Convert to numpy array
            fingerprint = np.array(flat_features, dtype=np.float32)
            
            # Remove any NaN or Inf
            fingerprint = np.nan_to_num(fingerprint, nan=0.0, posinf=0.0, neginf=0.0)
            
            # NORMALIZE the fingerprint (CRITICAL!)
            # This ensures all features are on the same scale
            from sklearn.preprocessing import normalize
            fingerprint = normalize(fingerprint.reshape(1, -1))[0]
            
            print(f"✓ Extracted voice fingerprint: {len(fingerprint)} features (normalized)")
            
            # Create a hash of the audio for additional verification
            audio_hash = hashlib.md5(audio_data.tobytes()).hexdigest()[:16]
            
            return fingerprint, audio_hash
            
        except Exception as e:
            print(f"✗ Fingerprint extraction failed: {str(e)}")
            import traceback
            traceback.print_exc()
            raise
    
    def enroll_speaker(self, user_id, audio_data, sample_rate=16000):
        """Enroll a speaker"""
        try:
            print(f"\n{'='*60}")
            print(f"ENROLLING SPEAKER: User {user_id}")
            print(f"{'='*60}")
            
            duration = len(audio_data) / sample_rate
            print(f"Audio duration: {duration:.2f} seconds")
            
            if duration < 2.0:
                print("✗ Audio too short! Need at least 2 seconds")
                return False
            
            # Extract fingerprint
            fingerprint, audio_hash = self.extract_voice_fingerprint(audio_data, sample_rate)
            
            # Save
            model_path = os.path.join(self.models_dir, f"speaker_{user_id}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'user_id': user_id,
                    'fingerprint': fingerprint,
                    'audio_hash': audio_hash,
                    'sample_rate': sample_rate,
                    'duration': duration
                }, f)
            
            print(f"✓ Speaker {user_id} enrolled successfully")
            print(f"  Fingerprint size: {len(fingerprint)} features")
            print(f"  Audio hash: {audio_hash}")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            print(f"✗ Enrollment failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_speaker(self, user_id, audio_data, sample_rate=16000, threshold=None):
        """Verify if audio matches enrolled speaker"""
        try:
            if threshold is None:
                threshold = self.DISTANCE_THRESHOLD
            
            print(f"\n{'='*60}")
            print(f"VERIFYING SPEAKER: User {user_id}")
            print(f"{'='*60}")
            
            # Load enrolled fingerprint
            model_path = os.path.join(self.models_dir, f"speaker_{user_id}.pkl")
            if not os.path.exists(model_path):
                print(f"✗ No enrollment found for user {user_id}")
                return False, 0.0
            
            with open(model_path, 'rb') as f:
                enrolled_data = pickle.load(f)
            
            enrolled_fingerprint = enrolled_data['fingerprint']
            
            # Extract test fingerprint
            test_fingerprint, test_hash = self.extract_voice_fingerprint(audio_data, sample_rate)
            
            # Calculate Euclidean distance (lower = more similar)
            distance = euclidean_distances(
                enrolled_fingerprint.reshape(1, -1),
                test_fingerprint.reshape(1, -1)
            )[0][0]
            
            # Convert to confidence (0-100%)
            # For normalized features, distance range is typically 0-2
            # Lower distance = higher confidence
            confidence = max(0, min(100, 100 * (1 - distance / 2.0)))
            
            # Verify
            verified = distance <= threshold
            
            print(f"Euclidean distance: {distance:.2f}")
            print(f"Confidence: {confidence:.2f}%")
            print(f"Threshold: {threshold:.2f}")
            print(f"Result: {'✓ VERIFIED' if verified else '✗ REJECTED'}")
            print(f"{'='*60}\n")
            
            return verified, confidence
            
        except Exception as e:
            print(f"✗ Verification failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, 0.0
    
    def identify_speaker(self, audio_data, sample_rate=16000, threshold=None):
        """Identify which enrolled speaker is speaking"""
        try:
            if threshold is None:
                threshold = self.DISTANCE_THRESHOLD
            
            print(f"\n{'='*60}")
            print(f"IDENTIFYING SPEAKER")
            print(f"{'='*60}")
            
            # Extract test fingerprint
            test_fingerprint, test_hash = self.extract_voice_fingerprint(audio_data, sample_rate)
            
            # Compare with all enrolled speakers
            best_match = None
            best_distance = float('inf')
            all_results = []
            
            for model_file in os.listdir(self.models_dir):
                if model_file.endswith('.pkl'):
                    user_id = model_file.replace('speaker_', '').replace('.pkl', '')
                    
                    model_path = os.path.join(self.models_dir, model_file)
                    with open(model_path, 'rb') as f:
                        enrolled_data = pickle.load(f)
                    
                    enrolled_fingerprint = enrolled_data['fingerprint']
                    
                    # Calculate distance
                    distance = euclidean_distances(
                        enrolled_fingerprint.reshape(1, -1),
                        test_fingerprint.reshape(1, -1)
                    )[0][0]
                    
                    confidence = max(0, min(100, 100 * (1 - distance / 2.0)))
                    
                    all_results.append((user_id, distance, confidence))
                    
                    print(f"User {user_id}: distance = {distance:.2f}, confidence = {confidence:.2f}%")
                    
                    if distance < best_distance:
                        best_distance = distance
                        best_match = user_id
            
            # Sort by distance (best match first)
            all_results.sort(key=lambda x: x[1])
            
            print(f"\nRanked results:")
            for i, (uid, dist, conf) in enumerate(all_results[:3], 1):
                print(f"  {i}. User {uid}: distance={dist:.2f}, confidence={conf:.2f}%")
            
            if best_match and best_distance <= threshold:
                confidence = max(0, min(100, 100 * (1 - best_distance / 2.0)))
                print(f"\n✓ IDENTIFIED: User {best_match}")
                print(f"  Distance: {best_distance:.2f}")
                print(f"  Confidence: {confidence:.2f}%")
                print(f"{'='*60}\n")
                return best_match, confidence
            else:
                print(f"\n✗ NO MATCH FOUND")
                print(f"  Best distance: {best_distance:.2f}")
                print(f"  Threshold: {threshold:.2f}")
                print(f"{'='*60}\n")
                return None, 0.0
                
        except Exception as e:
            print(f"✗ Identification failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None, 0.0
    
    def delete_speaker(self, user_id):
        """Delete speaker enrollment"""
        try:
            model_path = os.path.join(self.models_dir, f"speaker_{user_id}.pkl")
            if os.path.exists(model_path):
                os.remove(model_path)
                print(f"✓ Speaker {user_id} deleted")
                return True
            return False
        except Exception as e:
            print(f"✗ Delete failed: {str(e)}")
            return False
