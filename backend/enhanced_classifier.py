"""
Simple Enhanced ASL Classifier using teammate's LSTM model
"""

import numpy as np
import json
import os
from typing import Optional, Dict, Any
from collections import deque
import tensorflow as tf

class EnhancedASLClassifier:
    def __init__(self):
        """Initialize with teammate's LSTM model"""
        self.model = None
        self.labels_map = {}
        self.idx_to_word = {}
        self.sequence_buffer = deque(maxlen=30)
        
        # Load teammate's model and labels
        self.load_model()

    def load_model(self):
        """Load the LSTM model and gesture labels"""
        try:
            # Load labels
            with open("data/labels.json", "r") as f:
                self.labels_map = json.load(f)
                self.idx_to_word = {v: k for k, v in self.labels_map.items()}
            
            # Load LSTM model
            self.model = tf.keras.models.load_model("data/models/saved_models/simple_model.h5")
            print(f"✅ Enhanced classifier loaded: {list(self.labels_map.keys())}")
            return True
        except Exception as e:
            print(f"Failed to load enhanced model: {e}")
            return False

    def predict_single_frame(self, landmarks) -> Optional[Dict[str, Any]]:
        """Predict gesture using LSTM model"""
        if self.model is None or landmarks is None:
            return None
            
        try:
            # Handle both 42-feature (old) and 126-feature (new) formats
            if len(landmarks) == 126:
                # New format: already has 126 features
                keypoints = np.array(landmarks)
            elif len(landmarks) == 42:
                # Old format: convert x,y for 21 points to 126 features
                keypoints = np.zeros(126)
                for i in range(0, 42, 2):
                    idx = i // 2
                    keypoints[idx * 3] = landmarks[i]      # x
                    keypoints[idx * 3 + 1] = landmarks[i + 1]  # y
                    keypoints[idx * 3 + 2] = 0.0           # z
            else:
                print(f"Classifier debug: Invalid landmarks length: {len(landmarks)}")
                return None
            
            # Add to sequence buffer
            self.sequence_buffer.append(keypoints)
            print(f"Classifier debug: Buffer has {len(self.sequence_buffer)} frames")
            
            # Very low threshold for testing
            if len(self.sequence_buffer) < 5:
                print(f"Classifier debug: Need more frames, have {len(self.sequence_buffer)}/5")
                return None
            
            # Prepare sequence (use last 30 frames, pad if needed)
            sequence = np.array(list(self.sequence_buffer))
            if len(sequence) < 30:
                padding = np.tile(sequence[-1], (30 - len(sequence), 1))
                sequence = np.vstack([sequence, padding])
            else:
                sequence = sequence[-30:]
            
            # Make prediction
            sequence = np.expand_dims(sequence, axis=0)
            predictions = self.model.predict(sequence, verbose=0)
            
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            print(f"Classifier debug: Predicted {predicted_class} with confidence {confidence}")
            print(f"Classifier debug: All predictions: {predictions[0]}")
            
            # Get top 2 predictions to check if they're close
            top_2_indices = np.argsort(predictions[0])[-2:]
            top_1_conf = float(predictions[0][top_2_indices[1]])
            top_2_conf = float(predictions[0][top_2_indices[0]])
            
            print(f"Classifier debug: Top prediction: {self.idx_to_word.get(top_2_indices[1])} ({top_1_conf:.3f})")
            print(f"Classifier debug: Second prediction: {self.idx_to_word.get(top_2_indices[0])} ({top_2_conf:.3f})")
            
            # Simple prediction logic with adjusted thresholds
            print(f"Classifier debug: Original prediction: {self.idx_to_word.get(predicted_class)} ({confidence:.3f})")
            
            # Lower confidence threshold for better responsiveness
            confidence_threshold = 0.25  # Lowered from 0.4
            if confidence < confidence_threshold:
                print(f"Classifier debug: Confidence too low ({confidence:.3f} < {confidence_threshold})")
                return None
            
            # Check if the top prediction is significantly better than others
            sorted_indices = np.argsort(predictions[0])[::-1]
            top_1_conf = predictions[0][sorted_indices[0]]
            top_2_conf = predictions[0][sorted_indices[1]] if len(sorted_indices) > 1 else 0
            
            # Require clear winner but with more lenient threshold
            if top_1_conf - top_2_conf < 0.05:  # Lowered from 0.15
                print(f"Classifier debug: Predictions too close ({top_1_conf:.3f} vs {top_2_conf:.3f})")
                return None
            
            # Use the original prediction
            gesture_name = self.idx_to_word.get(predicted_class, "Unknown")
            final_confidence = confidence
            
            print(f"Classifier debug: Returning gesture: {gesture_name} (confidence: {final_confidence:.3f})")
            return {
                "gesture": gesture_name,
                "confidence": final_confidence,
                "success": True
            }
            
        except Exception as e:
            print(f"Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return None

# Compatibility wrapper
class ASLClassifier(EnhancedASLClassifier):
    def predict(self, landmarks_sequence):
        if landmarks_sequence:
            return self.predict_single_frame(landmarks_sequence[-1])
        return None