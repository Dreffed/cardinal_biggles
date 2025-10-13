# Cardinal Biggles - Deployment Guide

**Version**: 1.0
**Last Updated**: 2025-01-13

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Configuration Management](#configuration-management)
6. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 1. Prerequisites

### System Requirements

**Development**:
- OS: Linux, macOS, or Windows 10+
- Python: 3.9 or higher
- RAM: 8GB minimum (16GB recommended)
- Disk: 10GB free space
- Network: Internet access for API calls

**Production**:
- OS: Linux (Ubuntu 20.04+ recommended)
- Python: 3.9 or higher
- RAM: 16GB minimum (32GB recommended)
- Disk: 50GB+ SSD
- Network: Stable internet, 100Mbps+

### Software Dependencies

```bash
# Required
python3.9+
pip
git

# Optional (for local LLM)
ollama

# Optional (for development)
docker
docker-compose
```

---

## 2. Local Development Setup

### Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/cardinal-biggles.git
cd cardinal-biggles
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate (Linux/macOS)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install production dependencies
pip install -r requirements.txt

# Install development dependencies (optional)
pip install -r requirements-dev.txt
```

### Step 4: Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit with your API keys
nano .env  # or vim, code, etc.
```

**.env file**:
```bash
# LLM API Keys (optional - only needed if using these providers)
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
PERPLEXITY_API_KEY=pplx-...

# Ollama Configuration (if using local models)
OLLAMA_BASE_URL=http://localhost:11434

# Application Settings
LOG_LEVEL=INFO
OUTPUT_DIRECTORY=./reports
KNOWLEDGE_STORE_PATH=./data/knowledge_store.json
```

### Step 5: Initialize Configuration

```bash
# Create default configuration
python -m cli.main init-config

# Test configuration
python -m cli.main show-config
```

### Step 6: Install Ollama (Optional but Recommended)

```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows - Download from ollama.ai

# Pull a model
ollama pull llama3.1

# Verify
ollama list
```

### Step 7: Run Tests

```bash
# Run all tests
pytest

# Run only unit tests (fast)
pytest -m unit

# Run with coverage
pytest --cov=cardinal_biggles
```

### Step 8: Test the Application

```bash
# Simple test
python -m cli.main research "AI trends 2025" --output test_report.md

# Check output
cat test_report.md
```

---

## 3. Production Deployment

### 3.1 Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.9+
sudo apt install python3.9 python3.9-venv python3-pip -y

# Install system dependencies
sudo apt install git build-essential -y

# Create application user
sudo useradd -m -s /bin/bash cardinal
sudo usermod -aG sudo cardinal
```

### 3.2 Application Installation

```bash
# Switch to application user
sudo su - cardinal

# Clone repository
git clone https://github.com/yourusername/cardinal-biggles.git
cd cardinal-biggles

# Create virtual environment
python3.9 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### 3.3 Configuration

```bash
# Create directories
mkdir -p logs reports data config

# Set up environment
cp .env.example .env
nano .env  # Add production API keys

# Create production config
cp config/config.yaml config/production.yaml
nano config/production.yaml  # Adjust settings
```

**production.yaml** adjustments:
```yaml
logging:
  level: "WARNING"  # Less verbose in production
  file: "/var/log/cardinal/cardinal.log"
  console: false

output:
  output_directory: "/var/cardinal/reports"

# Use more powerful models for production
agents:
  reporter:
    provider: "claude"
    model: "claude-3-opus-20240229"
```

### 3.4 Service Configuration (systemd)

Create `/etc/systemd/system/cardinal-biggles.service`:

```ini
[Unit]
Description=Cardinal Biggles Research Service
After=network.target

[Service]
Type=simple
User=cardinal
Group=cardinal
WorkingDirectory=/home/cardinal/cardinal-biggles
Environment="PATH=/home/cardinal/cardinal-biggles/venv/bin"
EnvironmentFile=/home/cardinal/cardinal-biggles/.env
ExecStart=/home/cardinal/cardinal-biggles/venv/bin/python -m cli.main serve
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable cardinal-biggles
sudo systemctl start cardinal-biggles
sudo systemctl status cardinal-biggles
```

### 3.5 Nginx Reverse Proxy (Optional)

If exposing API:

```nginx
# /etc/nginx/sites-available/cardinal-biggles

server {
    listen 80;
    server_name cardinal.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable:
```bash
sudo ln -s /etc/nginx/sites-available/cardinal-biggles /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 3.6 SSL Certificate (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d cardinal.yourdomain.com
```

---

## 4. Cloud Deployment

### 4.1 AWS Deployment

**Using EC2**:

1. **Launch EC2 Instance**:
   - AMI: Ubuntu Server 22.04 LTS
   - Instance Type: t3.xlarge (4 vCPU, 16GB RAM)
   - Storage: 50GB gp3 SSD
   - Security Group: Allow ports 22, 80, 443

2. **Setup**:
```bash
# SSH into instance
ssh -i your-key.pem ubuntu@ec2-ip-address

# Follow "Production Deployment" steps above
```

3. **Use AWS Secrets Manager**:
```python
# Update code to fetch secrets
import boto3

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return response['SecretString']

# In llm_factory.py
api_key = get_secret('cardinal/openai_key')
```

**Using ECS (Docker)**:

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "cli.main", "serve"]
```

Build and push:
```bash
docker build -t cardinal-biggles:latest .
docker tag cardinal-biggles:latest your-ecr-repo/cardinal-biggles:latest
docker push your-ecr-repo/cardinal-biggles:latest
```

### 4.2 Google Cloud Deployment

**Using Cloud Run**:

```yaml
# cloudbuild.yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/cardinal-biggles', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/cardinal-biggles']
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'run'
      - 'deploy'
      - 'cardinal-biggles'
      - '--image=gcr.io/$PROJECT_ID/cardinal-biggles'
      - '--region=us-central1'
      - '--platform=managed'
```

Deploy:
```bash
gcloud builds submit --config cloudbuild.yaml
```

### 4.3 Azure Deployment

**Using Azure Container Instances**:

```bash
# Create resource group
az group create --name cardinal-rg --location eastus

# Create container instance
az container create \
  --resource-group cardinal-rg \
  --name cardinal-biggles \
  --image your-registry/cardinal-biggles:latest \
  --cpu 4 \
  --memory 16 \
  --ports 8000 \
  --environment-variables \
    OPENAI_API_KEY=$OPENAI_API_KEY \
    ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY
```

---

## 5. Configuration Management

### 5.1 Environment-Specific Configs

```
config/
├── config.yaml          # Default/development
├── production.yaml      # Production overrides
├── staging.yaml         # Staging environment
└── test.yaml           # Testing environment
```

Load based on environment:
```python
import os

env = os.getenv('CARDINAL_ENV', 'development')
config_file = f'config/{env}.yaml'
```

### 5.2 Secrets Management

**Development**: `.env` file
**Production**: Use secret management service

```python
# secrets.py
import os
from typing import Optional

def get_secret(key: str) -> Optional[str]:
    """Get secret from environment-appropriate source"""
    env = os.getenv('CARDINAL_ENV', 'development')

    if env == 'development':
        return os.getenv(key)
    elif env == 'production':
        # Use AWS Secrets Manager, Azure Key Vault, etc.
        return get_from_secrets_manager(key)
```

### 5.3 Configuration Validation

```python
# Validate configuration on startup
def validate_config(config: Dict) -> bool:
    required_fields = [
        'llm.default_provider',
        'llm.providers',
        'agents',
        'output.output_directory'
    ]

    for field in required_fields:
        if not get_nested(config, field):
            raise ConfigurationError(f"Missing required field: {field}")

    return True
```

---

## 6. Monitoring & Maintenance

### 6.1 Health Checks

```python
# health.py
async def health_check() -> Dict:
    """Perform health check"""
    checks = {
        'llm_factory': await check_llm_factory(),
        'knowledge_store': await check_knowledge_store(),
        'web_search': await check_web_search(),
    }

    return {
        'status': 'healthy' if all(checks.values()) else 'unhealthy',
        'checks': checks,
        'timestamp': datetime.now().isoformat()
    }
```

Endpoint:
```bash
curl http://localhost:8000/health
```

### 6.2 Log Management

**Log Rotation**:
```bash
# /etc/logrotate.d/cardinal-biggles
/var/log/cardinal/*.log {
    daily
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 cardinal cardinal
    sharedscripts
    postrotate
        systemctl reload cardinal-biggles
    endscript
}
```

**Centralized Logging**:
```python
# Use structured logging
import structlog

logger = structlog.get_logger()
logger.info("agent_execution", agent_id="scholar", duration=12.5, status="success")
```

### 6.3 Backup Strategy

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backup/cardinal/$(date +%Y%m%d)"
mkdir -p $BACKUP_DIR

# Backup knowledge store
cp /var/cardinal/data/knowledge_store.json $BACKUP_DIR/

# Backup configuration
cp /home/cardinal/cardinal-biggles/config/*.yaml $BACKUP_DIR/

# Backup reports (last 7 days)
find /var/cardinal/reports -name "*.md" -mtime -7 -exec cp {} $BACKUP_DIR/ \;

# Compress
tar -czf $BACKUP_DIR.tar.gz $BACKUP_DIR
rm -rf $BACKUP_DIR

# Upload to S3 (optional)
aws s3 cp $BACKUP_DIR.tar.gz s3://your-bucket/cardinal-backups/
```

Add to cron:
```bash
crontab -e
# Add: 0 2 * * * /home/cardinal/backup.sh
```

### 6.4 Performance Monitoring

**Application Metrics**:

```python
# metrics.py
from prometheus_client import Counter, Histogram, Gauge

request_count = Counter('cardinal_requests_total', 'Total requests')
request_duration = Histogram('cardinal_request_duration_seconds', 'Request duration')
active_agents = Gauge('cardinal_active_agents', 'Number of active agents')
```

**System Monitoring**:

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor in real-time
htop
```

### 6.5 Update & Upgrade Procedure

```bash
#!/bin/bash
# update.sh

# Stop service
sudo systemctl stop cardinal-biggles

# Backup current version
cp -r /home/cardinal/cardinal-biggles /home/cardinal/cardinal-biggles.backup

# Pull latest code
cd /home/cardinal/cardinal-biggles
git pull origin main

# Update dependencies
source venv/bin/activate
pip install -r requirements.txt

# Run migrations (if any)
# python manage.py migrate

# Run tests
pytest

# Restart service
sudo systemctl start cardinal-biggles

# Check status
sudo systemctl status cardinal-biggles
```

---

## 7. Troubleshooting Deployment Issues

See TROUBLESHOOTING.md for common issues and solutions.

---
