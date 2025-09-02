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

#### ERROR: Failed building wheel for psycopg2-binary

**Cause**: This error occurs when psycopg2-binary fails to build, usually due to missing system dependencies or incompatible Python versions.

**Solutions**:

1. **Use SQLite for Development (Recommended)**
   ```bash
   # Install without PostgreSQL dependencies
   pip install -r requirements-sqlite.txt
   ```

2. **Fix psycopg2-binary on Ubuntu/Debian**
   ```bash
   # Install system dependencies
   sudo apt update
   sudo apt install python3-dev libpq-dev postgresql-client
   
   # Try installing psycopg2-binary
   pip install psycopg2-binary
   ```

3. **Fix psycopg2-binary on Windows**
   ```bash
   # Install Microsoft Visual C++ Build Tools
   # Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/
   
   # Or try the source version
   pip install psycopg2
   ```

4. **Alternative PostgreSQL drivers**
   ```bash
   # Try newer version
   pip install psycopg2-binary>=2.9.9
   
   # Or use source version
   pip install psycopg2==2.9.9
   
   # Or use alternative driver
   pip install psycopg2cffi
   ```

5. **For Production with PostgreSQL**
   ```bash
   # Install PostgreSQL
   sudo apt install postgresql postgresql-contrib
   
   # Use the PostgreSQL requirements file
   pip install -r requirements-postgresql.txt
   ```

6. **For Development with SQLite**
   ```bash
   # No additional setup needed
   pip install -r requirements-sqlite.txt
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

## Quick Fix for Common Errors

### For Import Errors (pkgutil.ImpImporter)
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

### For psycopg2-binary Build Errors
```bash
# Option 1: Use SQLite for development (easiest)
pip install -r requirements-sqlite.txt

# Option 2: Try alternative PostgreSQL drivers
pip install psycopg2cffi

# Option 3: Install system dependencies (Ubuntu/Debian)
sudo apt install python3-dev libpq-dev
pip install psycopg2-binary

# Option 4: Use source version
pip install psycopg2==2.9.9
```
