# EngageAI - Developer Deployment Guide

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Local Development Setup](#local-development-setup)
3. [Production Deployment](#production-deployment)
4. [Docker Deployment](#docker-deployment)
5. [Cloud Deployment](#cloud-deployment)
6. [CI/CD Pipeline](#cicd-pipeline)
7. [Monitoring & Logging](#monitoring--logging)
8. [Troubleshooting](#troubleshooting)

## Prerequisites

### System Requirements
- **Python**: 3.10 or higher
- **Memory**: Minimum 4GB RAM (8GB recommended for production)
- **Storage**: At least 2GB free space
- **OS**: Linux (Ubuntu 20.04+ recommended), macOS, or Windows with WSL2

### Required Accounts & Keys
- OpenAI API account with valid API key
- Git repository access
- (Optional) Cloud provider account for deployment

## Local Development Setup

### 1. Clone Repository
```bash
git clone <repository-url>
cd marketing
```

### 2. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate
# On Windows:
.\venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 3. Install Dependencies
```bash
# Install Python packages
pip install -r requirements.txt

# Install Playwright browsers
playwright install

# Install system dependencies for Playwright (Linux only)
playwright install-deps
```

### 4. Environment Configuration
```bash
# Copy environment template
cp .env.template .env

# Edit .env file with your configuration
nano .env
```

Required environment variables:
```env
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini-2024-07-18

# SMTP Configuration (optional)
SMTP_SERVER=your_smtp_server
SMTP_PORT=587
SMTP_USER=your_smtp_username
SMTP_PASSWORD=your_smtp_password
FROM_EMAIL=your_email@domain.com
TO_EMAILS=recipient1@domain.com,recipient2@domain.com
```

### 5. Application Configuration
```bash
# Copy configuration template
cp config.template.py config.py

# Edit config.py with your business information
nano config.py
```

### 6. Run Development Server
```bash
# Start Streamlit development server
streamlit run app.py

# Or with custom configuration
streamlit run app.py --server.port 8501 --server.address localhost
```

The application will be available at `http://localhost:8501`

## Production Deployment

### Option 1: Linux Server with systemd

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python and dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install system dependencies for Playwright
sudo apt install libnss3 libnspr4 libatk-bridge2.0-0 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxrandr2 libgbm1 libxss1 libasound2 -y
```

#### 2. Application Setup
```bash
# Clone repository
git clone <repository-url> /opt/marketing-app
cd /opt/marketing-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install --with-deps

# Set up configuration
cp .env.template .env
cp config.template.py config.py

# Edit configuration files
nano .env
nano config.py
```

#### 3. Create systemd Service
```bash
sudo nano /etc/systemd/system/marketing-app.service
```

Service file content:
```ini
[Unit]
Description=EngageAI Marketing Application
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/opt/marketing-app
Environment="PATH=/opt/marketing-app/venv/bin"
EnvironmentFile=/opt/marketing-app/.env
ExecStart=/opt/marketing-app/venv/bin/streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

#### 4. Start Service
```bash
# Set permissions
sudo chown -R www-data:www-data /opt/marketing-app
sudo chmod 600 /opt/marketing-app/.env

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable marketing-app
sudo systemctl start marketing-app

# Check status
sudo systemctl status marketing-app
```

### Option 2: Using Screen/tmux (Alternative)
```bash
# Install screen
sudo apt install screen -y

# Start application in screen session
screen -S marketing-app
cd /opt/marketing-app
source venv/bin/activate
streamlit run app.py --server.port 8501 --server.address 0.0.0.0

# Detach from screen: Ctrl+A, then D
# Reattach: screen -r marketing-app
```

## Docker Deployment

### 1. Create Dockerfile
```dockerfile
FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright and browsers
RUN playwright install --with-deps

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  marketing-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - OPENAI_MODEL=${OPENAI_MODEL}
    volumes:
      - ./data:/app/data
      - ./uploads:/app/uploads
      - ./generated_docs:/app/generated_docs
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8501/_stcore/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - marketing-app
    restart: unless-stopped
```

### 3. Deploy with Docker
```bash
# Build and run
docker-compose up -d

# View logs
docker-compose logs -f marketing-app

# Update application
docker-compose pull
docker-compose up -d --build
```

## Cloud Deployment

### AWS EC2 Deployment
```bash
# Launch EC2 instance (Ubuntu 20.04 LTS)
# Security Group: Allow ports 22, 80, 443, 8501

# Connect to instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Follow Linux server deployment steps above
```

### Google Cloud Platform
```bash
# Create VM instance
gcloud compute instances create marketing-app \
    --image-family=ubuntu-2004-lts \
    --image-project=ubuntu-os-cloud \
    --machine-type=e2-medium \
    --tags=http-server,https-server

# SSH to instance
gcloud compute ssh marketing-app

# Follow Linux server deployment steps
```

### Heroku Deployment
Create `Procfile`:
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

Create `runtime.txt`:
```
python-3.10.12
```

Deploy:
```bash
# Install Heroku CLI and login
heroku create your-app-name
heroku config:set OPENAI_API_KEY=your_key
git push heroku main
```

## CI/CD Pipeline

### GitHub Actions Example
Create `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
    
    - name: Run tests
      run: |
        python -m pytest tests/ || true
    
    - name: Deploy to server
      uses: appleboy/ssh-action@v0.1.5
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /opt/marketing-app
          git pull origin main
          source venv/bin/activate
          pip install -r requirements.txt
          sudo systemctl restart marketing-app
```

## Monitoring & Logging

### 1. Application Logs
```bash
# View systemd logs
sudo journalctl -u marketing-app -f

# View application logs
tail -f /opt/marketing-app/logs/app.log
```

### 2. System Monitoring
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Monitor resources
htop
iotop
nethogs
```

### 3. Log Rotation
Create `/etc/logrotate.d/marketing-app`:
```
/opt/marketing-app/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 www-data www-data
    postrotate
        systemctl reload marketing-app
    endscript
}
```

## Troubleshooting

### Common Issues

#### 1. Playwright Browser Issues
```bash
# Reinstall browsers
playwright install --with-deps

# Check browser installation
playwright install --dry-run
```

#### 2. Permission Issues
```bash
# Fix ownership
sudo chown -R www-data:www-data /opt/marketing-app

# Fix permissions
chmod 644 /opt/marketing-app/.env
chmod 755 /opt/marketing-app
```

#### 3. OpenAI API Issues
```bash
# Test API key
python -c "
import openai
import os
from dotenv import load_dotenv
load_dotenv()
client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
print('API key is valid')
"
```

#### 4. Port Issues
```bash
# Check if port is in use
sudo netstat -tlnp | grep :8501

# Kill process using port
sudo kill -9 $(sudo lsof -t -i:8501)
```

### Performance Optimization

#### 1. Memory Management
```python
# Add to streamlit config
# .streamlit/config.toml
[server]
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
```

#### 2. Caching Configuration
```python
# In your app.py, use Streamlit caching
@st.cache_data
def expensive_function():
    # Your expensive computation
    pass
```

### Security Checklist

- [ ] API keys stored in environment variables
- [ ] `.env` file not committed to git
- [ ] Proper file permissions set
- [ ] Firewall configured
- [ ] HTTPS enabled in production
- [ ] Regular security updates applied
- [ ] Input validation implemented
- [ ] Rate limiting configured

### Backup Strategy

```bash
# Create backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/opt/backups/marketing-app"

mkdir -p $BACKUP_DIR

# Backup configuration
cp /opt/marketing-app/.env $BACKUP_DIR/.env_$DATE
cp /opt/marketing-app/config.py $BACKUP_DIR/config.py_$DATE

# Backup database
cp /opt/marketing-app/csv_manager.db $BACKUP_DIR/csv_manager.db_$DATE

# Backup generated files
tar -czf $BACKUP_DIR/generated_docs_$DATE.tar.gz /opt/marketing-app/generated_docs/

# Clean old backups (keep last 30 days)
find $BACKUP_DIR -name "*" -mtime +30 -delete
```

## Support & Maintenance

### Regular Maintenance Tasks
1. **Weekly**: Check logs and system resources
2. **Monthly**: Update dependencies and security patches
3. **Quarterly**: Review and update configuration
4. **Annually**: Security audit and performance review

### Getting Help
- Check application logs first
- Review this documentation
- Search existing issues in repository
- Contact system administrator or development team

---

**Note**: Always test deployments in a staging environment before production deployment.
