"""
Hand Tracking Module using MediaPipe and OpenCV
"""

import cv2
import mediapipe as mp
import numpy as np

class HandTracker:
    def __init__(self):
        """Initialize MediaPipe hand tracking pipeline"""
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,  # Track both hands
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
    def detect_hands(self, frame):
        """Detect hands in the given frame and return landmarks in 126-feature format"""
        if frame is None:
            return None
            
        try:
            # Convert BGR to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Process the frame
            results = self.hands.process(rgb_frame)
            
            # Initialize 126 features (21 landmarks * 2 hands * 3 coordinates)
            landmarks = np.zeros(126)
            
            if results.multi_hand_landmarks:
                # Process detected hands (up to 2)
                for hand_idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    if hand_idx >= 2:  # Only process first 2 hands
                        break
                        
                    # Extract x,y,z coordinates for all 21 landmarks
                    start_idx = hand_idx * 63  # 63 features per hand
                    
                    for landmark_idx, landmark in enumerate(hand_landmarks.landmark):
                        base_idx = start_idx + landmark_idx * 3
                        landmarks[base_idx] = landmark.x      # x coordinate
                        landmarks[base_idx + 1] = landmark.y  # y coordinate  
                        landmarks[base_idx + 2] = landmark.z  # z coordinate (depth)
                
                return landmarks.tolist()
            else:
                return None
                
        except Exception as e:
            print(f"Error in hand detection: {e}")
            return None