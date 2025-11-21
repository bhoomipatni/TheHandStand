"""
Demo ASL Classifier - Updated to use Static Geometric Features
Provides instant, accurate gesture recognition without frame sequences
"""

import numpy as np
import os
import json
import joblib
from typing import Optional, Dict, Any

class DemoASLClassifier:
    """
    Static gesture classifier using hand landmark geometric features
    Drop-in replacement for the old LSTM classifier with better accuracy
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.idx_to_word = {}
        self.word_to_idx = {}
        self.labels_map = {}
        self.confidence_threshold = 0.5
        self.model_loaded = False
        
        # Load static model if available, fallback to LSTM
        if not self.load_static_model():
            self.load_lstm_fallback()
    
    def load_static_model(self):
        """Load the trained static classifier model"""
        model_path = "data/models/static_classifier.pkl"
        
        if not os.path.exists(model_path):
            print("Static classifier not found. Run: python train_static_classifier.py")
            return False
        
        try:
            model_data = joblib.load(model_path)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.idx_to_word = model_data['idx_to_label']
            self.word_to_idx = model_data['label_to_idx']
            self.labels_map = self.idx_to_word
            
            self.model_loaded = True
            self.model_type = 'static'
            print(f"Static classifier loaded: {list(self.labels_map.values())}")
            return True
            
        except Exception as e:
            print(f"Error loading static classifier: {e}")
            return False
    
    def load_lstm_fallback(self):
        """Fallback to LSTM model if static model not available"""
        try:
            import tensorflow as tf
            from tensorflow import keras
            
            # Try to load demo model first
            demo_model_path = "data/models/saved_models/demo_model.h5"
            demo_info_path = "data/models/demo_model_info.json"
            
            if os.path.exists(demo_model_path) and os.path.exists(demo_info_path):
                self.model = keras.models.load_model(demo_model_path)
                with open(demo_info_path, 'r') as f:
                    model_info = json.load(f)
                self.labels_map = model_info.get('labels_map', {})
                self.idx_to_word = {int(k): v for k, v in self.labels_map.items()}
                print(f"LSTM fallback loaded: {list(self.labels_map.values())}")
                self.model_type = 'lstm'
                self.model_loaded = True
                return True
        except Exception as e:
            print(f"Error loading LSTM fallback: {e}")
        
        # Create mock classifier if no models available
        self.labels_map = {0: "hello", 1: "no", 2: "please", 3: "thank_you", 4: "yes"}
        self.idx_to_word = self.labels_map
        self.model_type = 'mock'
        self.model_loaded = True
        print("No models found - using mock classifier")
        return False
    
    def extract_geometric_features(self, landmarks):
        """Extract geometric features from hand landmarks"""
        if landmarks is None:
            return None
            
        # Handle different input formats - convert to (42,) format
        if len(landmarks) == 126:
            # Convert 126 to 42 format (take just x,y from first hand)
            landmarks_reshaped = np.array(landmarks).reshape(2, 21, 3)
            landmarks_42 = []
            for i in range(21):
                landmarks_42.extend([landmarks_reshaped[0][i][0], landmarks_reshaped[0][i][1]])
            landmarks = landmarks_42
        elif len(landmarks) != 42:
            return None
        
        # Reshape to (21, 2) for x,y coordinates
        landmarks = np.array(landmarks).reshape(21, 2)
        features = []
        
        # Normalize relative to wrist (landmark 0)
        wrist = landmarks[0]
        normalized_landmarks = landmarks - wrist
        
        # Finger tip landmarks: thumb(4), index(8), middle(12), ring(16), pinky(20)
        fingertips = [4, 8, 12, 16, 20]
        finger_bases = [2, 5, 9, 13, 17]
        
        # 1. Distances from wrist to fingertips
        for tip in fingertips:
            dist = np.linalg.norm(normalized_landmarks[tip])
            features.append(dist)
        
        # 2. Finger extension ratios
        for tip, base in zip(fingertips, finger_bases):
            tip_dist = np.linalg.norm(normalized_landmarks[tip])
            base_dist = np.linalg.norm(normalized_landmarks[base])
            ratio = tip_dist / (base_dist + 1e-6)
            features.append(ratio)
        
        # 3. Angles between fingers
        for i in range(4):
            v1 = normalized_landmarks[fingertips[i]]
            v2 = normalized_landmarks[fingertips[i+1]]
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
            angle = np.arccos(np.clip(cos_angle, -1, 1))
            features.append(angle)
        
        # 4. Hand orientation
        palm_vector = normalized_landmarks[9]  # Middle finger base
        features.append(np.arctan2(palm_vector[1], palm_vector[0]))
        
        # 5. Finger spreads
        thumb_index_dist = np.linalg.norm(normalized_landmarks[4] - normalized_landmarks[8])
        thumb_middle_dist = np.linalg.norm(normalized_landmarks[4] - normalized_landmarks[12])
        index_middle_dist = np.linalg.norm(normalized_landmarks[8] - normalized_landmarks[12])
        features.extend([thumb_index_dist, thumb_middle_dist, index_middle_dist])
        
        # 6. Hand openness
        palm_center = np.mean(normalized_landmarks[[0, 5, 9, 13, 17]], axis=0)
        openness = np.mean([np.linalg.norm(normalized_landmarks[tip] - palm_center) for tip in fingertips])
        features.append(openness)
        
        # 7. Hand size
        hand_size = np.max([np.linalg.norm(normalized_landmarks[i]) for i in range(21)])
        features.append(hand_size)
        
        # 8. Thumb position
        thumb_pos = normalized_landmarks[4]
        index_pos = normalized_landmarks[8]
        thumb_angle = np.arctan2(thumb_pos[1] - index_pos[1], thumb_pos[0] - index_pos[0])
        features.append(thumb_angle)
        
        return np.array(features)
    
    def predict_single_frame(self, landmarks) -> Optional[Dict[str, Any]]:
        """Predict gesture from a single frame - INSTANT recognition"""
        if landmarks is None:
            return None
        
        try:
            # Ensure a model is loaded; __init__ should have attempted this already
            if not self.model_loaded:
                # Try loading static first, then LSTM fallback
                self.load_static_model() or self.load_lstm_fallback()

            # Use behavior based on detected model type
            if getattr(self, 'model_type', None) == 'static' and self.model is not None:
                # Use static geometric classifier
                features = self.extract_geometric_features(landmarks)
                if features is None:
                    return None

                # Scale features if scaler available
                try:
                    features_scaled = self.scaler.transform([features]) if self.scaler is not None else [features]
                except Exception:
                    features_scaled = [features]

                # Predict probabilities if available
                if hasattr(self.model, 'predict_proba'):
                    probabilities = self.model.predict_proba(features_scaled)[0]
                    predicted_class = int(np.argmax(probabilities))
                    confidence = float(probabilities[predicted_class])
                else:
                    # Fallback to direct predict if no predict_proba
                    predicted_class = int(self.model.predict(features_scaled)[0])
                    confidence = 1.0

                if confidence < self.confidence_threshold:
                    return None

                gesture_name = self.idx_to_word.get(predicted_class, "Unknown")
                return {'gesture': gesture_name, 'confidence': confidence}

            elif getattr(self, 'model_type', None) == 'mock':
                # Mock classifier for testing
                return {'gesture': 'hello', 'confidence': 0.8}

            else:
                # Other model types (LSTM or unknown) - try to use generic predict/proba if possible
                if self.model is not None:
                    try:
                        # Attempt to predict using whatever interface is available
                        if hasattr(self.model, 'predict_proba'):
                            probs = self.model.predict_proba([landmarks])[0]
                            predicted_class = int(np.argmax(probs))
                            confidence = float(probs[predicted_class])
                            gesture_name = self.idx_to_word.get(predicted_class, 'Unknown')
                            if confidence < self.confidence_threshold:
                                return None
                            return {'gesture': gesture_name, 'confidence': confidence}
                        else:
                            pred = self.model.predict([landmarks])[0]
                            gesture_name = self.idx_to_word.get(int(pred), str(pred))
                            return {'gesture': gesture_name, 'confidence': 0.6}
                    except Exception as e:
                        print(f"Prediction error (generic model): {e}")
                        return None
                return None
                
        except Exception as e:
            print(f"Prediction error: {e}")
            return None
    
    def predict(self, landmarks):
        """Compatibility method"""
        return self.predict_single_frame(landmarks)

# Compatibility classes
EnhancedASLClassifier = DemoASLClassifier
ASLClassifier = DemoASLClassifier
