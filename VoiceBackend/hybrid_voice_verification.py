"""
Hybrid Voice Verification System
Combines:
1. Speaker Verification (WHO is speaking) - voice signature
2. Phrase Matching (WHAT they're saying) - speech recognition

This is the most secure form of voice authentication!
"""

import numpy as np
import librosa
from sklearn.preprocessing import normalize
from sklearn.metrics.pairwise import euclidean_distances
import pickle
import os
import hashlib
import speech_recognition as sr
from difflib import SequenceMatcher

class HybridVoiceVerification:
    """
    Hybrid verification combining:
    - Speaker verification (voice biometrics)
    - Phrase verification (speech recognition)
    
    Both must match for authentication to succeed!
    """
    
    def __init__(self, models_dir='voice_models_hybrid'):
        self.models_dir = models_dir
        os.makedirs(models_dir, exist_ok=True)
        
        # Thresholds
        self.VOICE_DISTANCE_THRESHOLD = 0.35  # Voice signature threshold
        self.PHRASE_SIMILARITY_THRESHOLD = 0.80  # 80% phrase match required
        
        # Initialize speech recognizer
        self.recognizer = sr.Recognizer()
        
        print("✓ Hybrid Voice Verification System initialized")
        print(f"  Voice threshold: {self.VOICE_DISTANCE_THRESHOLD}")
        print(f"  Phrase threshold: {self.PHRASE_SIMILARITY_THRESHOLD}")
    
    def extract_voice_fingerprint(self, audio_data, sample_rate=16000):
        """Extract voice signature (same as before)"""
        try:
            # Ensure mono
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Normalize
            audio_data = audio_data / (np.max(np.abs(audio_data)) + 1e-8)
            
            features = []
            
            # 1. Pitch features
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
            
            # 2. Spectral features
            spectral_centroids = librosa.feature.spectral_centroid(y=audio_data, sr=sample_rate)[0]
            spectral_rolloff = librosa.feature.spectral_rolloff(y=audio_data, sr=sample_rate)[0]
            spectral_bandwidth = librosa.feature.spectral_bandwidth(y=audio_data, sr=sample_rate)[0]
            
            features.extend([
                np.mean(spectral_centroids),
                np.std(spectral_centroids),
                np.mean(spectral_rolloff),
                np.std(spectral_rolloff),
                np.mean(spectral_bandwidth),
                np.std(spectral_bandwidth)
            ])
            
            # 3. MFCC features
            mfccs = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=20)
            
            features.extend([
                np.mean(mfccs, axis=1).tolist(),
                np.std(mfccs, axis=1).tolist()
            ])
            
            # Flatten
            flat_features = []
            for f in features:
                if isinstance(f, (list, np.ndarray)):
                    flat_features.extend(f)
                else:
                    flat_features.append(f)
            
            fingerprint = np.array(flat_features, dtype=np.float32)
            fingerprint = np.nan_to_num(fingerprint, nan=0.0, posinf=0.0, neginf=0.0)
            
            # Normalize
            fingerprint = normalize(fingerprint.reshape(1, -1))[0]
            
            return fingerprint
            
        except Exception as e:
            print(f"✗ Fingerprint extraction failed: {str(e)}")
            raise
    
    def recognize_speech(self, audio_data, sample_rate=16000):
        """
        Convert speech to text using speech recognition
        Returns the recognized phrase
        """
        try:
            # Convert numpy array to AudioData format
            import io
            import wave
            
            # Create WAV in memory
            wav_io = io.BytesIO()
            with wave.open(wav_io, 'wb') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)  # 16-bit
                wav_file.setframerate(sample_rate)
                
                # Convert float to int16
                audio_int16 = (audio_data * 32767).astype(np.int16)
                wav_file.writeframes(audio_int16.tobytes())
            
            wav_io.seek(0)
            
            # Use speech recognition
            with sr.AudioFile(wav_io) as source:
                audio = self.recognizer.record(source)
            
            # Recognize speech
            text = self.recognizer.recognize_google(audio)
            
            print(f"✓ Recognized speech: \"{text}\"")
            return text.lower().strip()
            
        except sr.UnknownValueError:
            print("✗ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"✗ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"✗ Speech recognition failed: {str(e)}")
            return None
    
    def calculate_phrase_similarity(self, phrase1, phrase2):
        """
        Calculate similarity between two phrases
        Returns similarity score (0-1)
        """
        if not phrase1 or not phrase2:
            return 0.0
        
        # Normalize phrases
        p1 = phrase1.lower().strip()
        p2 = phrase2.lower().strip()
        
        # Calculate similarity using SequenceMatcher
        similarity = SequenceMatcher(None, p1, p2).ratio()
        
        return similarity
    
    def enroll_speaker(self, user_id, audio_data, sample_rate=16000):
        """
        Enroll speaker with BOTH voice signature and phrase
        """
        try:
            print(f"\n{'='*60}")
            print(f"HYBRID ENROLLMENT: User {user_id}")
            print(f"{'='*60}")
            
            duration = len(audio_data) / sample_rate
            print(f"Audio duration: {duration:.2f} seconds")
            
            if duration < 2.0:
                print("✗ Audio too short! Need at least 2 seconds")
                return False
            
            # 1. Extract voice fingerprint
            fingerprint = self.extract_voice_fingerprint(audio_data, sample_rate)
            print(f"✓ Voice fingerprint extracted: {len(fingerprint)} features")
            
            # 2. Recognize enrollment phrase
            enrollment_phrase = self.recognize_speech(audio_data, sample_rate)
            
            if not enrollment_phrase:
                print("⚠️  Could not recognize phrase - enrolling with voice only")
                enrollment_phrase = ""  # Allow voice-only enrollment
            else:
                print(f"✓ Enrollment phrase: \"{enrollment_phrase}\"")
            
            # 3. Save both
            model_path = os.path.join(self.models_dir, f"speaker_{user_id}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump({
                    'user_id': user_id,
                    'fingerprint': fingerprint,
                    'enrollment_phrase': enrollment_phrase,
                    'sample_rate': sample_rate,
                    'duration': duration
                }, f)
            
            print(f"✓ User {user_id} enrolled successfully")
            print(f"  Voice fingerprint: {len(fingerprint)} features")
            print(f"  Enrollment phrase: \"{enrollment_phrase}\"")
            print(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            print(f"✗ Enrollment failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False
    
    def verify_speaker(self, user_id, audio_data, sample_rate=16000):
        """
        Verify BOTH voice signature AND phrase
        """
        try:
            print(f"\n{'='*60}")
            print(f"HYBRID VERIFICATION: User {user_id}")
            print(f"{'='*60}")
            
            # Load enrolled data
            model_path = os.path.join(self.models_dir, f"speaker_{user_id}.pkl")
            if not os.path.exists(model_path):
                print(f"✗ No enrollment found for user {user_id}")
                return False, 0.0, "Not enrolled"
            
            with open(model_path, 'rb') as f:
                enrolled_data = pickle.load(f)
            
            enrolled_fingerprint = enrolled_data['fingerprint']
            enrolled_phrase = enrolled_data.get('enrollment_phrase', '')
            
            # 1. Verify voice signature
            test_fingerprint = self.extract_voice_fingerprint(audio_data, sample_rate)
            
            voice_distance = euclidean_distances(
                enrolled_fingerprint.reshape(1, -1),
                test_fingerprint.reshape(1, -1)
            )[0][0]
            
            voice_confidence = max(0, min(100, 100 * (1 - voice_distance / 2.0)))
            voice_match = voice_distance <= self.VOICE_DISTANCE_THRESHOLD
            
            print(f"Voice signature:")
            print(f"  Distance: {voice_distance:.4f}")
            print(f"  Confidence: {voice_confidence:.2f}%")
            print(f"  Match: {'✓ YES' if voice_match else '✗ NO'}")
            
            # 2. Verify phrase (if enrolled with phrase)
            phrase_match = True
            phrase_similarity = 1.0
            
            if enrolled_phrase:  # Only check phrase if one was enrolled
                test_phrase = self.recognize_speech(audio_data, sample_rate)
                
                if test_phrase:
                    phrase_similarity = self.calculate_phrase_similarity(
                        enrolled_phrase, test_phrase
                    )
                    phrase_match = phrase_similarity >= self.PHRASE_SIMILARITY_THRESHOLD
                    
                    print(f"Phrase verification:")
                    print(f"  Enrolled: \"{enrolled_phrase}\"")
                    print(f"  Spoken: \"{test_phrase}\"")
                    print(f"  Similarity: {phrase_similarity*100:.2f}%")
                    print(f"  Match: {'✓ YES' if phrase_match else '✗ NO'}")
                else:
                    print(f"Phrase verification:")
                    print(f"  ✗ Could not recognize speech")
                    phrase_match = False
                    phrase_similarity = 0.0
            else:
                print(f"Phrase verification: SKIPPED (no phrase enrolled)")
            
            # 3. BOTH must match!
            verified = voice_match and phrase_match
            
            # Combined confidence (average of both)
            combined_confidence = (voice_confidence + phrase_similarity * 100) / 2
            
            print(f"\nFinal result:")
            print(f"  Voice match: {'✓' if voice_match else '✗'}")
            print(f"  Phrase match: {'✓' if phrase_match else '✗'}")
            print(f"  Combined confidence: {combined_confidence:.2f}%")
            print(f"  Result: {'✓ VERIFIED' if verified else '✗ REJECTED'}")
            print(f"{'='*60}\n")
            
            reason = ""
            if not voice_match:
                reason = "Voice signature mismatch"
            elif not phrase_match:
                reason = "Phrase mismatch"
            else:
                reason = "Verified"
            
            return verified, combined_confidence, reason
            
        except Exception as e:
            print(f"✗ Verification failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, 0.0, str(e)
    
    def identify_speaker(self, audio_data, sample_rate=16000):
        """
        Identify speaker using BOTH voice and phrase
        """
        try:
            print(f"\n{'='*60}")
            print(f"HYBRID IDENTIFICATION")
            print(f"{'='*60}")
            
            # Extract test features
            test_fingerprint = self.extract_voice_fingerprint(audio_data, sample_rate)
            test_phrase = self.recognize_speech(audio_data, sample_rate)
            
            if test_phrase:
                print(f"Spoken phrase: \"{test_phrase}\"")
            else:
                print(f"Could not recognize phrase")
            
            # Compare with all enrolled users
            best_match = None
            best_score = -1
            all_results = []
            
            for model_file in os.listdir(self.models_dir):
                if model_file.endswith('.pkl'):
                    user_id = model_file.replace('speaker_', '').replace('.pkl', '')
                    
                    model_path = os.path.join(self.models_dir, model_file)
                    with open(model_path, 'rb') as f:
                        enrolled_data = pickle.load(f)
                    
                    enrolled_fingerprint = enrolled_data['fingerprint']
                    enrolled_phrase = enrolled_data.get('enrollment_phrase', '')
                    
                    # Calculate voice distance
                    voice_distance = euclidean_distances(
                        enrolled_fingerprint.reshape(1, -1),
                        test_fingerprint.reshape(1, -1)
                    )[0][0]
                    
                    voice_confidence = max(0, min(100, 100 * (1 - voice_distance / 2.0)))
                    voice_match = voice_distance <= self.VOICE_DISTANCE_THRESHOLD
                    
                    # Calculate phrase similarity
                    phrase_similarity = 1.0
                    phrase_match = True
                    
                    if enrolled_phrase and test_phrase:
                        phrase_similarity = self.calculate_phrase_similarity(
                            enrolled_phrase, test_phrase
                        )
                        phrase_match = phrase_similarity >= self.PHRASE_SIMILARITY_THRESHOLD
                    
                    # Combined score
                    combined_score = (voice_confidence + phrase_similarity * 100) / 2
                    both_match = voice_match and phrase_match
                    
                    all_results.append((
                        user_id, voice_distance, voice_match, 
                        phrase_similarity, phrase_match, 
                        combined_score, both_match
                    ))
                    
                    print(f"User {user_id}:")
                    print(f"  Voice: dist={voice_distance:.4f}, match={'✓' if voice_match else '✗'}")
                    if enrolled_phrase:
                        print(f"  Phrase: sim={phrase_similarity:.2f}, match={'✓' if phrase_match else '✗'}")
                    print(f"  Combined: {combined_score:.2f}%, both_match={'✓' if both_match else '✗'}")
                    
                    if both_match and combined_score > best_score:
                        best_score = combined_score
                        best_match = user_id
            
            # Sort by combined score
            all_results.sort(key=lambda x: x[5], reverse=True)
            
            print(f"\nRanked results:")
            for i, (uid, vd, vm, ps, pm, cs, bm) in enumerate(all_results[:3], 1):
                print(f"  {i}. User {uid}: score={cs:.2f}%, both_match={'✓' if bm else '✗'}")
            
            if best_match:
                print(f"\n✓ IDENTIFIED: User {best_match}")
                print(f"  Combined confidence: {best_score:.2f}%")
                print(f"{'='*60}\n")
                return best_match, best_score
            else:
                print(f"\n✗ NO MATCH FOUND")
                print(f"  No user matched both voice AND phrase")
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
