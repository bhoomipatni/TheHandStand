#!/bin/bash

# Create directories for raw videos, processed keypoints, and skeletons
mkdir -p data/raw
mkdir -p data/videos
mkdir -p data/processed/keypoints
mkdir -p data/processed/skeletons

# Download videos from specified sources
# Example: Replace with actual download commands or scripts
echo "Downloading videos..."
# Add your video downloading commands here, e.g., using youtube-dl or yt-dlp
# yt-dlp -o "data/raw/%(title)s.%(ext)s" <video_url>

echo "Videos downloaded to data/raw."