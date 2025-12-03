FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    espeak-ng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download Piper binary
RUN wget https://github.com/rhasspy/piper/releases/download/v1.2.0/piper_amd64.tar.gz \
    && tar -xvf piper_amd64.tar.gz \
    && rm piper_amd64.tar.gz \
    && chmod +x piper/piper

# Copy application
COPY . .

EXPOSE 8002

HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8002/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8002"]