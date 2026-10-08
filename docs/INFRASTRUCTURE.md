# Infrastructure Guide - Hermes Agent

This guide provides the complete setup requirements and operational instructions for running Hermes Agent in development, testing, and production environments.

---

## 1. System Requirements

### 1.1 Supported Operating Systems

- Linux (recommended): Ubuntu 20.04+ / Debian 11+
- macOS: 11 Big Sur or newer
- Windows: Recommended to use WSL2 for local development

### 1.2 Minimum Hardware Requirements

| Component | Minimum | Recommended | Production |
| --- | --- | --- | --- |
| CPU | 4 cores | 8 cores | 16+ cores |
| RAM | 8 GB | 16 GB | 32 GB+ |
| Storage | 50 GB | 100 GB | 500 GB+ |
| GPU | Optional | NVIDIA 8GB+ | NVIDIA 24GB+ |

### 1.3 Required Software

- Python 3.10+ (recommended 3.11 or 3.12)
- Git
- pip
- Docker (optional, recommended for containerized deployment)
- CUDA 11.8+ and cuDNN 8.6+ for NVIDIA GPU acceleration (optional)

---

## 2. Repository Setup

### 2.1 Clone the Project

```bash
git clone https://github.com/ahmedmokireldinonline/hermes-agent.git
cd hermes-agent
```

### 2.2 Create a Virtual Environment

```bash
# Linux / macOS
python3 -m venv venv
source venv/bin/activate

# Windows (PowerShell)
python -m venv venv
venv\Scripts\Activate.ps1
```

### 2.3 Install Dependencies

```bash
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
```

If GPU support is required:

```bash
pip install -r requirements-gpu.txt
```

For development/testing tools:

```bash
pip install -r requirements-dev.txt
```

---

## 3. Environment Configuration

Create a local env file:

```bash
cp .env.example .env
```

Then edit the file with your values:

```env
HOST=0.0.0.0
PORT=8000
DATABASE_URL=sqlite:///./hermes.db
OPENAI_API_KEY=your_key_here
HUGGING_FACE_TOKEN=your_token_here
ANTHROPIC_API_KEY=your_key_here
USE_GPU=false
GPU_ID=0
LOG_LEVEL=INFO
LOG_FILE=logs/hermes.log
SECRET_KEY=your_secret_key
```

---

## 4. Database Configuration

### SQLite (Default for Local Development)

```bash
python -m hermes.cli init-db
```

### PostgreSQL (Recommended for Production)

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create role and database
createdb hermes_db
createuser hermes_user -P

# Update DATABASE_URL in .env
DATABASE_URL=postgresql://hermes_user:password@localhost:5432/hermes_db

# Run migrations
alembic upgrade head
```

---

## 5. Run the Application

### Development Mode

```bash
python -m uvicorn hermes.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode

```bash
gunicorn hermes.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000
```

---

## 6. Docker Setup

### Build Image

```bash
docker build -t hermes-agent:latest .
```

### Run Container

```bash
docker run -p 8000:8000 hermes-agent:latest
```

### Docker Compose Example

```yaml
version: '3.9'

services:
  hermes:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=sqlite:///./hermes.db
      - HUGGING_FACE_TOKEN=${HUGGING_FACE_TOKEN}
    restart: unless-stopped
```

---

## 7. External Services

Hermes Agent may integrate with different providers:

| Service | Variable | Notes |
| --- | --- | --- |
| Hugging Face | `HUGGING_FACE_TOKEN` | Required for model downloads and hosting integrations |
| OpenAI | `OPENAI_API_KEY` | Optional |
| Anthropic | `ANTHROPIC_API_KEY` | Optional |
| Google | `GOOGLE_API_KEY` | Optional |

---

## 8. Monitoring and Logging

Logs should be written to a file and console for production debugging.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/hermes.log'),
        logging.StreamHandler()
    ]
)
```

---

## 9. Troubleshooting

### Import Errors

```bash
pip install --upgrade pip
pip install --force-reinstall -r requirements.txt
```

### Database Errors

```bash
python -m hermes.cli check-db
python -m hermes.cli reset-db --confirm
```

### GPU Not Detected

```bash
nvidia-smi
python -c "import torch; print(torch.cuda.is_available())"
```

### API Key Issues

Check `HUGGING_FACE_TOKEN`, `OPENAI_API_KEY`, and other variables in `.env` and verify they are valid.

---

## 10. Security Best Practices

- Keep `.env` out of version control.
- Use a strong `SECRET_KEY`.
- Restrict public ports in production.
- Use a reverse proxy such as Nginx with TLS.
- Rotate API keys regularly.

---

## 11. Performance Recommendations

- Use PostgreSQL for production workloads.
- Enable Redis for caching if needed.
- Run with multiple workers in production.
- Use GPU only for large model inference workloads.

---

## 12. Support

- GitHub Repo: https://github.com/ahmedmokireldinonline/hermes-agent
- Issues: https://github.com/ahmedmokireldinonline/hermes-agent/issues

---

This document is intended as a practical deployment guide for Hermes Agent. Adjust the setup based on your deployment environment and model requirements.
