#!/bin/bash

# Production Update Script for MCQ Exam System
# This script updates your production server with the latest changes

set -e

echo "🚀 Updating MCQ Exam System in Production..."
echo "=============================================="

# Configuration
PROJECT_DIR="/var/www/mcq-exam"
SERVICE_NAME="mcq-exam"
BACKUP_DIR="/var/backups/mcq-exam"
DATE=$(date +%Y%m%d_%H%M%S)

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script with sudo: sudo ./update_production.sh"
    exit 1
fi

echo ""
echo "1. 📋 Pre-update checks..."
echo "-------------------------"

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo "❌ Project directory not found: $PROJECT_DIR"
    echo "Please run the initial deployment first."
    exit 1
fi

# Check if service exists
if ! systemctl is-active --quiet $SERVICE_NAME; then
    echo "⚠️  Service $SERVICE_NAME is not running"
fi

echo "✅ Pre-update checks completed"

echo ""
echo "2. 💾 Creating backup..."
echo "----------------------"

# Create backup directory
mkdir -p $BACKUP_DIR

# Backup current code
echo "Backing up current code..."
tar -czf $BACKUP_DIR/code_backup_$DATE.tar.gz -C $PROJECT_DIR .

# Backup database
echo "Backing up database..."
sudo -u postgres pg_dump mcq_exam_db > $BACKUP_DIR/database_backup_$DATE.sql

echo "✅ Backup created: $BACKUP_DIR/backup_$DATE"

echo ""
echo "3. 🔄 Stopping services..."
echo "-------------------------"

# Stop the application service
systemctl stop $SERVICE_NAME || true

# Stop Nginx (optional, for zero-downtime updates)
# systemctl stop nginx || true

echo "✅ Services stopped"

echo ""
echo "4. 📥 Pulling latest changes..."
echo "-------------------------------"

cd $PROJECT_DIR

# Switch to www-data user for git operations
sudo -u www-data git fetch origin
sudo -u www-data git reset --hard origin/main

echo "✅ Latest changes pulled"

echo ""
echo "5. 🐍 Updating Python environment..."
echo "-----------------------------------"

# Activate virtual environment and update packages
sudo -u www-data $PROJECT_DIR/venv/bin/pip install --upgrade pip

# Install/update requirements
if [ -f "$PROJECT_DIR/requirements_compatible.txt" ]; then
    sudo -u www-data $PROJECT_DIR/venv/bin/pip install -r $PROJECT_DIR/requirements_compatible.txt
elif [ -f "$PROJECT_DIR/requirements_production.txt" ]; then
    sudo -u www-data $PROJECT_DIR/venv/bin/pip install -r $PROJECT_DIR/requirements_production.txt
else
    sudo -u www-data $PROJECT_DIR/venv/bin/pip install -r $PROJECT_DIR/requirements.txt
fi

echo "✅ Python environment updated"

echo ""
echo "6. 🗄️ Running database migrations..."
echo "----------------------------------"

# Run migrations
sudo -u www-data $PROJECT_DIR/venv/bin/python $PROJECT_DIR/manage.py migrate

echo "✅ Database migrations completed"

echo ""
echo "7. 📁 Collecting static files..."
echo "-------------------------------"

# Collect static files
sudo -u www-data $PROJECT_DIR/venv/bin/python $PROJECT_DIR/manage.py collectstatic --noinput

echo "✅ Static files collected"

echo ""
echo "8. 🔧 Updating service configuration..."
echo "--------------------------------------"

# Copy updated service file if it exists
if [ -f "$PROJECT_DIR/mcq-exam.service" ]; then
    cp $PROJECT_DIR/mcq-exam.service /etc/systemd/system/mcq-exam.service
    systemctl daemon-reload
    echo "✅ Service configuration updated"
fi

echo ""
echo "9. 🚀 Starting services..."
echo "------------------------"

# Start the application service
systemctl start $SERVICE_NAME
systemctl enable $SERVICE_NAME

# Start Nginx if it was stopped
# systemctl start nginx

# Check service status
sleep 3
if systemctl is-active --quiet $SERVICE_NAME; then
    echo "✅ Service $SERVICE_NAME is running"
else
    echo "❌ Service $SERVICE_NAME failed to start"
    echo "Check logs: sudo journalctl -u $SERVICE_NAME -n 50"
    exit 1
fi

echo ""
echo "10. 🔍 Health checks..."
echo "----------------------"

# Test if the application is responding
sleep 5
if curl -f -s http://localhost:8000 > /dev/null; then
    echo "✅ Application is responding"
else
    echo "⚠️  Application may not be responding properly"
    echo "Check logs: sudo journalctl -u $SERVICE_NAME -f"
fi

# Check Nginx status
if systemctl is-active --quiet nginx; then
    echo "✅ Nginx is running"
else
    echo "⚠️  Nginx is not running"
fi

echo ""
echo "🎉 Production update completed successfully!"
echo ""
echo "📋 Summary:"
echo "- Code updated from Git repository"
echo "- Python packages updated"
echo "- Database migrations applied"
echo "- Static files collected"
echo "- Services restarted"
echo "- Backup created: $BACKUP_DIR/backup_$DATE"
echo ""
echo "🔗 Your application should be available at:"
echo "- HTTP: http://your-server-ip"
echo "- HTTPS: https://your-domain.com (if SSL configured)"
echo ""
echo "📊 Monitor your application:"
echo "- Service status: sudo systemctl status $SERVICE_NAME"
echo "- Service logs: sudo journalctl -u $SERVICE_NAME -f"
echo "- Nginx logs: sudo tail -f /var/log/nginx/error.log"
