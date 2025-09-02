# Deployment Guide

## Python Version Compatibility

This project is compatible with:
- **Python 3.8** (recommended minimum)
- **Python 3.9** (recommended)
- **Python 3.10** (recommended)
- **Python 3.11** (recommended)
- **Python 3.12** (compatible with updated requirements)

## Installation on Different Servers

### For Production Servers

1. **Install Python 3.9+ (recommended)**
   ```bash
   # Ubuntu/Debian
   sudo apt update
   sudo apt install python3.9 python3.9-venv python3.9-dev
   
   # CentOS/RHEL
   sudo yum install python39 python39-devel
   ```

2. **Create virtual environment**
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install requirements**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

### For Development Servers

1. **Install all packages including dev tools**
   ```bash
   pip install -r requirements-dev.txt
   ```

## Troubleshooting Common Issues

### AttributeError: module 'pkgutil' has no attribute 'ImpImporter'

**Cause**: This error occurs when using Python 3.12+ with older package versions.

**Solutions**:

1. **Use Python 3.9-3.11 (Recommended)**
   ```bash
   # Check Python version
   python --version
   
   # If using Python 3.12+, downgrade to 3.11
   pyenv install 3.11.7
   pyenv local 3.11.7
   ```

2. **Update problematic packages**
   ```bash
   pip install --upgrade setuptools wheel
   pip install --upgrade cryptography
   ```

3. **Use the cleaned requirements.txt**
   ```bash
   pip install -r requirements.txt
   ```

### Database Issues

1. **For PostgreSQL (Production)**
   ```bash
   # Install PostgreSQL
   sudo apt install postgresql postgresql-contrib
   
   # Install Python PostgreSQL adapter
   pip install psycopg2-binary
   ```

2. **For SQLite (Development)**
   ```bash
   # No additional setup needed
   python manage.py migrate
   ```

### Static Files Issues

1. **Collect static files**
   ```bash
   python manage.py collectstatic
   ```

2. **Configure static files in settings.py**
   ```python
   STATIC_ROOT = BASE_DIR / 'staticfiles'
   STATIC_URL = '/static/'
   ```

## Environment Variables

Create a `.env` file:
```bash
DEBUG=False
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/dbname
EMAIL_HOST=your-smtp-host
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email
EMAIL_HOST_PASSWORD=your-password
```

## Deployment Checklist

- [ ] Python 3.9+ installed
- [ ] Virtual environment created and activated
- [ ] Requirements installed successfully
- [ ] Database configured
- [ ] Environment variables set
- [ ] Static files collected
- [ ] Migrations applied
- [ ] Superuser created
- [ ] Server configured (nginx/apache)
- [ ] SSL certificate installed (production)

## Quick Fix for Import Errors

If you encounter import errors, try this sequence:

```bash
# 1. Update pip and setuptools
pip install --upgrade pip setuptools wheel

# 2. Clear pip cache
pip cache purge

# 3. Reinstall requirements
pip uninstall -r requirements.txt -y
pip install -r requirements.txt

# 4. If still having issues, use Python 3.11
pyenv install 3.11.7
pyenv local 3.11.7
pip install -r requirements.txt
```
