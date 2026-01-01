"""
Voice Authentication System
Similar to Siri's voice recognition for iPhone unlock
Uses MFCC (Mel-Frequency Cepstral Coefficients) and GMM (Gaussian Mixture Models)
"""

import numpy as np
import pickle
import os
from python_speech_features import mfcc
from sklearn.mixture import GaussianMixture
import soundfile as sf
import librosa


class VoiceAuthenticator:
    """
    Voice-based user authentication system
    Enrolls users and verifies their identity through voice
    """
    
    def __init__(self, models_dir="voice_models"):
        """
        Initialize the voice authenticator
        
        Args:
            models_dir: Directory to store voice models
        """
        self.models_dir = models_dir
        if not os.path.exists(models_dir):
            os.makedirs(models_dir)
        
        # GMM parameters
        self.n_components = 16  # Number of Gaussian components
        self.n_mfcc = 13  # Number of MFCC coefficients
        
    def extract_features(self, audio_data, sample_rate=16000):
        """
        Extract MFCC features from audio data
        
        Args:
            audio_data: Audio samples as numpy array
            sample_rate: Sample rate of audio
            
        Returns:
            MFCC features as numpy array
        """
        # Extract MFCC features
        features = mfcc(audio_data, 
                       samplerate=sample_rate,
                       numcep=self.n_mfcc,
                       nfilt=26,
                       nfft=512,
                       appendEnergy=True)
        
        # Normalize features
        features = (features - np.mean(features, axis=0)) / (np.std(features, axis=0) + 1e-8)
        
        return features
    
    def enroll_user(self, user_id, audio_file_path=None, audio_data=None, sample_rate=16000):
        """
        Enroll a new user by training a GMM model on their voice
        
        Args:
            user_id: Unique identifier for the user
            audio_file_path: Path to audio file (WAV format)
            audio_data: Raw audio data as numpy array
            sample_rate: Sample rate of audio
            
        Returns:
            True if enrollment successful, False otherwise
        """
        try:
            # Load audio
            if audio_file_path:
                audio_data, sample_rate = sf.read(audio_file_path)
            elif audio_data is None:
                raise ValueError("Either audio_file_path or audio_data must be provided")
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Extract features
            features = self.extract_features(audio_data, sample_rate)
            
            # Train GMM model
            gmm = GaussianMixture(n_components=self.n_components,
                                 covariance_type='diag',
                                 max_iter=200,
                                 random_state=42)
            gmm.fit(features)
            
            # Save model
            model_path = os.path.join(self.models_dir, f"user_{user_id}.pkl")
            with open(model_path, 'wb') as f:
                pickle.dump(gmm, f)
            
            print(f"✓ User {user_id} enrolled successfully")
            return True
            
        except Exception as e:
            print(f"✗ Enrollment failed: {str(e)}")
            return False
    
    def verify_user(self, user_id, audio_file_path=None, audio_data=None, 
                   sample_rate=16000, threshold=-50):
        """
        Verify if the voice matches the enrolled user
        
        Args:
            user_id: User ID to verify against
            audio_file_path: Path to audio file
            audio_data: Raw audio data
            sample_rate: Sample rate
            threshold: Log-likelihood threshold for verification
            
        Returns:
            (is_verified, confidence_score)
        """
        try:
            # Load user's model
            model_path = os.path.join(self.models_dir, f"user_{user_id}.pkl")
            if not os.path.exists(model_path):
                print(f"✗ No model found for user {user_id}")
                return False, 0.0
            
            with open(model_path, 'rb') as f:
                gmm = pickle.load(f)
            
            # Load audio
            if audio_file_path:
                audio_data, sample_rate = sf.read(audio_file_path)
            elif audio_data is None:
                raise ValueError("Either audio_file_path or audio_data must be provided")
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Extract features
            features = self.extract_features(audio_data, sample_rate)
            
            # Calculate log-likelihood
            log_likelihood = gmm.score(features)
            
            # Normalize score to 0-100 range
            confidence = min(100, max(0, (log_likelihood - threshold) * 2 + 50))
            
            is_verified = bool(log_likelihood > threshold)
            
            print(f"{'✓' if is_verified else '✗'} Verification: {confidence:.1f}% confidence")
            return is_verified, float(confidence)
            
        except Exception as e:
            print(f"✗ Verification failed: {str(e)}")
            return False, 0.0
    
    def identify_user(self, audio_file_path=None, audio_data=None, 
                     sample_rate=16000, threshold=-50):
        """
        Identify which enrolled user is speaking
        
        Args:
            audio_file_path: Path to audio file
            audio_data: Raw audio data
            sample_rate: Sample rate
            threshold: Minimum threshold for identification
            
        Returns:
            (user_id, confidence) or (None, 0.0) if no match
        """
        try:
            # Load audio
            if audio_file_path:
                audio_data, sample_rate = sf.read(audio_file_path)
            elif audio_data is None:
                raise ValueError("Either audio_file_path or audio_data must be provided")
            
            # Convert to mono if stereo
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)
            
            # Extract features
            features = self.extract_features(audio_data, sample_rate)
            
            # Test against all enrolled users
            best_score = float('-inf')
            best_user = None
            
            for model_file in os.listdir(self.models_dir):
                if model_file.endswith('.pkl'):
                    user_id = model_file.replace('user_', '').replace('.pkl', '')
                    
                    with open(os.path.join(self.models_dir, model_file), 'rb') as f:
                        gmm = pickle.load(f)
                    
                    score = gmm.score(features)
                    
                    if score > best_score:
                        best_score = score
                        best_user = user_id
            
            if best_score > threshold:
                confidence = float(min(100, max(0, (best_score - threshold) * 2 + 50)))
                print(f"✓ Identified user {best_user} with {confidence:.1f}% confidence")
                return str(best_user), confidence
            else:
                print("✗ No matching user found")
                return None, 0.0
                
        except Exception as e:
            print(f"✗ Identification failed: {str(e)}")
            return None, 0.0
    
    def delete_user(self, user_id):
        """
        Delete a user's voice model
        
        Args:
            user_id: User ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            model_path = os.path.join(self.models_dir, f"user_{user_id}.pkl")
            if os.path.exists(model_path):
                os.remove(model_path)
                print(f"✓ User {user_id} deleted")
                return True
            else:
                print(f"✗ User {user_id} not found")
                return False
        except Exception as e:
            print(f"✗ Deletion failed: {str(e)}")
            return False


# Example usage
if __name__ == "__main__":
    # Initialize authenticator
    auth = VoiceAuthenticator()
    
    # Example: Enroll a user
    # auth.enroll_user(user_id=1, audio_file_path="user1_enrollment.wav")
    
    # Example: Verify a user
    # is_verified, confidence = auth.verify_user(user_id=1, audio_file_path="user1_test.wav")
    
    # Example: Identify unknown speaker
    # user_id, confidence = auth.identify_user(audio_file_path="unknown_speaker.wav")
    
    print("Voice Authentication System Ready")
