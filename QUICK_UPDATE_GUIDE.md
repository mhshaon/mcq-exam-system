# Quick Update Guide - Examiner Role Fix

## 🚀 How to Deploy the Examiner Role Fix to Production

### Method 1: Using the Update Script (Recommended)

1. **Upload the update script to your server:**
   ```bash
   # On your local machine
   scp update_production.sh user@your-server-ip:/home/user/
   
   # Or download directly on server
   wget https://raw.githubusercontent.com/your-username/mcq-exam-system/main/update_production.sh
   ```

2. **Run the update script:**
   ```bash
   # SSH into your server
   ssh user@your-server-ip
   
   # Make script executable and run
   chmod +x update_production.sh
   sudo ./update_production.sh
   ```

### Method 2: Manual Update

1. **SSH into your production server:**
   ```bash
   ssh user@your-server-ip
   ```

2. **Navigate to project directory:**
   ```bash
   cd /var/www/mcq-exam
   ```

3. **Stop the service:**
   ```bash
   sudo systemctl stop mcq-exam
   ```

4. **Pull latest changes:**
   ```bash
   sudo -u www-data git fetch origin
   sudo -u www-data git reset --hard origin/main
   ```

5. **Update Python packages:**
   ```bash
   sudo -u www-data venv/bin/pip install -r requirements_compatible.txt
   ```

6. **Run database migrations:**
   ```bash
   sudo -u www-data venv/bin/python manage.py migrate
   ```

7. **Collect static files:**
   ```bash
   sudo -u www-data venv/bin/python manage.py collectstatic --noinput
   ```

8. **Update service configuration:**
   ```bash
   sudo cp mcq-exam.service /etc/systemd/system/mcq-exam.service
   sudo systemctl daemon-reload
   ```

9. **Start the service:**
   ```bash
   sudo systemctl start mcq-exam
   sudo systemctl enable mcq-exam
   ```

10. **Check status:**
    ```bash
    sudo systemctl status mcq-exam
    ```

### Method 3: Using Git Hooks (Advanced)

If you want automatic deployments, you can set up a Git hook:

1. **Create a webhook endpoint:**
   ```bash
   # Create webhook script
   sudo nano /var/www/mcq-exam/webhook.sh
   ```

2. **Add webhook content:**
   ```bash
   #!/bin/bash
   cd /var/www/mcq-exam
   sudo -u www-data git pull origin main
   sudo -u www-data venv/bin/pip install -r requirements_compatible.txt
   sudo -u www-data venv/bin/python manage.py migrate
   sudo -u www-data venv/bin/python manage.py collectstatic --noinput
   sudo systemctl restart mcq-exam
   ```

3. **Make it executable:**
   ```bash
   sudo chmod +x /var/www/mcq-exam/webhook.sh
   ```

## 🔍 What Changed in This Update

### Files Modified:
- `accounts/forms.py` - Custom signup form with role handling
- `accounts/adapters.py` - Custom account adapter for role assignment
- `templates/account/signup.html` - Updated role selection logic
- `config/settings.py` - Added custom form and adapter settings

### New Features:
- ✅ **Examiner role selection** works from "Get Started" button
- ✅ **URL parameter handling** (`?role=examiner`)
- ✅ **Visual role selection** with JavaScript
- ✅ **Proper form validation** for role assignment

## 🧪 Testing After Update

1. **Test Examiner Signup:**
   - Go to your production URL
   - Click "Get Started" under "For Examiners"
   - Verify "Examiner" role is pre-selected
   - Complete signup and verify user has EXAMINER role

2. **Test Examinee Signup:**
   - Click "Join Now" under "For Students"
   - Verify "Examinee" role is pre-selected
   - Complete signup and verify user has EXAMINEE role

3. **Test Direct URL:**
   - Visit `/accounts/signup/?role=examiner`
   - Verify Examiner role is selected
   - Visit `/accounts/signup/?role=examinee`
   - Verify Examinee role is selected

## 🚨 Troubleshooting

### If the update fails:

1. **Check service status:**
   ```bash
   sudo systemctl status mcq-exam
   ```

2. **Check logs:**
   ```bash
   sudo journalctl -u mcq-exam -n 50
   ```

3. **Restore from backup:**
   ```bash
   # Find your backup
   ls -la /var/backups/mcq-exam/
   
   # Restore code (if needed)
   cd /var/www/mcq-exam
   sudo tar -xzf /var/backups/mcq-exam/code_backup_YYYYMMDD_HHMMSS.tar.gz
   
   # Restore database (if needed)
   sudo -u postgres psql mcq_exam_db < /var/backups/mcq-exam/database_backup_YYYYMMDD_HHMMSS.sql
   ```

4. **Manual restart:**
   ```bash
   sudo systemctl restart mcq-exam
   sudo systemctl restart nginx
   ```

## 📞 Support

If you encounter any issues:
1. Check the logs first
2. Verify all services are running
3. Test the application functionality
4. Check database connectivity

The update should be smooth and take only a few minutes! 🎉
