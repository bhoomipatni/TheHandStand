"""
Speech Synthesis Module
Supports ElevenLabs and Google TTS
"""

import io
import requests
import pygame
import tempfile
import os
from utils.config import get_elevenlabs_api_key, get_google_tts_config

class SpeechSynthesizer:
    def __init__(self, preferred_service="elevenlabs"):
        """Initialize speech synthesis"""
        self.preferred_service = preferred_service
        self.elevenlabs_api_key = get_elevenlabs_api_key()
        self.agent_id = os.getenv('ELEVENLABS_AGENT_ID')
        
        # Voice settings
        self.voice_settings = {
            "stability": 0.5,
            "similarity_boost": 0.5,
            "style": 0.0,
            "use_speaker_boost": True
        }
        
        # Initialize pygame for audio playback
        self.pygame_initialized = False
        try:
            pygame.mixer.init()
            self.pygame_initialized = True
            print("Audio system initialized")
        except Exception as e:
            print(f"Audio initialization failed, will use fallback: {e}")
            self.pygame_initialized = False
        
        # Log configuration
        if self.elevenlabs_api_key:
            print("ElevenLabs API key loaded")
        else:
            print("ElevenLabs API key not found")
            
        if self.agent_id:
            print(f"ElevenLabs agent ID loaded: {self.agent_id[:20]}...")
        else:
            print("ElevenLabs agent ID not found")
        
    def setup_agent(self, agent_id):
        """Setup ElevenLabs conversational agent"""
        self.agent_id = agent_id
        print(f"ElevenLabs agent configured: {agent_id}")
    
    def speak_text(self, text, language="en", voice_id=None):
        """Convert text to speech and play"""
        if not text or not text.strip():
            return False
        
        if self.preferred_service == "elevenlabs_agent" and self.agent_id:
            return self._elevenlabs_agent_speak(text)
        elif self.preferred_service == "elevenlabs":
            return self._elevenlabs_tts(text, voice_id)
        else:
            return self._fallback_tts(text)
    
    def _elevenlabs_agent_speak(self, text):
        """Use ElevenLabs conversational agent"""
        if not self.elevenlabs_api_key or not self.agent_id:
            return self._fallback_tts(text)
        
        try:
            url = f"https://api.elevenlabs.io/v1/convai/agents/{self.agent_id}/speak"
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "voice_settings": self.voice_settings
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            # Play audio directly from response
            audio_data = response.content
            return self._play_audio(audio_data)
            
        except Exception as e:
            print(f"ElevenLabs agent error: {e}")
            return self._fallback_tts(text)
    
    def _elevenlabs_tts(self, text, voice_id=None):
        """Generate speech using ElevenLabs TTS API"""
        if not self.elevenlabs_api_key:
            return self._fallback_tts(text)
        
        # Default voice ID (Rachel - natural female voice)
        if not voice_id:
            voice_id = "21m00Tcm4TlvDq8ikWAM"
        
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            
            headers = {
                "xi-api-key": self.elevenlabs_api_key,
                "Content-Type": "application/json"
            }
            
            data = {
                "text": text,
                "voice_settings": self.voice_settings,
                "model_id": "eleven_monolingual_v1"
            }
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            
            # Play audio
            audio_data = response.content
            return self._play_audio(audio_data)
            
        except Exception as e:
            print(f"ElevenLabs TTS error: {e}")
            return self._fallback_tts(text)
    
    def _fallback_tts(self, text):
        """Fallback to system TTS or pygame"""
        try:
            # Try Windows SAPI
            import win32com.client
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Speak(text)
            return True
        except:
            try:
                # Try espeak (cross-platform)
                os.system(f'echo "{text}" | espeak')
                return True
            except:
                print(f"Speaking (fallback): {text}")
                return False
    
    def _play_audio(self, audio_data):
        """Play audio data using pygame"""
        try:
            # Save to temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                temp_file.write(audio_data)
                temp_filename = temp_file.name
            
            # Load and play with pygame
            pygame.mixer.music.load(temp_filename)
            pygame.mixer.music.play()
            
            # Wait for playback to complete
            while pygame.mixer.music.get_busy():
                pygame.time.wait(100)
            
            # Clean up
            os.unlink(temp_filename)
            return True
            
        except Exception as e:
            print(f"Audio playback error: {e}")
            return False
    
    def get_available_voices(self):
        """Get list of available voices from ElevenLabs"""
        if not self.elevenlabs_api_key:
            return {}
        
        try:
            url = "https://api.elevenlabs.io/v1/voices"
            headers = {"xi-api-key": self.elevenlabs_api_key}
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            voices_data = response.json()
            voices = {}
            
            for voice in voices_data.get("voices", []):
                voices[voice["voice_id"]] = voice["name"]
            
            return voices
            
        except Exception as e:
            print(f"Failed to get voices: {e}")
            return {
                "21m00Tcm4TlvDq8ikWAM": "Rachel (Default)",
                "AZnzlk1XvdvUeBnXmlld": "Domi",
                "EXAVITQu4vr4xnSDxMaL": "Bella"
            }
    
    def set_voice_settings(self, stability=0.5, similarity=0.5, style=0.0):
        """Configure voice settings for ElevenLabs"""
        self.voice_settings = {
            "stability": stability,
            "similarity_boost": similarity,
            "style": style,
            "use_speaker_boost": True
        }
        print(f"Voice settings updated: {self.voice_settings}")