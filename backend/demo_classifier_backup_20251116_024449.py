"""
Demo-Ready Enhanced ASL Classifier with Smoothing
"""

import numpy as np
import json
import os
from typing import Optional, Dict, Any
from collections import deque
import tensorflow as tf

class DemoASLClassifier:
    def __init__(self):
        """Initialize with demo-optimized model"""
        self.model = None
        self.labels_map = {}
        self.idx_to_word = {}
        self.sequence_buffer = deque(maxlen=30)
        
        # Smoothing buffers
        self.prediction_history = deque(maxlen=10)  # Last 10 predictions
        self.confidence_history = deque(maxlen=10)
        
        # Demo parameters
        self.confidence_threshold = 0.22
        self.smoothing_threshold = 0.6  # 60% of recent predictions should agree
        
        # Load model
        self.load_demo_model()

    def load_demo_model(self):
        """Load the demo-optimized model"""
        try:
            # Load labels
            with open("data/labels.json", "r") as f:
                self.labels_map = json.load(f)
                self.idx_to_word = {v: k for k, v in self.labels_map.items()}
            
            # Try to load demo model, fall back to simple model
            demo_model_path = "data/models/saved_models/demo_model.h5"
            simple_model_path = "data/models/saved_models/simple_model.h5"
            
            if os.path.exists(demo_model_path):
                self.model = tf.keras.models.load_model(demo_model_path)
                print(f"Demo classifier loaded: {list(self.labels_map.keys())}")
            elif os.path.exists(simple_model_path):
                self.model = tf.keras.models.load_model(simple_model_path)
                print(f"Simple classifier loaded: {list(self.labels_map.keys())}")
            else:
                print("No model found!")
                return False
                
            return True
        except Exception as e:
            print(f"Failed to load demo model: {e}")
            return False

    def predict_single_frame(self, landmarks) -> Optional[Dict[str, Any]]:
        """Predict gesture with smoothing for demo stability"""
        if self.model is None or landmarks is None:
            return None
            
        try:
            # Handle different input formats
            if len(landmarks) == 126:
                keypoints = np.array(landmarks)
            elif len(landmarks) == 42:
                # Convert 42-feature to 126-feature
                keypoints = np.zeros(126)
                landmarks_xy = np.array(landmarks).reshape(21, 2)
                for i in range(21):
                    # First hand
                    keypoints[i*3] = landmarks_xy[i, 0]
                    keypoints[i*3 + 1] = landmarks_xy[i, 1]
                    keypoints[i*3 + 2] = 0.0
                    # Second hand (copy)
                    keypoints[63 + i*3] = landmarks_xy[i, 0]
                    keypoints[63 + i*3 + 1] = landmarks_xy[i, 1]
                    keypoints[63 + i*3 + 2] = 0.0
            else:
                print(f"Warning: Unexpected landmark format: {len(landmarks)}")
                return None
            
            # Add to sequence buffer
            self.sequence_buffer.append(keypoints)
            
            # Reduced requirement for faster response: 5 frames instead of 30
            if len(self.sequence_buffer) < 5:
                print(f"Building sequence: {len(self.sequence_buffer)}/5 frames")
                return None
            
            # For faster prediction, duplicate the sequence to reach model requirement
            sequence = np.array(list(self.sequence_buffer))
            # Repeat the sequence to reach 30 frames
            while len(sequence) < 30:
                sequence = np.vstack([sequence, sequence[-1]])
            
            # Take last 30 frames
            sequence = sequence[-30:]
            sequence = np.expand_dims(sequence, axis=0)
            
            # Make prediction
            predictions = self.model.predict(sequence, verbose=0)
            predicted_class = np.argmax(predictions[0])
            confidence = float(predictions[0][predicted_class])
            
            print(f"Demo debug: Raw prediction: {self.idx_to_word.get(predicted_class)} ({confidence:.3f})")
            print(f"Demo debug: All confidences: {[f'{p:.3f}' for p in predictions[0]]}")
            
            # Basic confidence check
            if confidence < self.confidence_threshold:
                print(f"Demo debug: Confidence too low ({confidence:.3f} < {self.confidence_threshold})")
                return None
            
            # Add to prediction history
            self.prediction_history.append(predicted_class)
            self.confidence_history.append(confidence)
            
            # Apply smoothing if we have enough history
            if len(self.prediction_history) >= 5:
                smoothed_result = self.apply_smoothing()
                if smoothed_result:
                    return smoothed_result
            
            # If no smoothed result, use current prediction if confidence is high
            if confidence > 0.35:  # High confidence threshold for immediate response
                gesture_name = self.idx_to_word.get(predicted_class, "Unknown")
                print(f"Demo debug: High confidence prediction: {gesture_name} ({confidence:.3f})")
                return {
                    "gesture": gesture_name,
                    "confidence": confidence,
                    "success": True
                }
            
            return None
            
        except Exception as e:
            print(f"Demo prediction error: {e}")
            return None

    def apply_smoothing(self) -> Optional[Dict[str, Any]]:
        """Apply temporal smoothing for stable predictions"""
        if len(self.prediction_history) < 5:
            return None
        
        # Get recent predictions
        recent_predictions = list(self.prediction_history)[-7:]  # Last 7 predictions
        recent_confidences = list(self.confidence_history)[-7:]
        
        # Count occurrences of each prediction
        prediction_counts = {}
        confidence_sums = {}
        
        for pred, conf in zip(recent_predictions, recent_confidences):
            if pred not in prediction_counts:
                prediction_counts[pred] = 0
                confidence_sums[pred] = 0.0
            prediction_counts[pred] += 1
            confidence_sums[pred] += conf
        
        # Find the most common prediction
        most_common_pred = max(prediction_counts.items(), key=lambda x: x[1])
        pred_class, pred_count = most_common_pred
        
        # Calculate agreement ratio
        agreement_ratio = pred_count / len(recent_predictions)
        avg_confidence = confidence_sums[pred_class] / pred_count
        
        print(f"Demo debug: Smoothing - {self.idx_to_word.get(pred_class)} appears {pred_count}/{len(recent_predictions)} times")
        print(f"Demo debug: Agreement ratio: {agreement_ratio:.2f}, Avg confidence: {avg_confidence:.3f}")
        
        # Check if prediction is stable enough
        if agreement_ratio >= self.smoothing_threshold and avg_confidence > 0.25:
            gesture_name = self.idx_to_word.get(pred_class, "Unknown")
            
            print(f"Demo debug: SMOOTHED PREDICTION: {gesture_name} (agreement: {agreement_ratio:.2f}, conf: {avg_confidence:.3f})")
            
            return {
                "gesture": gesture_name,
                "confidence": avg_confidence,
                "success": True,
                "smoothed": True
            }
        
        return None

    def reset_buffers(self):
        """Reset all buffers - useful between gestures"""
        self.sequence_buffer.clear()
        self.prediction_history.clear()
        self.confidence_history.clear()
        print("Demo debug: Buffers reset")

# Compatibility wrapper
class EnhancedASLClassifier(DemoASLClassifier):
    def predict_single_frame(self, landmarks):
        return super().predict_single_frame(landmarks)

# Legacy wrapper    
class ASLClassifier(DemoASLClassifier):
    def predict(self, landmarks_sequence):
        if landmarks_sequence:
            return self.predict_single_frame(landmarks_sequence[-1])
        return None