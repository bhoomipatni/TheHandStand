"""
Static ASL Classifier
Fast, accurate single-frame gesture recognition using geometric hand features
"""

import numpy as np
import os
import json
import joblib
from typing import Optional, Dict, Any

class StaticASLClassifier:
    """
    Static gesture classifier using hand landmark geometric features
    Provides instant recognition without requiring frame sequences
    """
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.idx_to_word = {}
        self.word_to_idx = {}
        self.gesture_names = []
        self.confidence_threshold = 0.6
        self.model_loaded = False
        
        # Load model if available
        self.load_model()
    
    def load_model(self):
        """Load the trained static classifier model"""
        model_path = "data/models/static_classifier.pkl"
        
        if not os.path.exists(model_path):
            print("No static classifier found. Train one with train_static_classifier.py")
            return False
        
        try:
            model_data = joblib.load(model_path)
            
            self.model = model_data['model']
            self.scaler = model_data['scaler']
            self.idx_to_word = model_data['idx_to_label']
            self.word_to_idx = model_data['label_to_idx']
            self.gesture_names = model_data['gesture_names']
            
            self.model_loaded = True
            print(f"Static classifier loaded: {self.gesture_names}")
            return True
            
        except Exception as e:
            print(f"Error loading static classifier: {e}")
            return False
    
    def extract_geometric_features(self, landmarks):
        """
        Extract geometric features from hand landmarks for classification
        Returns a feature vector that captures hand shape and finger positions
        """
        if landmarks is None:
            return None
            
        # Handle different input formats
        if len(landmarks) == 42:
            # Convert 42-feature to 126-feature format
            landmarks_xy = np.array(landmarks).reshape(21, 2)
            landmarks_126 = np.zeros(126)
            for i in range(21):
                # First hand
                landmarks_126[i*3] = landmarks_xy[i, 0]
                landmarks_126[i*3 + 1] = landmarks_xy[i, 1]
                landmarks_126[i*3 + 2] = 0.0
                # Second hand (copy for single hand detection)
                landmarks_126[63 + i*3] = landmarks_xy[i, 0]
                landmarks_126[63 + i*3 + 1] = landmarks_xy[i, 1]
                landmarks_126[63 + i*3 + 2] = 0.0
            landmarks = landmarks_126
        elif len(landmarks) != 126:
            print(f"Warning: Unexpected landmark format: {len(landmarks)}")
            return None
        
        # Reshape to get 21 landmarks with (x, y, z) coordinates for each hand
        landmarks = np.array(landmarks).reshape(2, 21, 3)
        
        features = []
        
        # Process each hand separately
        for hand_idx in range(2):
            hand_landmarks = landmarks[hand_idx]
            
            # Skip if hand not detected (all zeros)
            if np.all(hand_landmarks == 0):
                features.extend([0] * 50)  # Add 50 zero features for missing hand
                continue
            
            # Wrist position (landmark 0)
            wrist = hand_landmarks[0]
            
            # Normalize all landmarks relative to wrist
            normalized_landmarks = hand_landmarks - wrist
            
            # Finger tip landmarks: thumb(4), index(8), middle(12), ring(16), pinky(20)
            fingertips = [4, 8, 12, 16, 20]
            # Finger base landmarks: thumb(2), index(5), middle(9), ring(13), pinky(17)
            finger_bases = [2, 5, 9, 13, 17]
            
            # Feature 1-5: Distances from wrist to fingertips
            for tip in fingertips:
                dist = np.linalg.norm(normalized_landmarks[tip])
                features.append(dist)
            
            # Feature 6-10: Finger extension ratios (tip distance / base distance)
            for i, (tip, base) in enumerate(zip(fingertips, finger_bases)):
                tip_dist = np.linalg.norm(normalized_landmarks[tip])
                base_dist = np.linalg.norm(normalized_landmarks[base])
                ratio = tip_dist / (base_dist + 1e-6)  # Avoid division by zero
                features.append(ratio)
            
            # Feature 11-20: Angles between adjacent fingers
            finger_vectors = []
            for tip in fingertips:
                vector = normalized_landmarks[tip]
                finger_vectors.append(vector)
            
            # Calculate angles between adjacent finger vectors
            for i in range(len(finger_vectors)-1):
                v1 = finger_vectors[i]
                v2 = finger_vectors[i+1]
                # Calculate angle using dot product
                cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
                angle = np.arccos(np.clip(cos_angle, -1, 1))
                features.append(angle)
                
            # Add more angle features
            for i in range(len(finger_vectors)):
                for j in range(i+2, len(finger_vectors)):
                    v1 = finger_vectors[i]
                    v2 = finger_vectors[j]
                    cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-6)
                    angle = np.arccos(np.clip(cos_angle, -1, 1))
                    features.append(angle)
            
            # Feature 21-25: Hand orientation (palm direction)
            # Vector from wrist to middle finger base
            palm_vector = normalized_landmarks[9]
            
            # Palm orientation angles
            palm_x_angle = np.arctan2(palm_vector[1], palm_vector[0])
            palm_y_angle = np.arctan2(palm_vector[2], palm_vector[0])
            palm_z_angle = np.arctan2(palm_vector[2], palm_vector[1])
            
            features.extend([palm_x_angle, palm_y_angle, palm_z_angle])
            
            # Feature 26-30: Finger spread measures
            # Distances between fingertips
            finger_spreads = []
            for i in range(len(fingertips)):
                for j in range(i+1, len(fingertips)):
                    dist = np.linalg.norm(normalized_landmarks[fingertips[i]] - normalized_landmarks[fingertips[j]])
                    finger_spreads.append(dist)
            
            # Take first 5 most important spreads
            finger_spreads.sort(reverse=True)
            features.extend(finger_spreads[:5])
        
        return np.array(features)
    
    def predict_single_frame(self, landmarks) -> Optional[Dict[str, Any]]:
        """
        Predict gesture from a single frame of hand landmarks
        Returns prediction with confidence score
        """
        if not self.model_loaded or self.model is None or landmarks is None:
            return None
        
        try:
            # Extract geometric features
            features = self.extract_geometric_features(landmarks)
            if features is None:
                return None
            
            # Scale features
            features_scaled = self.scaler.transform([features])
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(features_scaled)[0]
            predicted_class = np.argmax(probabilities)
            confidence = float(probabilities[predicted_class])
            
            # Check confidence threshold
            if confidence < self.confidence_threshold:
                return None
            
            gesture_name = self.idx_to_word.get(predicted_class, "Unknown")
            
            return {
                'gesture': gesture_name,
                'confidence': confidence,
                'probabilities': {
                    self.idx_to_word.get(i, f"class_{i}"): float(prob) 
                    for i, prob in enumerate(probabilities)
                }
            }
            
        except Exception as e:
            print(f"Static classifier prediction error: {e}")
            return None
    
    def predict(self, landmarks):
        """Compatibility method for existing pipeline"""
        return self.predict_single_frame(landmarks)
    
    def set_confidence_threshold(self, threshold: float):
        """Adjust confidence threshold for predictions"""
        self.confidence_threshold = max(0.1, min(0.95, threshold))
        print(f"Confidence threshold set to: {self.confidence_threshold}")

# Create aliases for compatibility
EnhancedStaticASLClassifier = StaticASLClassifier
ASLStaticClassifier = StaticASLClassifier