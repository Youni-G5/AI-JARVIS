#!/bin/bash

# AI-JARVIS Setup Script

set -e

echo "🤖 AI-JARVIS Setup"
echo "=================="
echo ""

# Check prerequisites
echo "Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Please install Docker Compose first."
    exit 1
fi

echo "✅ Docker found"
echo "✅ Docker Compose found"
echo ""

# Create directories
echo "Creating directories..."
mkdir -p models/whisper
mkdir -p models/piper
mkdir -p models/yolo
mkdir -p logs
mkdir -p sandbox

echo "✅ Directories created"
echo ""

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "✅ .env created (please edit with your configuration)"
else
    echo "ℹ️ .env already exists"
fi
echo ""

# Download models (optional)
read -p "Download AI models now? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Downloading YOLO model..."
    cd models/yolo
    wget -q https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
    cd ../..
    echo "✅ YOLO model downloaded"
fi
echo ""

# Build containers
echo "Building Docker containers..."
make build

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Run 'make up' to start services"
echo "3. Access dashboard at http://localhost:3000"
echo ""
echo "For more information, see docs/Installation.md"