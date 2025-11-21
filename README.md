# The HandStand

A real-time American Sign Language (ASL) translation system built for hackathons and educational purposes. This project combines computer vision, machine learning, and natural language processing to translate ASL finger spelling into text and speech in multiple languages.

## 🎯 Project Overview

SignSpeak AI captures hand gestures through a camera, recognizes ASL letters using MediaPipe and machine learning models, builds words and sentences from detected letters, and provides real-time translation and text-to-speech output. The system is designed to be accessible, fast, and user-friendly for both ASL users and learners.

## 🏗️ Project Structure

```
SignSpeak AI/
├── app.py                 # Main Flask application entry point
├── backend/               # Core processing modules
│   ├── hand_tracking.py   # MediaPipe hand detection and landmark extraction
│   ├── classifier.py      # ASL letter classification using ML models
│   ├── word_builder.py    # Letter-to-word-to-sentence logic
│   ├── translator.py      # Multi-language translation via Gemini API
│   └── speech.py          # Text-to-speech using ElevenLabs/Google TTS
├── frontend/              # User interface components
│   ├── templates/        # Flask HTML templates (alternative UI)
│   └── static/           # CSS, JavaScript, images
├── models/               # Pre-trained ASL recognition models
├── data/                 # Training/testing datasets
├── utils/                # Helper functions and configuration
├── tests/                # Unit tests for core modules
└── requirements.txt      # Python dependencies
```

## 🚀 Features

- **Real-time ASL Recognition**: Live camera feed processing with MediaPipe
- **Multi-language Translation**: Support for Spanish, French, German, Italian, Portuguese, and more
- **Text-to-Speech**: High-quality voice synthesis using ElevenLabs or Google TTS
- **User-friendly Interface**: Clean web interface with live feedback
- **Modular Architecture**: Easy to extend and customize for different use cases
- **Cross-platform**: Works on Windows, macOS, and Linux

## 🔧 Technologies Used

- **Computer Vision**: MediaPipe, OpenCV
- **Machine Learning**: scikit-learn, TensorFlow/Keras
- **Translation**: Google Gemini API
- **Text-to-Speech**: ElevenLabs API, Google TTS
- **Language**: Python 3.8+

## 📋 Setup Requirements

1. Python 3.8 or higher
2. Webcam for real-time gesture capture
3. API keys for Gemini (translation) and ElevenLabs (speech synthesis)
4. Pre-trained ASL classification model (to be trained or downloaded)

This project is designed for rapid development and demonstration, making it perfect for hackathons, educational workshops, and accessibility initiatives.
