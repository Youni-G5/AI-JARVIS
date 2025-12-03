# AI-JARVIS Verification Checklist

🎯 **Use this checklist to verify your AI-JARVIS installation is complete and functional.**

---

## Phase 1: Repository Verification 📋

### File Structure Check

Verify all essential files exist:

```bash
# Core services
[ ] apps/orchestrator_core/main.py
[ ] apps/orchestrator_core/core/orchestrator.py
[ ] apps/orchestrator_core/core/planning.py
[ ] apps/orchestrator_core/core/safety.py
[ ] apps/orchestrator_core/core/executor.py
[ ] apps/orchestrator_core/core/config.py
[ ] apps/orchestrator_core/core/logger.py

# Microservices
[ ] apps/stt_service/main.py
[ ] apps/tts_service/main.py
[ ] apps/llm_agent/main.py
[ ] apps/vision_service/main.py
[ ] apps/action_executor/main.py
[ ] apps/bridge_api/main.py

# Service clients
[ ] apps/orchestrator_core/services/llm_client.py
[ ] apps/orchestrator_core/services/memory_client.py
[ ] apps/orchestrator_core/services/action_client.py

# API routes
[ ] apps/orchestrator_core/api/health.py
[ ] apps/orchestrator_core/api/actions.py
[ ] apps/orchestrator_core/api/memory.py
[ ] apps/orchestrator_core/api/websocket.py

# Infrastructure
[ ] docker-compose.yml
[ ] Makefile
[ ] .env.example
[ ] .gitignore

# Prompts
[ ] prompts/system_orchestrator.txt
[ ] prompts/permissions.yml

# Documentation
[ ] README.md
[ ] docs/Architecture.md
[ ] docs/Installation.md
[ ] docs/Security.md
[ ] docs/ROADMAP.md
[ ] docs/CODE_AUDIT.md
[ ] CONTRIBUTING.md
[ ] CHANGELOG.md
[ ] LICENSE

# CI/CD
[ ] .github/workflows/ci.yml
[ ] .github/workflows/cd.yml
[ ] .github/workflows/security.yml

# Tests
[ ] tests/test_orchestrator.py
[ ] tests/conftest.py
[ ] pytest.ini

# Scripts
[ ] scripts/setup.sh
[ ] scripts/download_models.sh

# Frontend
[ ] frontend/package.json
[ ] frontend/Dockerfile
[ ] frontend/pages/_app.tsx
[ ] frontend/pages/index.tsx
[ ] frontend/next.config.js
[ ] frontend/tsconfig.json
```

**Command to check:**
```bash
find . -name "main.py" | grep -E "(orchestrator|stt|tts|llm|vision|executor|bridge)"
# Should return 7 files
```

---

## Phase 2: Code Syntax Verification 🔍

### Python Syntax Check

```bash
# Check all Python files for syntax errors
find apps -name "*.py" -exec python3 -m py_compile {} \;

# Expected output: No errors (silent if successful)
```

### Import Verification

```bash
# Test imports in orchestrator
cd apps/orchestrator_core
python3 -c "from core.orchestrator import JarvisOrchestrator; print('Imports OK')"

# Test service imports
python3 -c "from services.llm_client import LLMClient; print('LLM client OK')"
python3 -c "from services.memory_client import MemoryClient; print('Memory client OK')"
python3 -c "from services.action_client import ActionClient; print('Action client OK')"
```

**Expected Results:**
```
Imports OK
LLM client OK
Memory client OK
Action client OK
```

---

## Phase 3: Docker Build Verification 🐳

### Check Docker Installation

```bash
[ ] docker --version
# Expected: Docker version 24.0+ or higher

[ ] docker-compose --version
# Expected: Docker Compose version 2.0+ or higher
```

### Build Individual Services

Test each service builds successfully:

```bash
# Orchestrator
[ ] docker build -t jarvis-orchestrator ./apps/orchestrator_core

# STT Service
[ ] docker build -t jarvis-stt ./apps/stt_service

# TTS Service
[ ] docker build -t jarvis-tts ./apps/tts_service

# LLM Agent
[ ] docker build -t jarvis-llm ./apps/llm_agent

# Vision Service
[ ] docker build -t jarvis-vision ./apps/vision_service

# Action Executor
[ ] docker build -t jarvis-executor ./apps/action_executor

# Bridge API
[ ] docker build -t jarvis-bridge ./apps/bridge_api

# Frontend
[ ] docker build -t jarvis-frontend ./frontend
```

**Expected:** All builds complete without errors.

### Build All Services with Compose

```bash
[ ] make build
# OR
[ ] docker-compose build
```

**Expected output:**
```
Building orchestrator... done
Building stt_service... done
Building tts_service... done
...
```

---

## Phase 4: Configuration Verification ⚙️

### Environment Variables

```bash
[ ] cp .env.example .env
[ ] nano .env  # Edit with your values
```

