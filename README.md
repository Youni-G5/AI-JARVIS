# 🤖 AI-JARVIS

**Production-grade autonomous AI assistant with voice, vision, LLM, and system automation capabilities**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

## 🎯 Overview

AI-JARVIS is a modular, local-first intelligent assistant capable of:

- 🎤 **Voice Input** - Real-time speech-to-text via Whisper
- 🧠 **AI Reasoning** - Local LLM inference with Ollama/llama.cpp
- 🗣️ **Voice Output** - Natural TTS with Piper
- 👁️ **Computer Vision** - Object detection, OCR, scene analysis (YOLOv8)
- ⚡ **System Actions** - Secure OS automation with sandboxing
- 🏠 **IoT Control** - MQTT-based home automation
- 🧩 **Memory System** - Vector-based contextual memory (ChromaDB)
- 🎨 **Modern UI** - Real-time Next.js dashboard

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js)                       │
└───────────────────────┬─────────────────────────────────────┘
                        │ WebSocket + REST
┌───────────────────────▼─────────────────────────────────────┐
│              Orchestrator Core (Python)                      │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Planning Engine → Action Validation → Execution     │  │
│  └──────────────────────────────────────────────────────┘  │
└───┬────┬────┬────┬────┬────┬────┬─────────────────────────┘
    │    │    │    │    │    │    │
┌───▼──┐ │ ┌──▼─┐ │ ┌──▼─┐ │ ┌───▼────┐  ┌──────────┐
│ STT  │ │ │TTS │ │ │LLM │ │ │Vision  │  │  Memory  │
│Whisper│ │Piper│ │Ollama│ │ YOLOv8 │  │ ChromaDB │
└──────┘ │ └────┘ │ └────┘ │ └────────┘  └──────────┘
         │        │        │
      ┌──▼────┐   │   ┌───▼────────┐
      │Action │   │   │ Bridge API │
      │Executor│  │   └────────────┘
      └───────┘   │
                  ▼
           [OS / IoT / MQTT]
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- Node.js 18+
- NVIDIA GPU (optional, for faster inference)

### Installation

```bash
# Clone the repository
git clone https://github.com/Youni-G5/AI-JARVIS.git
cd AI-JARVIS

# Copy environment file
cp .env.example .env

# Build and start all services
make build
make up

# Access the dashboard
open http://localhost:3000
```

## 📚 Documentation

- [Architecture Overview](docs/Architecture.md)
- [API Documentation](docs/API.md)
- [Installation Guide](docs/Installation.md)
- [Security Policy](docs/Security.md)

## 🧪 Testing

```bash
make test
make coverage
```

## 🔒 Security Features

- 🛡️ **Sandboxed Execution** - All OS actions run in isolated environment
- ✅ **Action Validation** - Multi-layer permission checks
- 📝 **Audit Logging** - Complete action history
- 🚫 **Dry-run Mode** - Test actions without execution

## 📄 License

MIT License - see LICENSE file for details.

---

**Made with ❤️ for the AI community**