#!/bin/bash

# Deployment script for MCQ Exam System
# Usage: ./deploy.sh [environment]

set -e

ENVIRONMENT=${1:-production}
PROJECT_DIR="/var/www/mcq-exam"
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="/var/backups/mcq-exam"

echo "🚀 Starting deployment for $ENVIRONMENT environment..."

# Create backup
echo "📦 Creating backup..."
mkdir -p $BACKUP_DIR
BACKUP_FILE="$BACKUP_DIR/backup_$(date +%Y%m%d_%H%M%S).sql"
pg_dump mcq_exam_db > $BACKUP_FILE
echo "✅ Backup created: $BACKUP_FILE"

# Navigate to project directory
cd $PROJECT_DIR

# Pull latest changes
echo "📥 Pulling latest changes..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtual environment..."
source $VENV_DIR/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
if [ "$ENVIRONMENT" = "production" ]; then
    pip install -r requirements_production.txt
else
    pip install -r requirements.txt
fi

# Run database migrations
echo "🗄️ Running database migrations..."
python manage.py migrate

# Collect static files
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

# Create logs directory
echo "📝 Setting up logging..."
mkdir -p logs
sudo chown www-data:www-data logs

# Restart services
echo "🔄 Restarting services..."
sudo systemctl restart mcq-exam
sudo systemctl restart nginx

# Check service status
echo "✅ Checking service status..."
sudo systemctl status mcq-exam --no-pager -l
sudo systemctl status nginx --no-pager -l

echo "🎉 Deployment completed successfully!"
echo "🌐 Application should be available at your domain"
echo "📊 Check logs with: sudo journalctl -u mcq-exam -f"
