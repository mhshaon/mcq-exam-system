#!/bin/bash

# Database setup script for MCQ Exam System
# Run this script to properly configure PostgreSQL for Django

set -e

echo "🗄️ Setting up PostgreSQL database for MCQ Exam System..."

# Get database credentials
read -p "Enter database name (default: mcq_exam_db): " DB_NAME
DB_NAME=${DB_NAME:-mcq_exam_db}

read -p "Enter database user (default: mcq_user): " DB_USER
DB_USER=${DB_USER:-mcq_user}

read -s -p "Enter database password: " DB_PASSWORD
echo

# Connect to PostgreSQL and create database/user
sudo -u postgres psql << EOF
-- Create database
CREATE DATABASE $DB_NAME;

-- Create user with password
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

-- Grant all privileges
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
GRANT ALL PRIVILEGES ON SCHEMA public TO $DB_USER;
ALTER USER $DB_USER CREATEDB;

-- Grant privileges on existing tables (if any)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO $DB_USER;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO $DB_USER;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO $DB_USER;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO $DB_USER;

-- Exit
\q
EOF

echo "✅ Database setup completed!"
echo "📝 Database credentials:"
echo "   Database: $DB_NAME"
echo "   User: $DB_USER"
echo "   Password: [hidden]"

echo ""
echo "🔧 Add these to your .env file:"
echo "DB_NAME=$DB_NAME"
echo "DB_USER=$DB_USER"
echo "DB_PASSWORD=$DB_PASSWORD"
echo "DB_HOST=localhost"
echo "DB_PORT=5432"

echo ""
echo "🚀 Now you can run migrations:"
echo "python manage.py migrate"