**Required variables:**
```bash
[ ] API_HOST=0.0.0.0
[ ] API_PORT=8000
[ ] LLM_MODEL=llama3.2:latest
[ ] POSTGRES_PASSWORD=<your-password>
[ ] REDIS_PASSWORD=<your-password>
```

### Create Required Directories

```bash
[ ] mkdir -p models/whisper
[ ] mkdir -p models/piper
[ ] mkdir -p models/yolo
[ ] mkdir -p logs
[ ] mkdir -p sandbox
```

---

## Phase 5: Service Startup Verification 🚀

### Start All Services

```bash
[ ] make up
# OR
[ ] docker-compose up -d
```

### Check Container Status

```bash
[ ] docker-compose ps
```

**Expected output (all "Up" and "healthy"):**
```
NAME                  STATUS
jarvis_orchestrator   Up (healthy)
jarvis_stt            Up (healthy)
jarvis_tts            Up (healthy)
jarvis_llm            Up (healthy)
jarvis_vision         Up (healthy)
jarvis_executor       Up (healthy)
jarvis_bridge         Up (healthy)
jarvis_frontend       Up (healthy)
jarvis_postgres       Up (healthy)
jarvis_redis          Up (healthy)
jarvis_ollama         Up
jarvis_memory         Up (healthy)
```

### Check Logs

```bash
# View all logs
[ ] make logs

# Check specific service
[ ] docker-compose logs orchestrator
[ ] docker-compose logs stt_service
```

**Look for:**
- ✅ No error messages
- ✅ "Application startup complete"
- ✅ "Lifespan startup complete"
- ✅ "Listening on http://0.0.0.0:8000"

---

## Phase 6: Health Check Verification 🏪

### Test Health Endpoints

```bash
# Orchestrator
[ ] curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# STT Service
[ ] curl http://localhost:8001/health
# Expected: {"status":"healthy"}

# TTS Service
[ ] curl http://localhost:8002/health
# Expected: {"status":"healthy"}

# LLM Agent
[ ] curl http://localhost:8003/health
# Expected: {"status":"healthy","ollama_connected":true}

# Vision Service
[ ] curl http://localhost:8004/health
# Expected: {"status":"healthy","model_loaded":true}

# Action Executor
[ ] curl http://localhost:8006/health
# Expected: {"status":"healthy"}

# Bridge API
[ ] curl http://localhost:8007/health
# Expected: {"status":"healthy","services":{...}}
```

### Automated Health Check

```bash
# Check all services at once
[ ] make health
```

---

## Phase 7: API Functionality Tests 🧪

### Test Orchestrator API

```bash
# Get API info
[ ] curl http://localhost:8000/
# Expected: {"service":"AI-JARVIS Orchestrator Core","version":"1.0.0",...}

# Check API docs
[ ] Open browser: http://localhost:8000/docs
# Expected: FastAPI Swagger UI
```

### Test STT Service

```bash
# Test audio transcription endpoint exists
[ ] curl http://localhost:8001/
# Expected: Service info JSON
```

### Test LLM Agent

```bash
# List available models
[ ] curl http://localhost:8003/models
# Expected: {"models":[...],"current_model":"llama3.2:latest"}
```

### Test Vision Service

```bash
# List available models
[ ] curl http://localhost:8004/models
# Expected: {"available_models":["yolov8n.pt",...],"current_model":"yolov8n.pt"}
```

### Test Action Executor

```bash
# List available actions
[ ] curl http://localhost:8006/actions
# Expected: {"system_actions":[...],"iot_actions":[...]}
```

---

## Phase 8: Integration Tests 🔗

### Test Service Communication

```bash
# Test LLM generation (simple prompt)
curl -X POST http://localhost:8003/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hello, who are you?",
    "temperature": 0.7,
    "max_tokens": 100
  }'

# Expected: {"text":"I am JARVIS...","model":"llama3.2:latest",...}
```

### Test Memory Service

```bash
# Check ChromaDB connection
[ ] curl http://localhost:8005/api/v1/heartbeat
# Expected: {"nanosecond heartbeat": <number>}
```

---

## Phase 9: Frontend Verification 🎨

### Access Dashboard

```bash
# Open in browser
[ ] Open: http://localhost:3000
```

**Expected:**
- ✅ Dashboard loads without errors
- ✅ "AI-JARVIS" title visible
- ✅ Service status cards displayed
- ✅ Connection status shows "Connected"

### Check Browser Console

```
F12 (Developer Tools) > Console
```

**Expected:**
- ✅ No JavaScript errors
- ✅ "Orchestrator health:" log with data

---

## Phase 10: Database Verification 💾

### PostgreSQL Check

```bash
[ ] docker-compose exec postgres psql -U jarvis -d jarvis_db -c "\dt"
# Expected: List of tables (or "No relations" if first run)
```

### Redis Check

```bash
[ ] docker-compose exec redis redis-cli -a changeme PING
# Expected: PONG
```

### ChromaDB Check

