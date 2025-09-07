#!/bin/bash

# Troubleshooting script for MCQ Exam System service
# Run this script to diagnose and fix service issues

set -e

echo "🔍 Troubleshooting MCQ Exam System Service..."
echo "=============================================="

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ Please run this script with sudo: sudo ./troubleshoot_service.sh"
    exit 1
fi

PROJECT_DIR="/var/www/mcq-exam"
SERVICE_NAME="mcq-exam"

echo ""
echo "1. 📊 Checking service status..."
echo "-------------------------------"
systemctl status $SERVICE_NAME --no-pager -l || true

echo ""
echo "2. 📝 Checking service logs..."
echo "------------------------------"
journalctl -u $SERVICE_NAME -n 20 --no-pager || true

echo ""
echo "3. 🔧 Checking service configuration..."
echo "---------------------------------------"
if systemctl cat $SERVICE_NAME > /dev/null 2>&1; then
    echo "✅ Service file exists"
    systemctl cat $SERVICE_NAME
else
    echo "❌ Service file not found. Creating it..."
    
    # Create the service file
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=MCQ Exam System Gunicorn daemon
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn --config gunicorn.conf.py config.wsgi:application
ExecReload=/bin/kill -s HUP \$MAINPID
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

    echo "✅ Service file created"
fi

echo ""
echo "4. 📁 Checking project directory..."
echo "----------------------------------"
if [ -d "$PROJECT_DIR" ]; then
    echo "✅ Project directory exists: $PROJECT_DIR"
    ls -la $PROJECT_DIR/ | head -10
else
    echo "❌ Project directory not found: $PROJECT_DIR"
    echo "Please ensure the project is deployed correctly"
    exit 1
fi

echo ""
echo "5. 🐍 Checking Python virtual environment..."
echo "-------------------------------------------"
if [ -d "$PROJECT_DIR/venv" ]; then
    echo "✅ Virtual environment exists"
    if [ -f "$PROJECT_DIR/venv/bin/gunicorn" ]; then
        echo "✅ Gunicorn is installed"
        ls -la $PROJECT_DIR/venv/bin/gunicorn
    else
        echo "❌ Gunicorn not found in virtual environment"
        echo "Installing Gunicorn..."
        sudo -u www-data $PROJECT_DIR/venv/bin/pip install gunicorn
    fi
else
    echo "❌ Virtual environment not found"
    echo "Creating virtual environment..."
    python3 -m venv $PROJECT_DIR/venv
    sudo -u www-data $PROJECT_DIR/venv/bin/pip install --upgrade pip
    sudo -u www-data $PROJECT_DIR/venv/bin/pip install -r $PROJECT_DIR/requirements_compatible.txt
fi

echo ""
echo "6. 🔐 Checking file permissions..."
echo "---------------------------------"
echo "Setting correct ownership..."
chown -R www-data:www-data $PROJECT_DIR
chmod +x $PROJECT_DIR/venv/bin/gunicorn
echo "✅ Permissions set"

echo ""
echo "7. 📝 Checking logs directory..."
echo "--------------------------------"
mkdir -p /var/log/gunicorn
chown www-data:www-data /var/log/gunicorn
echo "✅ Logs directory ready"

echo ""
echo "8. 🌐 Checking port availability..."
echo "----------------------------------"
if netstat -tlnp | grep :8000 > /dev/null; then
    echo "⚠️  Port 8000 is in use:"
    netstat -tlnp | grep :8000
    echo "Killing processes on port 8000..."
    fuser -k 8000/tcp || true
    sleep 2
else
    echo "✅ Port 8000 is available"
fi

echo ""
echo "9. 🔄 Reloading and restarting service..."
echo "-----------------------------------------"
systemctl daemon-reload
systemctl enable $SERVICE_NAME
systemctl restart $SERVICE_NAME

echo ""
echo "10. ✅ Final status check..."
echo "----------------------------"
sleep 3
systemctl status $SERVICE_NAME --no-pager -l

echo ""
echo "🎉 Troubleshooting complete!"
echo ""
echo "📋 Next steps:"
echo "1. Check if the service is running: sudo systemctl status $SERVICE_NAME"
echo "2. View logs: sudo journalctl -u $SERVICE_NAME -f"
echo "3. Test the application: curl http://localhost:8000"
echo "4. Check Nginx: sudo systemctl status nginx"
