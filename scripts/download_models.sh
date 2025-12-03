#!/bin/bash

# Download AI Models Script

set -e

echo "🧠 Downloading AI Models"
echo "======================"
echo ""

# Create directories
mkdir -p models/whisper
mkdir -p models/piper
mkdir -p models/yolo

cd models

# Download YOLO
echo "Downloading YOLOv8 nano model..."
cd yolo
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
echo "✅ YOLOv8 downloaded"
cd ..

# Whisper models (require manual download or API)
echo ""
echo "ℹ️ Whisper models:"
echo "   Download from: https://huggingface.co/ggerganov/whisper.cpp"
echo "   Place in: models/whisper/"

# Piper voices
echo ""
echo "ℹ️ Piper TTS voices:"
echo "   Download from: https://github.com/rhasspy/piper/releases"
echo "   Place in: models/piper/"

echo ""
echo "✅ Model download complete!"
echo ""
echo "Don't forget to download Whisper and Piper models manually."