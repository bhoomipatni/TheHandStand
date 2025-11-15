#!/bin/bash

# Directory paths
RAW_VIDEOS_DIR="data/raw"
PROCESSED_KEYPOINTS_DIR="data/processed/keypoints"
VIDEO_EXTENSIONS=("mp4" "avi" "mov")

# Create processed keypoints directory if it doesn't exist
mkdir -p $PROCESSED_KEYPOINTS_DIR

# Loop through each video in the raw directory
for video in "$RAW_VIDEOS_DIR"/*; do
    # Check if the file is a video
    if [[ -f "$video" ]]; then
        # Get the video filename without extension
        filename=$(basename -- "$video")
        filename_no_ext="${filename%.*}"

        # Extract keypoints using the keypoint extractor script
        python src/extractor/keypoint_extractor.py --input "$video" --output "$PROCESSED_KEYPOINTS_DIR/$filename_no_ext.json"
    fi
done

echo "Keypoint extraction completed."