from pathlib import Path

class Config:
    # Paths - point to SignLanguageTranslator folder structure
    BASE_DIR = Path(__file__).parent.parent.parent  # Goes to SignLanguageTranslator
    DATA_PATH = BASE_DIR / "data"
    RAW_DATA_PATH = DATA_PATH / "raw" / "wlasl"
    PROCESSED_DATA_PATH = DATA_PATH / "processed" / "keypoints"
    MODELS_PATH = DATA_PATH / "models" / "saved_models"
    LABELS_PATH = DATA_PATH / "labels.json"
    
    # Model parameters
    SEQUENCE_LENGTH = 30  # Number of frames to collect before prediction
    NUM_KEYPOINTS = 126   # 21 landmarks * 3 coords * 2 hands
    LSTM_UNITS = 128
    DROPOUT_RATE = 0.5
    LEARNING_RATE = 0.001
    BATCH_SIZE = 32
    EPOCHS = 50
    
    # Inference
    CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence for prediction