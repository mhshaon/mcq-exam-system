# Production Deployment Guide for MCQ Exam System

## 🚀 Production Deployment Options

### Option 1: VPS/Cloud Server (Recommended)
- **DigitalOcean Droplet** (Ubuntu 20.04/22.04)
- **AWS EC2** (Ubuntu Server)
- **Google Cloud Platform** (Compute Engine)
- **Linode** (Ubuntu)
- **Vultr** (Ubuntu)

### Option 2: Platform as a Service (PaaS)
- **Heroku** (Easy deployment)
- **Railway** (Modern platform)
- **Render** (Free tier available)
- **PythonAnywhere** (Django-friendly)

## 🛠️ VPS/Cloud Server Setup (Ubuntu)

### 1. Server Preparation

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3.8+ (check available versions)
sudo apt install python3.8 python3.8-venv python3.8-dev python3-pip -y
# OR for newer systems:
# sudo apt install python3.9 python3.9-venv python3.9-dev python3-pip -y
# OR for latest:
# sudo apt install python3.10 python3.10-venv python3.10-dev python3-pip -y

# Install PostgreSQL
sudo apt install postgresql postgresql-contrib -y

# Install Nginx
sudo apt install nginx -y

# Install Git
sudo apt install git -y

# Install other dependencies
sudo apt install build-essential libpq-dev -y
```

### 2. Database Setup

```bash
# Switch to postgres user
sudo -u postgres psql

# Create database and user with proper privileges
CREATE DATABASE mcq_exam_db;
CREATE USER mcq_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE mcq_exam_db TO mcq_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO mcq_user;
ALTER USER mcq_user CREATEDB;  # Allow user to create databases
\q

# Alternative: Create user interactively with proper privileges
# sudo -u postgres createuser --interactive --pwprompt mcq_user
# sudo -u postgres createdb --owner=mcq_user mcq_exam_db
```

### 3. Application Deployment

```bash
# Create application directory
sudo mkdir -p /var/www/mcq-exam
sudo chown $USER:$USER /var/www/mcq-exam
cd /var/www/mcq-exam

# Clone your repository
git clone https://github.com/mhshaon/mcq-exam-system.git .

# Create virtual environment (use your Python version)
python3.8 -m venv venv
# OR: python3.9 -m venv venv
# OR: python3.10 -m venv venv
source venv/bin/activate

# Upgrade pip first
pip install --upgrade pip setuptools wheel

# Install dependencies (choose based on your Python version)
# For Python 3.8+ (most compatible):
pip install -r requirements_compatible.txt
# OR for Python 3.10+ (latest features):
# pip install -r requirements_production.txt
```

### 4. Environment Configuration

Create `.env` file:
```bash
nano .env
```

```env
DEBUG=False
SECRET_KEY=your-super-secret-key-here
DATABASE_URL=postgresql://mcq_user:your_secure_password@localhost/mcq_exam_db
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@domain.com
EMAIL_HOST_PASSWORD=your-email-password
```

### 5. Django Configuration

Update `config/settings.py` for production:

```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Security settings
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', '').split(',')

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'mcq_exam_db',
        'USER': 'mcq_user',
        'PASSWORD': os.getenv('DATABASE_PASSWORD'),
        'HOST': 'localhost',
        'PORT': '5432',
    }
}

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = '/var/www/mcq-exam/staticfiles/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = '/var/www/mcq-exam/media/'

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')
```

### 6. Database Migration

```bash
# Activate virtual environment
source venv/bin/activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput
```

### 7. Gunicorn Configuration

Create `gunicorn.conf.py`:
```python
bind = "127.0.0.1:8000"
workers = 3
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
timeout = 30
keepalive = 2
preload_app = True
```

### 8. Systemd Service

Create `/etc/systemd/system/mcq-exam.service`:
```bash
# Copy the service file
sudo cp mcq-exam.service /etc/systemd/system/mcq-exam.service

# OR create manually:
sudo nano /etc/systemd/system/mcq-exam.service
```

Service file content:
```ini
[Unit]
Description=MCQ Exam System Gunicorn daemon
After=network.target postgresql.service
Wants=postgresql.service

[Service]
Type=notify
User=www-data
Group=www-data
WorkingDirectory=/var/www/mcq-exam
Environment="PATH=/var/www/mcq-exam/venv/bin"
Environment="DJANGO_SETTINGS_MODULE=config.settings_production"
ExecStart=/var/www/mcq-exam/venv/bin/gunicorn --config gunicorn.conf.py config.wsgi:application
ExecReload=/bin/kill -s HUP $MAINPID
Restart=on-failure
RestartSec=5
TimeoutStopSec=30

# Security settings
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/www/mcq-exam
ReadWritePaths=/var/log/gunicorn

[Install]
WantedBy=multi-user.target
```

### 9. Nginx Configuration

Create `/etc/nginx/sites-available/mcq-exam`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /var/www/mcq-exam;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    location /media/ {
        root /var/www/mcq-exam;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 10. SSL Certificate (Let's Encrypt)

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx -y

# Get SSL certificate
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Auto-renewal
sudo crontab -e
# Add: 0 12 * * * /usr/bin/certbot renew --quiet
```

### 11. Start Services

```bash
# Enable and start services
sudo systemctl enable mcq-exam
sudo systemctl start mcq-exam
sudo systemctl enable nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status mcq-exam
sudo systemctl status nginx
```

