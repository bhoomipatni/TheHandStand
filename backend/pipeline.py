"""
Complete ASL Translation Pipeline
MediaPipe → Gemini → ElevenLabs Agent Integration
"""


import os
import cv2
import time
from typing import Dict, Any, Optional
from backend.hand_tracking import HandTracker
from backend.demo_classifier import DemoASLClassifier
from backend.word_builder import WordBuilder
from backend.translator import GeminiTranslator
from backend.speech import SpeechSynthesizer
from utils.config import PREDICTION_CONFIG

class ASLPipeline:
    """Simple pipeline for web interface ASL recognition"""
    
    def __init__(self):
        """Initialize simplified pipeline for web processing"""
        self.hand_tracker = HandTracker()
        self.classifier = DemoASLClassifier()
        # Initialize translation and speech but don't fail if they have issues
        try:
            self.translator = GeminiTranslator()
        except:
            print("Translation disabled - continuing without it")
            self.translator = None
            
        try:
            self.speech_synthesizer = SpeechSynthesizer(preferred_service="elevenlabs")
        except:
            print("Speech disabled - continuing without it")
            self.speech_synthesizer = None
        
        # State for single-gesture detection mode
        self.detected_gestures = []
        self.last_gesture = None
        self.gesture_count = 0
        self.detection_active = False  # Manual start/auto stop
        
        # Gesture name mapping for display
        self.gesture_display_names = {
            'i_love_you': 'I love you',
            'thank_you': 'thank you',
            'hello': 'hello',
            'help': 'help',
            'no': 'no',
            'please': 'please',
            'yes': 'yes'
        }
        
        print("ASL Pipeline initialized for web interface")
    
    def process_frame(self, frame) -> Dict[str, Any]:
        """Process a single frame and return recognition results"""
        try:
            # Only process if detection is active
            if not self.detection_active:
                return {
                    'success': True,
                    'gesture': None,
                    'confidence': 0,
                    'translation': 'Press "Start Detection" to begin',
                    'gesture_count': self.gesture_count,
                    'detection_active': False
                }
            
            # Step 1: Detect hands using MediaPipe
            landmarks = self.hand_tracker.detect_hands(frame)
            print(f"Debug: Landmarks detected: {landmarks is not None}")
            
            if landmarks is not None:
                print(f"Debug: Landmarks shape: {len(landmarks) if landmarks is not None else 0}")
                # Step 2: Classify gesture using single frame
                prediction = self.classifier.predict_single_frame(landmarks)
                print(f"Debug: Prediction result: {prediction}")
                
                if prediction and prediction.get('confidence', 0) > 0.15:
                    gesture = prediction['gesture']
                    confidence = prediction['confidence']
                    
                    # Convert internal gesture name to display name
                    display_gesture = self.gesture_display_names.get(gesture, gesture)
                    
                    # Single gesture mode - detect once and stop
                    self.gesture_count += 1
                    
                    # Use ONLY the current gesture (no accumulation, no sentence building)
                    current_sentence = display_gesture
                    improved_sentence = display_gesture  # Start with just the gesture
                    
                    # Improve sentence with Gemini (if available) - but keep it simple for single gestures
                    if self.translator:
                        try:
                            # For single gestures, maybe just clean up the text slightly
                            improved_sentence = self.translator.improve_sentence(display_gesture)
                            if not improved_sentence or improved_sentence.strip() == "":
                                improved_sentence = display_gesture
                        except:
                            improved_sentence = display_gesture
                    
                    # Generate speech with ElevenLabs (if available) - speak only current gesture
                    speech_success = False
                    if self.speech_synthesizer:
                        try:
                            speech_success = self.speech_synthesizer.speak_text(improved_sentence)
                        except Exception as e:
                            print(f"Speech synthesis error: {e}")
                    
                    # AUTOMATICALLY STOP after detection and speech
                    self.detection_active = False
                    self.last_gesture = None  # Reset for next detection
                    # DON'T add to detected_gestures list - keep it independent
                    
                    result = {
                        'gesture': display_gesture,
                        'confidence': confidence,
                        'translation': improved_sentence,
                        'sentence': display_gesture,  # Always just the single gesture
                        'gesture_count': self.gesture_count,
                        'speech_played': speech_success,
                        'success': True,
                        'detection_active': False,  # Now stopped
                        'auto_stopped': True  # Flag to indicate auto-stop
                    }
                    
                    print(f"🤟 Gesture: {display_gesture}")
                    print(f"📝 Translation: {improved_sentence}")
                    print(f"🛑 Auto-stopped after detection")
                    
                    return result
                else:
                    print(f"Debug: Prediction confidence too low: {prediction.get('confidence', 0) if prediction else 'None'}")
            
            # No gesture detected but detection is still active
            print("Debug: No gesture detected, still listening...")
            return {
                'gesture': None,
                'confidence': 0.0,
                'translation': 'Listening for gesture...',
                'detection_active': True,
                'success': True
            }
            
        except Exception as e:
            print(f"Error in pipeline processing: {e}")
            return {
                'gesture': 'Error',
                'confidence': 0.0,
                'translation': f'Processing error: {str(e)}',
                'success': False
            }
    
    def reset_demo(self):
        """Reset the demo - clear gesture history"""
        self.detected_gestures = []
        self.last_gesture = None
        self.gesture_count = 0
        print("Demo reset - gesture history cleared")
    
    def start_detection(self):
        """Start single gesture detection"""
        self.detection_active = True
        self.last_gesture = None
        # Clear any accumulated gestures for fresh start
        self.detected_gestures = []
        print("🎯 Detection started - show your gesture!")
    
    def stop_detection(self):
        """Stop gesture detection"""
        self.detection_active = False
        print("🛑 Detection stopped")

