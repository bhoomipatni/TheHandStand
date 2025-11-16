"""
Configuration Management for SignSpeak AI
"""

import os
import json
from typing import Optional

# API Configuration
def get_gemini_api_key() -> Optional[str]:
    """Get Gemini service account path for authentication"""
    # For service account authentication, return the path to the service account file
    service_account_path = os.getenv('GEMINI_SERVICE_ACCOUNT_JSON', 'service_account.json')
    if os.path.exists(service_account_path):
        return service_account_path
    
    # Fallback to direct API key if service account not found
    api_key = os.getenv('GEMINI_API_KEY')
    if api_key and api_key.strip() and not api_key.startswith('#'):
        return api_key.strip()
    
    print("No valid Gemini credentials found. Please check your service_account.json or .env")
    return None

def get_elevenlabs_api_key() -> Optional[str]:
    """Get ElevenLabs API key from environment variables"""
    return os.getenv('ELEVENLABS_API_KEY')

def get_google_tts_config() -> dict:
    """Get Google TTS configuration"""
    return {
        'credentials_path': os.getenv('GOOGLE_TTS_CREDENTIALS'),
        'project_id': os.getenv('GOOGLE_CLOUD_PROJECT')
    }

# Model Configuration
MODEL_PATHS = {
    'asl_pickle': 'models/asl_model.pkl',
    'asl_cnn': 'models/asl_cnn.h5',
    'metadata': 'models/model_metadata.json'
}

# Camera Configuration
CAMERA_CONFIG = {
    'width': 640,
    'height': 480,
    'fps': 30,
    'device_id': 0
}

# MediaPipe Configuration
MEDIAPIPE_CONFIG = {
    'static_image_mode': False,
    'max_num_hands': 2,
    'min_detection_confidence': 0.5,
    'min_tracking_confidence': 0.5
}

# Prediction Configuration
PREDICTION_CONFIG = {
    'confidence_threshold': 0.7,
    'letter_hold_time': 1.0,
    'word_gap_time': 2.0,
    'smoothing_window': 5
}

# Translation Configuration
TRANSLATION_CONFIG = {
    'default_target_language': 'es',
    'max_sentence_length': 500,
    'translation_timeout': 10
}

# Speech Configuration
SPEECH_CONFIG = {
    'default_voice': 'default',
    'speech_rate': 1.0,
    'volume': 1.0,
    'elevenlabs_voice_id': 'default'
}