## 🌐 Domain Configuration

### DNS Settings
- **A Record**: `@` → `your-server-ip`
- **A Record**: `www` → `your-server-ip`
- **CNAME**: `api` → `your-domain.com` (optional)

## 📊 Monitoring & Maintenance

### Log Files
```bash
# Application logs
sudo journalctl -u mcq-exam -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Backup Script
```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump mcq_exam_db > /var/backups/mcq_exam_$DATE.sql
tar -czf /var/backups/mcq_exam_files_$DATE.tar.gz /var/www/mcq-exam/media/
```

## 🔧 Environment-Specific Settings

### Development
```python
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
```

### Staging
```python
DEBUG = False
ALLOWED_HOSTS = ['staging.your-domain.com']
```

### Production
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
```

## 🚀 Quick Deployment Commands

```bash
# Update application
cd /var/www/mcq-exam
git pull origin main
source venv/bin/activate

# Upgrade pip and install dependencies
pip install --upgrade pip setuptools wheel
pip install -r requirements_compatible.txt

# Run migrations and collect static files
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart mcq-exam
```

## 📋 Pre-Deployment Checklist

- [ ] Server prepared with all dependencies
- [ ] Database created and configured
- [ ] Environment variables set
- [ ] Static files collected
- [ ] Database migrations applied
- [ ] Superuser created
- [ ] SSL certificate installed
- [ ] Domain DNS configured
- [ ] Monitoring setup
- [ ] Backup strategy implemented

## 🆘 Troubleshooting

### Common Issues

#### 1. "No matching distribution found for Django==5.0.6"
**Cause**: Python version is too old (Django 5.0+ requires Python 3.10+)

**Solutions**:
```bash
# Check Python version
python3 --version

# If Python < 3.10, use compatible requirements:
pip install -r requirements_compatible.txt

# OR upgrade Python (Ubuntu 20.04+):
sudo apt install python3.10 python3.10-venv python3.10-dev -y
python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements_production.txt
```

#### 2. "ERROR: Failed building wheel for psycopg2-binary"
**Solutions**:
```bash
# Install system dependencies
sudo apt install libpq-dev build-essential -y

# OR use SQLite for development:
pip install -r requirements-sqlite.txt
```

#### 3. "AttributeError: module 'pkgutil' has no attribute 'ImpImporter'"
**Solutions**:
```bash
# Upgrade pip and setuptools
pip install --upgrade pip setuptools wheel

# Use compatible requirements
pip install -r requirements_compatible.txt
```

#### 4. "Unable to create the django_migrations table (permission denied for schema public)"
**Cause**: PostgreSQL user lacks CREATE privileges on the database

**Solutions**:
```bash
# Connect to PostgreSQL as superuser
sudo -u postgres psql

# Grant necessary privileges to your user
GRANT ALL PRIVILEGES ON DATABASE mcq_exam_db TO mcq_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO mcq_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO mcq_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO mcq_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO mcq_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO mcq_user;

# Exit PostgreSQL
\q

# OR create a new user with proper privileges
sudo -u postgres createuser --interactive --pwprompt mcq_user
sudo -u postgres createdb --owner=mcq_user mcq_exam_db
```

#### 5. "Failed to start mcq-exam.service - MCQ Exam System Gunicorn daemon"
**Cause**: Systemd service configuration or permission issues

**Solutions**:
```bash
# Check service status and logs
sudo systemctl status mcq-exam
sudo journalctl -u mcq-exam -n 50

# Common fixes:

# 1. Check if the service file exists and is correct
sudo systemctl cat mcq-exam

# 2. Reload systemd and restart
sudo systemctl daemon-reload
sudo systemctl restart mcq-exam

# 3. Check file permissions
sudo chown -R www-data:www-data /var/www/mcq-exam
sudo chmod +x /var/www/mcq-exam/venv/bin/gunicorn

# 4. Test Gunicorn manually
cd /var/www/mcq-exam
source venv/bin/activate
gunicorn --config gunicorn.conf.py config.wsgi:application

# 5. Check if port 8000 is available
sudo netstat -tlnp | grep :8000
sudo lsof -i :8000

# 6. Create logs directory
sudo mkdir -p /var/log/gunicorn
sudo chown www-data:www-data /var/log/gunicorn
```

#### 6. Other Common Issues
- **502 Bad Gateway**: Check if Gunicorn is running
- **Static files not loading**: Check Nginx configuration
- **Database connection error**: Verify database credentials
- **Permission denied**: Check file ownership and permissions

### Useful Commands
```bash
# Check service status
sudo systemctl status mcq-exam

# View logs
sudo journalctl -u mcq-exam -n 50

# Test Nginx configuration
sudo nginx -t

# Restart services
sudo systemctl restart mcq-exam
sudo systemctl restart nginx
```

## 💰 Cost Estimation

### VPS Options
- **DigitalOcean**: $5-10/month (1GB RAM, 1 CPU)
- **AWS EC2**: $8-15/month (t2.micro)
- **Google Cloud**: $5-12/month (e2-micro)
- **Linode**: $5-10/month (Nanode)

### Additional Costs
- **Domain**: $10-15/year
- **SSL Certificate**: Free (Let's Encrypt)
- **Email Service**: $5-10/month (SendGrid, Mailgun)

---

**Total Estimated Cost: $5-25/month** for a small to medium traffic application.