class ASLTranslationPipeline:
    """Complete pipeline for ASL translation with ElevenLabs agent"""
    
    def __init__(self, agent_id: Optional[str] = None):
        """Initialize the complete translation pipeline"""
        # Initialize all components
        self.hand_tracker = HandTracker()
        self.classifier = ASLClassifier()
        self.word_builder = WordBuilder()
        self.translator = GeminiTranslator()
        self.speech_synthesizer = SpeechSynthesizer(preferred_service="elevenlabs_agent")
        
        # Setup ElevenLabs agent if provided
        if agent_id:
            self.speech_synthesizer.setup_agent(agent_id)
        
        # Pipeline state
        self.is_running = False
        self.current_sentence = ""
        self.last_translation = ""
        
    def start_pipeline(self):
        """Start the complete ASL translation pipeline"""
        self.is_running = True
        
        # Initialize camera
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        
        print("🤟 ASL Translation Pipeline Started!")
        print("Pipeline: MediaPipe → Classifier → Word Builder → Gemini → ElevenLabs Agent")
        
        try:
            while self.is_running:
                ret, frame = cap.read()
                if not ret:
                    continue
                
                # Step 1: MediaPipe hand tracking
                landmarks = self.hand_tracker.detect_hands(frame)
                
                if landmarks is not None:
                    # Step 2: ASL classification
                    prediction = self.classifier.predict(landmarks)
                    
                    if prediction and prediction['confidence'] > PREDICTION_CONFIG['confidence_threshold']:
                        # Step 3: Word building
                        self.word_builder.add_letter_prediction(
                            prediction['letter'], 
                            prediction['confidence'],
                            time.time()
                        )
                        
                        # Check if sentence is updated
                        current_sentence = self.word_builder.get_current_sentence()
                        
                        if current_sentence != self.current_sentence and len(current_sentence.strip()) > 0:
                            self.current_sentence = current_sentence
                            
                            # Step 4: Translation with Gemini
                            translation = self.translator.improve_sentence(self.current_sentence)
                            
                            if translation and translation != self.last_translation:
                                self.last_translation = translation
                                
                                # Step 5: ElevenLabs Agent Response
                                response = self.speech_synthesizer.process_asl_translation(translation)
                                
                                print(f"ASL: {self.current_sentence}")
                                print(f"Translation: {translation}")
                                print(f"Speech: {response['service']} - {response.get('success', False)}")
                                print("-" * 50)
                
                # Display frame with landmarks
                if landmarks is not None:
                    frame = self.hand_tracker.draw_landmarks_on_image(frame, landmarks)
                
                # Show current sentence on frame
                cv2.putText(frame, f"Sentence: {self.current_sentence}", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, f"Translation: {self.last_translation}", 
                           (10, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                
                cv2.imshow('ASL Translation Pipeline', frame)
                
                # Exit on 'q' key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
        except KeyboardInterrupt:
            print("\\nPipeline stopped by user")
        finally:
            cap.release()
            cv2.destroyAllWindows()
            self.is_running = False
    
    def process_single_translation(self, asl_text: str) -> Dict[str, Any]:
        """Process a single ASL text through the pipeline"""
        try:
            # Step 1: Improve sentence with Gemini
            improved_text = self.translator.improve_sentence(asl_text)
            
            # Step 2: Generate speech with ElevenLabs agent
            speech_response = self.speech_synthesizer.process_asl_translation(improved_text)
            
            return {
                "original": asl_text,
                "improved": improved_text,
                "speech": speech_response,
                "success": True
            }
            
        except Exception as e:
            return {
                "original": asl_text,
                "error": str(e),
                "success": False
            }
    
    def reset_conversation(self):
        """Reset the conversation and sentence building"""
        self.detected_gestures = []
        self.last_gesture = None
        self.detection_active = False
        self.gesture_count = 0  # Also reset gesture count
        print("Detection reset!")
    
    def stop_pipeline(self):
        """Stop the translation pipeline"""
        self.is_running = False

# Example usage and testing
if __name__ == "__main__":
    # Initialize pipeline with your ElevenLabs agent ID
    pipeline = ASLTranslationPipeline(agent_id=os.getenv('ELEVENLABS_AGENT_ID'))
    
    # Test single translation
    test_result = pipeline.process_single_translation("HELLO HOW ARE YOU")
    print("Test Result:", test_result)
    
    # Start live pipeline (uncomment to run)
    # pipeline.start_pipeline()