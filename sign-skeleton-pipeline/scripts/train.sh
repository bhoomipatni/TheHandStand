#!/bin/bash

# Navigate to the project directory
cd "$(dirname "$0")/.."

# Activate the virtual environment if needed
# source venv/bin/activate

# Set paths
DATA_DIR="./data/processed"
KEYPOINTS_DIR="$DATA_DIR/keypoints"
SKELETONS_DIR="$DATA_DIR/skeletons"

# Create directories if they do not exist
mkdir -p "$KEYPOINTS_DIR"
mkdir -p "$SKELETONS_DIR"

# Run the keypoint extraction script
echo "Extracting keypoints..."
bash scripts/extract_keypoints.sh

# Run the training script
echo "Starting training on skeleton sequences..."
python src/train/train.py --keypoints_dir="$KEYPOINTS_DIR" --skeletons_dir="$SKELETONS_DIR"

echo "Training completed."