```bash
[ ] curl http://localhost:8005/api/v1/collections
# Expected: [] or list of collections
```

---

## Phase 11: Security Verification 🔒

### Check Permissions File

```bash
[ ] cat prompts/permissions.yml
# Verify permission rules are defined
```

### Test Sandbox Mode

```bash
# Check if sandbox is enabled
[ ] grep "ENABLE_SANDBOX" .env
# Expected: ENABLE_SANDBOX=true
```

### Verify No Exposed Secrets

```bash
# Search for hardcoded passwords
[ ] grep -r "password=" apps/ --exclude-dir=node_modules
# Expected: No results (all in .env)
```

---

## Phase 12: Monitoring Verification 📊

### Prometheus Metrics

```bash
# If Prometheus is running
[ ] curl http://localhost:9090/api/v1/status/config
# Expected: Configuration JSON

# Check targets
[ ] Open: http://localhost:9090/targets
# Expected: All targets "UP"
```

### Check Logs Aggregation

```bash
# View logs directory
[ ] ls -la logs/
# Expected: Log files from services
```

---

## Phase 13: Performance Tests ⚡

### Response Time Tests

```bash
# Test orchestrator latency
[ ] time curl http://localhost:8000/health
# Expected: < 100ms

# Test LLM latency
[ ] time curl http://localhost:8003/health
# Expected: < 200ms
```

### Concurrent Requests

```bash
# Use Apache Bench (install: apt-get install apache2-utils)
[ ] ab -n 100 -c 10 http://localhost:8000/health
# Expected: 100% successful requests, low latency
```

---

## Phase 14: Error Handling Tests ⚠️

### Test Invalid Requests

```bash
# Test with invalid JSON
[ ] curl -X POST http://localhost:8003/generate \
     -H "Content-Type: application/json" \
     -d '{invalid json}'
# Expected: 400 Bad Request

# Test with missing parameters
[ ] curl -X POST http://localhost:8003/generate \
     -H "Content-Type: application/json" \
     -d '{}'
# Expected: 422 Unprocessable Entity (validation error)
```

---

## Phase 15: Cleanup & Restart Tests 🔄

### Stop Services

```bash
[ ] make down
# OR
[ ] docker-compose down
```

**Expected:**
- ✅ All containers stopped
- ✅ Network removed

### Restart Services

```bash
[ ] make up
# OR
[ ] docker-compose up -d
```

**Expected:**
- ✅ All services start successfully
- ✅ Data persists (PostgreSQL, ChromaDB)

### Test Data Persistence

```bash
# Add data before restart
# ... (add test data)

# Restart
[ ] make restart

# Verify data still exists
# ... (check data)
```

---

## Final Verification Summary ✅

### Critical Checks (Must Pass)

- [ ] All 12 containers running and healthy
- [ ] All health endpoints return 200 OK
- [ ] No critical errors in logs
- [ ] Frontend loads successfully
- [ ] PostgreSQL connection works
- [ ] Redis connection works
- [ ] ChromaDB connection works
- [ ] API documentation accessible

### Optional Checks (Nice to Have)

- [ ] Prometheus metrics working
- [ ] Load tests passing
- [ ] All integration tests passing
- [ ] No security warnings

---

## Troubleshooting Common Issues 🔧

### Issue: Container unhealthy

```bash
# Check logs
docker-compose logs <service_name>

# Restart specific service
docker-compose restart <service_name>
```

### Issue: Port already in use

```bash
# Find process using port
sudo lsof -i :8000

# Kill process
sudo kill -9 <PID>
```

### Issue: Permission denied

```bash
# Fix Docker permissions
sudo usermod -aG docker $USER
newgrp docker
```

### Issue: Out of disk space

```bash
# Clean Docker resources
docker system prune -a --volumes
```

---

## Success Criteria 🏆

**Your AI-JARVIS installation is VERIFIED when:**

✅ All 12 containers are healthy  
✅ All health checks return 200 OK  
✅ Frontend dashboard loads and connects  
✅ No critical errors in logs  
✅ Database connections work  
✅ API documentation accessible  
✅ Services can communicate  

**🎉 Congratulations! Your AI-JARVIS is fully functional!**

---

## Next Steps After Verification 🚀

1. **Download AI Models**
   ```bash
   bash scripts/download_models.sh
   ```

2. **Test Voice Input**
   - Upload audio to STT endpoint
   - Verify transcription works

3. **Test Vision**
   - Upload image to Vision endpoint
   - Verify object detection works

4. **Create Your First Action**
   - Define custom action in permissions.yml
   - Test execution through orchestrator

5. **Explore API Docs**
   - Visit http://localhost:8000/docs
   - Try interactive API testing

6. **Set Up Monitoring**
   - Configure Prometheus alerts
   - Set up Grafana dashboards

7. **Read Documentation**
   - Review docs/Architecture.md
   - Check docs/Security.md
   - Follow docs/ROADMAP.md

---

**Happy Building! 🤖**