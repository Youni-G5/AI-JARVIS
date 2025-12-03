# AI-JARVIS Installation Guide

## Prerequisites

### Required
- **Docker** 24.0+
- **Docker Compose** 2.20+
- **Git**
- **8GB RAM** minimum (16GB recommended)
- **20GB free disk space**

### Optional
- **NVIDIA GPU** with CUDA support (for faster inference)
- **Webcam** (for vision features)
- **Microphone** (for voice input)

---

## Quick Start (Docker)

### 1. Clone Repository

```bash
git clone https://github.com/Youni-G5/AI-JARVIS.git
cd AI-JARVIS
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit configuration (optional)
nano .env
```

### 3. Start Services

```bash
# Build all containers
make build

# Start all services
make up

# View logs
make logs
```

### 4. Access Dashboard

Open your browser to: **http://localhost:3000**

---

## Manual Installation (Development)

### 1. Install Python Dependencies

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install orchestrator dependencies
cd apps/orchestrator_core
pip install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
cd frontend
npm install
```

### 3. Start Services Manually

```bash
# Terminal 1: Start orchestrator
cd apps/orchestrator_core
uvicorn main:app --reload

# Terminal 2: Start frontend
cd frontend
npm run dev
```

---

## Download AI Models

### Whisper (STT)

```bash
mkdir -p models/whisper
cd models/whisper
# Download from OpenAI or Hugging Face
```

### YOLOv8 (Vision)

```bash
mkdir -p models/yolo
cd models/yolo
wget https://github.com/ultralytics/assets/releases/download/v0.0.0/yolov8n.pt
```

### Ollama Models

```bash
# Pull Llama 3.2 model
docker exec jarvis_ollama ollama pull llama3.2:latest

# Alternative: Mistral
docker exec jarvis_ollama ollama pull mistral:latest
```

---

## GPU Support (NVIDIA)

### 1. Install NVIDIA Container Toolkit

```bash
# Ubuntu/Debian
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
sudo systemctl restart docker
```

### 2. Enable GPU in Docker Compose

Uncomment GPU sections in `docker-compose.yml`

---

## Verification

### Check Service Health

```bash
make health

# Or manually
curl http://localhost:8000/health
curl http://localhost:3000
```

### View Container Status

```bash
make ps
```

---

## Troubleshooting

### Services Won't Start

```bash
# Check logs
docker-compose logs orchestrator

# Restart specific service
docker-compose restart orchestrator
```

### Out of Memory

Increase Docker memory limit in Docker Desktop settings (8GB minimum)

### Port Already in Use

Change port mappings in `docker-compose.yml` or `.env`

---

## Next Steps

- Read [Architecture Documentation](Architecture.md)
- Configure [Security Settings](Security.md)
- Explore [API Documentation](API.md)
- Join the community on GitHub Discussions