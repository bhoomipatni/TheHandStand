from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Bidirectional
from tensorflow.keras.optimizers import Adam
import sys
from pathlib import Path

parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))
import config
Config = config.Config

def create_model(num_classes, sequence_length=None):
    """Create LSTM model for sign language recognition"""
    model = Sequential([
        Bidirectional(LSTM(Config.LSTM_UNITS, return_sequences=True, activation='relu'),
                     input_shape=(None, Config.NUM_KEYPOINTS)),
        Dropout(Config.DROPOUT_RATE),
        Bidirectional(LSTM(Config.LSTM_UNITS, return_sequences=False, activation='relu')),
        Dropout(Config.DROPOUT_RATE),
        Dense(128, activation='relu'),
        Dropout(Config.DROPOUT_RATE),
        Dense(64, activation='relu'),
        Dense(num_classes, activation='softmax')
    ])
    
    model.compile(
        optimizer=Adam(learning_rate=Config.LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['categorical_accuracy']
    )
    
    return model