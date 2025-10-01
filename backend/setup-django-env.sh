#!/bin/bash

# Setup Django Environment Variables
# Run this script with: source ./setup-django-env.sh

echo "Setting up Django environment variables..."

# Django Core Settings
export SECRET_KEY="django-insecure-your-secret-key-here-generate-new-one-for-production"
export DEBUG=True
export ALLOWED_HOSTS="localhost,127.0.0.1,0.0.0.0"

# CORS Settings
export CORS_ALLOWED_ORIGINS="http://localhost:3000,http://127.0.0.1:3000"
export CORS_ALLOW_CREDENTIALS=True

# Database Configuration (PostgreSQL)
export DATABASE_URL="postgresql://username:password@localhost:5432/mariahavens_pos"

# Alternative Database Settings
export DB_ENGINE="django.db.backends.postgresql"
export DB_NAME="mariahavens_pos"
export DB_USER="your_db_user"
export DB_PASSWORD="your_db_password"
export DB_HOST="localhost"
export DB_PORT="5432"

# JWT Configuration
export JWT_SECRET_KEY="your-jwt-secret-key-here-make-it-long-and-random"
export JWT_ACCESS_TOKEN_LIFETIME=3600
export JWT_REFRESH_TOKEN_LIFETIME=86400

# Redis Configuration
export REDIS_URL="redis://localhost:6379/0"

# Email Configuration
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
export EMAIL_HOST="smtp.gmail.com"
export EMAIL_PORT=587
export EMAIL_USE_TLS=True
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="your-app-password"

# File Upload Settings
export MAX_UPLOAD_SIZE=5242880
export ALLOWED_FILE_TYPES="jpg,jpeg,png,gif,pdf"

# API Rate Limiting
export API_THROTTLE_RATE_ANON="100/hour"
export API_THROTTLE_RATE_USER="1000/hour"

# Logging
export LOG_LEVEL="INFO"

# Localization
export TIME_ZONE="Africa/Nairobi"
export LANGUAGE_CODE="en-us"

# Security Settings (for development)
export SECURE_SSL_REDIRECT=False
export SESSION_COOKIE_SECURE=False
export CSRF_COOKIE_SECURE=False
export SECURE_BROWSER_XSS_FILTER=True
export SECURE_CONTENT_TYPE_NOSNIFF=True

echo "Django environment variables have been set!"
echo ""
echo "To use these variables:"
echo "1. Run: source ./setup-django-env.sh"
echo "2. Then start your Django server: python manage.py runserver"
echo ""
echo "Remember to:"
echo "- Update DATABASE_URL with your actual database credentials"
echo "- Generate a new SECRET_KEY for production"
echo "- Set DEBUG=False in production"
echo "- Update email configuration with your SMTP details"