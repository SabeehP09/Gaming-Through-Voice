"""
Voice Recognition API Server
Flask-based REST API to connect C# application with Python voice backend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import base64
import numpy as np
import io
import soundfile as sf
from voice_authentication import VoiceAuthenticator
from voice_command_recognizer import VoiceCommandRecognizer
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for C# client

# Initialize voice systems
authenticator = VoiceAuthenticator(models_dir="voice_models")
recognizer = VoiceCommandRecognizer(commands_file="commands.json")


def decode_audio(audio_base64):
    """
    Decode base64 audio data to numpy array
    
    Args:
        audio_base64: Base64 encoded audio data
        
    Returns:
        (audio_data, sample_rate)
    """
    try:
        # Decode base64
        audio_bytes = base64.b64decode(audio_base64)
        
        # Read audio from bytes
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
            'command_recognition': 'running'
        }
    })


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.route('/auth/enroll', methods=['POST'])
def enroll_user():
    """
    Enroll a new user for voice authentication
    
    Request JSON:
    {
        "user_id": 123,
        "audio_data": "base64_encoded_audio"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        audio_base64 = data.get('audio_data')
        
        if not user_id or not audio_base64:
            return jsonify({'error': 'Missing user_id or audio_data'}), 400
        
        # Decode audio
        audio_data, sample_rate = decode_audio(audio_base64)
        
        # Enroll user
        success = authenticator.enroll_user(
            user_id=user_id,
            audio_data=audio_data,
            sample_rate=sample_rate
        )
        
        if success:
            return jsonify({
                'success': True,
                'message': f'User {user_id} enrolled successfully'
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
    """
    Verify user identity through voice
    
    Request JSON:
    {
        "user_id": 123,
        "audio_data": "base64_encoded_audio",
        "threshold": -50  (optional)
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        audio_base64 = data.get('audio_data')
        threshold = data.get('threshold', -50)
        
        if not user_id or not audio_base64:
            return jsonify({'error': 'Missing user_id or audio_data'}), 400
        
        # Decode audio
        audio_data, sample_rate = decode_audio(audio_base64)
        
        # Verify user
        is_verified, confidence = authenticator.verify_user(
            user_id=user_id,
            audio_data=audio_data,
            sample_rate=sample_rate,
            threshold=threshold
        )
        
        return jsonify({
            'verified': is_verified,
            'confidence': float(confidence),
            'user_id': user_id
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/auth/identify', methods=['POST'])
def identify_user():
    """
    Identify which user is speaking
    
    Request JSON:
    {
        "audio_data": "base64_encoded_audio",
        "threshold": -50  (optional)
    }
    """
    try:
        data = request.json
        audio_base64 = data.get('audio_data')
        threshold = data.get('threshold', -50)
        
        if not audio_base64:
            return jsonify({'error': 'Missing audio_data'}), 400
        
        # Decode audio
        audio_data, sample_rate = decode_audio(audio_base64)
        
        # Identify user
        user_id, confidence = authenticator.identify_user(
            audio_data=audio_data,
            sample_rate=sample_rate,
            threshold=threshold
        )
        
        if user_id:
            return jsonify({
                'identified': True,
                'user_id': user_id,
                'confidence': float(confidence)
            })
        else:
            return jsonify({
                'identified': False,
                'user_id': None,
                'confidence': 0.0
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/auth/delete', methods=['POST'])
def delete_user():
    """
    Delete user's voice model
    
    Request JSON:
    {
        "user_id": 123
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({'error': 'Missing user_id'}), 400
        
        success = authenticator.delete_user(user_id)
        
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
    
    Request JSON:
    {
        "audio_data": "base64_encoded_audio",
        "threshold": 0.7  (optional)
    }
    """
    try:
        data = request.json
        audio_base64 = data.get('audio_data')
        threshold = data.get('threshold', 0.7)
        
        if not audio_base64:
            return jsonify({'error': 'Missing audio_data'}), 400
        
        # Decode audio
        audio_data, sample_rate = decode_audio(audio_base64)
        
        # Save temporarily for recognition
        temp_file = "temp_command.wav"
        sf.write(temp_file, audio_data, sample_rate)
        
        # Recognize speech
        text = recognizer.recognize_speech()
        
        # Match command
        category, action, confidence = recognizer.match_command(text, threshold)
        
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        
        return jsonify({
            'recognized': action is not None,
            'text': text,
            'category': category,
            'action': action,
            'confidence': confidence
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/commands/list', methods=['GET'])
def list_commands():
    """Get all available commands"""
    try:
        category = request.args.get('category')
        
        if category:
            if category in recognizer.commands:
                return jsonify({
                    'category': category,
                    'commands': recognizer.commands[category]
                })
            else:
                return jsonify({'error': f'Category {category} not found'}), 404
        else:
            return jsonify({
                'commands': recognizer.commands
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/commands/add', methods=['POST'])
def add_command():
    """
    Add a new voice command
    
    Request JSON:
    {
        "category": "gaming",
        "phrase": "shoot",
        "action": "SHOOT"
    }
    """
    try:
        data = request.json
        category = data.get('category')
        phrase = data.get('phrase')
        action = data.get('action')
        
        if not all([category, phrase, action]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        recognizer.add_command(category, phrase, action)
        
        return jsonify({
            'success': True,
            'message': f'Command added: {phrase} -> {action}'
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/commands/remove', methods=['POST'])
def remove_command():
    """
    Remove a voice command
    
    Request JSON:
    {
        "category": "gaming",
        "phrase": "shoot"
    }
    """
    try:
        data = request.json
        category = data.get('category')
        phrase = data.get('phrase')
        
        if not all([category, phrase]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        success = recognizer.remove_command(category, phrase)
        
        return jsonify({
            'success': success,
            'message': f'Command removed: {phrase}' if success else 'Command not found'
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
        total_commands = sum(len(cmds) for cmds in recognizer.commands.values())
        
        return jsonify({
            'enrolled_users': enrolled_users,
            'total_commands': total_commands,
            'command_categories': list(recognizer.commands.keys()),
            'models_directory': authenticator.models_dir,
            'commands_file': recognizer.commands_file
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 Starting Voice Recognition API Server...")
    print("📡 Server will be available at: http://localhost:5000")
    print("\nAvailable endpoints:")
    print("  GET  /health - Health check")
    print("  POST /auth/enroll - Enroll user")
    print("  POST /auth/verify - Verify user")
    print("  POST /auth/identify - Identify user")
    print("  POST /auth/delete - Delete user")
    print("  POST /commands/recognize - Recognize command")
    print("  GET  /commands/list - List commands")
    print("  POST /commands/add - Add command")
    print("  POST /commands/remove - Remove command")
    print("  GET  /system/info - System info")
    
    app.run(host='0.0.0.0', port=5000, debug=True)
