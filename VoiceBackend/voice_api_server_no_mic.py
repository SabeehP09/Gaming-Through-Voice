"""
Voice Recognition API Server (No Microphone Version)
Flask-based REST API - Works with pre-recorded audio only
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import io
import soundfile as sf
from voice_authentication import VoiceAuthenticator
from speaker_verification import SpeakerVerificationSystem
from robust_speaker_verification import RobustSpeakerVerification
from hybrid_voice_verification import HybridVoiceVerification
import os
import json

app = Flask(__name__)
CORS(app)  # Enable CORS for C# client

# Initialize voice authenticator (old GMM-based)
authenticator = VoiceAuthenticator(models_dir="voice_models")

# Initialize advanced speaker verification
speaker_verifier = SpeakerVerificationSystem(models_dir="voice_models_embeddings")

# Initialize ROBUST speaker verification
robust_verifier = RobustSpeakerVerification(models_dir="voice_models_robust")

# Initialize HYBRID verification (voice + phrase) - MOST SECURE!
hybrid_verifier = HybridVoiceVerification(models_dir="voice_models_hybrid")

# Use HYBRID verification by default (checks both voice AND phrase!)
USE_HYBRID_VERIFICATION = True
USE_ROBUST_VERIFICATION = False
USE_ADVANCED_VERIFICATION = False

# Load commands from file
COMMANDS_FILE = "commands.json"

def load_commands():
    """Load command definitions"""
    if os.path.exists(COMMANDS_FILE):
        with open(COMMANDS_FILE, 'r') as f:
            return json.load(f)
    else:
        # Default commands
        default_commands = {
            "navigation": {
                "go home": "HOME",
                "open dashboard": "DASHBOARD",
                "show profile": "PROFILE",
                "open settings": "SETTINGS",
                "show games": "GAMES",
                "voice commands": "VOICE_COMMANDS"
            },
            "gaming": {
                "jump": "JUMP",
                "move forward": "FORWARD",
                "move backward": "BACKWARD",
                "move left": "LEFT",
                "move right": "RIGHT",
                "attack": "ATTACK",
                "defend": "DEFEND",
                "pause game": "PAUSE",
                "resume game": "RESUME",
                "quit game": "QUIT"
            },
            "system": {
                "start listening": "START_LISTEN",
                "stop listening": "STOP_LISTEN",
                "help": "HELP",
                "repeat": "REPEAT",
                "cancel": "CANCEL",
                "confirm": "CONFIRM",
                "yes": "YES",
                "no": "NO"
            }
        }
        
        with open(COMMANDS_FILE, 'w') as f:
            json.dump(default_commands, f, indent=4)
        
        return default_commands

commands = load_commands()


def decode_audio(audio_base64):
    """Decode base64 audio data to numpy array"""
    try:
        audio_bytes = base64.b64decode(audio_base64)
        audio_data, sample_rate = sf.read(io.BytesIO(audio_bytes))
        return audio_data, sample_rate
    except Exception as e:
        raise ValueError(f"Failed to decode audio: {str(e)}")


@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'services': {
            'authentication': 'running',
            'command_recognition': 'limited (no microphone)'
        },
        'note': 'This is the no-microphone version. Audio must be sent via API.'
    })


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/auth/enroll', methods=['POST'])
def enroll_user():
    """Enroll a new user for voice authentication using advanced speaker verification"""
    try:
        data = request.json
        user_id = data.get('user_id')
        audio_base64 = data.get('audio_data')
        
        if not user_id or not audio_base64:
            return jsonify({'error': 'Missing user_id or audio_data'}), 400
        
        # Decode audio
        audio_data, sample_rate = decode_audio(audio_base64)
        
        # Use HYBRID verification (voice + phrase) - most secure!
        if USE_HYBRID_VERIFICATION:
            success = hybrid_verifier.enroll_speaker(
                user_id=user_id,
                audio_data=audio_data,
                sample_rate=sample_rate
            )
        elif USE_ROBUST_VERIFICATION:
            success = robust_verifier.enroll_speaker(
                user_id=user_id,
                audio_data=audio_data,
                sample_rate=sample_rate
            )
        elif USE_ADVANCED_VERIFICATION:
            success = speaker_verifier.enroll_speaker(
                user_id=user_id,
                audio_data=audio_data,
                sample_rate=sample_rate
            )
        else:
            # Fallback to old GMM method
            success = authenticator.enroll_user(
                user_id=user_id,
                audio_data=audio_data,
                sample_rate=sample_rate
            )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'User {user_id} enrolled successfully with advanced speaker verification'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Enrollment failed'
            }), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/auth/verify', methods=['POST'])
def verify_user():
    """Verify user identity through voice using advanced speaker verification"""
    try:
        data = request.json
        user_id = data.get('user_id')
        audio_base64 = data.get('audio_data')
        threshold = data.get('threshold', 0.80)  # Default to strict threshold
        
        if not user_id or not audio_base64:
            return jsonify({'error': 'Missing user_id or audio_data'}), 400
        
        # Decode audio
        audio_data, sample_rate = decode_audio(audio_base64)
        
        # Use ROBUST speaker verification (best!)
        if USE_ROBUST_VERIFICATION:
            is_verified, confidence = robust_verifier.verify_speaker(
                user_id=user_id,
                audio_data=audio_data,
                sample_rate=sample_rate,
                threshold=threshold if threshold != 0.80 else None
            )
        elif USE_ADVANCED_VERIFICATION:
            is_verified, confidence = speaker_verifier.verify_speaker(
                user_id=user_id,
                audio_data=audio_data,
                sample_rate=sample_rate,
                threshold=threshold
            )
        else:
            # Fallback to old GMM method
            is_verified, confidence = authenticator.verify_user(
                user_id=user_id,
                audio_data=audio_data,
                sample_rate=sample_rate,
                threshold=threshold
            )
        
        return jsonify({
            'verified': bool(is_verified),
            'confidence': float(confidence),
            'user_id': user_id,
            'method': 'advanced_speaker_verification' if USE_ADVANCED_VERIFICATION else 'gmm'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/auth/identify', methods=['POST'])
def identify_user():
    """Identify which user is speaking using advanced speaker verification"""
    try:
        data = request.json
        audio_base64 = data.get('audio_data')
        threshold = data.get('threshold', 0.80)  # Default to strict threshold
        
        if not audio_base64:
            return jsonify({'error': 'Missing audio_data'}), 400
        
        # Decode audio
        audio_data, sample_rate = decode_audio(audio_base64)
        
        # Use HYBRID verification (voice + phrase) - most secure!
        if USE_HYBRID_VERIFICATION:
            user_id, confidence = hybrid_verifier.identify_speaker(
                audio_data=audio_data,
                sample_rate=sample_rate
            )
        elif USE_ROBUST_VERIFICATION:
            # Ignore old GMM threshold (-50), use None to get default (0.5)
            use_threshold = None if threshold < 0 or threshold == 0.80 else threshold
            user_id, confidence = robust_verifier.identify_speaker(
                audio_data=audio_data,
                sample_rate=sample_rate,
                threshold=use_threshold
            )
        elif USE_ADVANCED_VERIFICATION:
            user_id, confidence = speaker_verifier.identify_speaker(
                audio_data=audio_data,
                sample_rate=sample_rate,
                threshold=threshold
            )
        else:
            # Fallback to old GMM method
            user_id, confidence = authenticator.identify_user(
                audio_data=audio_data,
                sample_rate=sample_rate,
                threshold=threshold
            )
        
        if user_id:
            return jsonify({
                'success': True,
                'identified': True,
                'user_id': str(user_id),
                'confidence': float(confidence),
                'method': 'advanced_speaker_verification' if USE_ADVANCED_VERIFICATION else 'gmm'
            })
        else:
            return jsonify({
                'success': False,
                'identified': False,
                'user_id': None,
                'confidence': 0.0,
                'message': 'No matching user found'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/auth/delete/<user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user's voice model from both systems"""
    try:
        # Delete from all systems
        success1 = hybrid_verifier.delete_speaker(user_id) if USE_HYBRID_VERIFICATION else True
        success2 = robust_verifier.delete_speaker(user_id) if USE_ROBUST_VERIFICATION else True
        success3 = speaker_verifier.delete_speaker(user_id) if USE_ADVANCED_VERIFICATION else True
        success4 = authenticator.delete_user(user_id)
        
        success = success1 or success2 or success3 or success4
        
        return jsonify({
            'success': success,
            'message': f'User {user_id} deleted' if success else 'User not found'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== COMMAND RECOGNITION ENDPOINTS ====================

@app.route('/commands/recognize', methods=['POST'])
def recognize_command():
    """
    Recognize voice command from audio
    Note: This version uses simple text matching, not speech recognition
    """
    try:
        data = request.json
        audio_base64 = data.get('audio_data')
        text = data.get('text')  # Optional: pre-recognized text
        threshold = data.get('threshold', 0.7)
        
        if not audio_base64 and not text:
            return jsonify({'error': 'Missing audio_data or text'}), 400
        
        # For now, return a mock response
        # In full version, this would use speech recognition
        return jsonify({
            'recognized': False,
            'text': None,
            'category': None,
            'action': None,
            'confidence': 0,
            'note': 'Speech recognition requires PyAudio. Use text parameter for testing.'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/commands/list', methods=['GET'])
def list_commands():
    """Get all available commands"""
    try:
        category = request.args.get('category')
        
        if category:
            if category in commands:
                return jsonify({
                    'category': category,
                    'commands': commands[category]
                })
            else:
                return jsonify({'error': f'Category {category} not found'}), 404
        else:
            return jsonify({
                'commands': commands
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/commands/add', methods=['POST'])
def add_command():
    """Add a new voice command"""
    try:
        data = request.json
        category = data.get('category')
        phrase = data.get('phrase')
        action = data.get('action')
        
        if not all([category, phrase, action]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if category not in commands:
            commands[category] = {}
        
        commands[category][phrase.lower()] = action
        
        # Save to file
        with open(COMMANDS_FILE, 'w') as f:
            json.dump(commands, f, indent=4)
        
        return jsonify({
            'success': True,
            'message': f'Command added: {phrase} -> {action}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/commands/remove', methods=['POST'])
def remove_command():
    """Remove a voice command"""
    try:
        data = request.json
        category = data.get('category')
        phrase = data.get('phrase')
        
        if not all([category, phrase]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        if category in commands and phrase.lower() in commands[category]:
            del commands[category][phrase.lower()]
            
            # Save to file
            with open(COMMANDS_FILE, 'w') as f:
                json.dump(commands, f, indent=4)
            
            return jsonify({
                'success': True,
                'message': f'Command removed: {phrase}'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Command not found'
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ==================== SYSTEM ENDPOINTS ====================

@app.route('/system/info', methods=['GET'])
def system_info():
    """Get system information"""
    try:
        # Count enrolled users
        enrolled_users = len([f for f in os.listdir(authenticator.models_dir) 
                            if f.endswith('.pkl')])
        
        # Count commands
        total_commands = sum(len(cmds) for cmds in commands.values())
        
        return jsonify({
            'enrolled_users': enrolled_users,
            'total_commands': total_commands,
            'command_categories': list(commands.keys()),
            'models_directory': authenticator.models_dir,
            'commands_file': COMMANDS_FILE,
            'version': 'no-microphone',
            'note': 'This version works with pre-recorded audio only'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting Voice Recognition API Server (No Microphone Version)...")
    print("📡 Server will be available at: http://localhost:5000")
    print("\n⚠️  NOTE: This version does not support live microphone input.")
    print("   Audio must be sent via API as base64-encoded data.")
    print("\nAvailable endpoints:")
    print("  GET  /health - Health check")
    print("  POST /auth/enroll - Enroll user")
    print("  POST /auth/verify - Verify user")
    print("  POST /auth/identify - Identify user")
    print("  POST /auth/delete - Delete user")
    print("  POST /commands/recognize - Recognize command (limited)")
    print("  GET  /commands/list - List commands")
    print("  POST /commands/add - Add command")
    print("  POST /commands/remove - Remove command")
    print("  GET  /system/info - System info")
    print("\n✅ Voice authentication will work!")
    print("❌ Live speech recognition requires PyAudio installation")
    print("\n🔊 Voice Authentication Server running on: http://localhost:5001")
    
    app.run(host='0.0.0.0', port=5001, debug=True)
