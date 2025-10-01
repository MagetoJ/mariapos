# PowerShell Script to Set Django Environment Variables
# Run this script with: .\setup-django-env.ps1

Write-Host "Setting up Django environment variables..." -ForegroundColor Green

# Django Core Settings
$env:SECRET_KEY = "django-insecure-your-secret-key-here-generate-new-one-for-production"
$env:DEBUG = "True"
$env:ALLOWED_HOSTS = "localhost,127.0.0.1,0.0.0.0"

# CORS Settings
$env:CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
$env:CORS_ALLOW_CREDENTIALS = "True"

# Database Configuration (PostgreSQL)
$env:DATABASE_URL = "postgresql://username:password@localhost:5432/mariahavens_pos"

# Alternative Database Settings
$env:DB_ENGINE = "django.db.backends.postgresql"
$env:DB_NAME = "mariahavens_pos"
$env:DB_USER = "your_db_user"
$env:DB_PASSWORD = "your_db_password"
$env:DB_HOST = "localhost"
$env:DB_PORT = "5432"

# JWT Configuration
$env:JWT_SECRET_KEY = "your-jwt-secret-key-here-make-it-long-and-random"
$env:JWT_ACCESS_TOKEN_LIFETIME = "3600"
$env:JWT_REFRESH_TOKEN_LIFETIME = "86400"

# Redis Configuration
$env:REDIS_URL = "redis://localhost:6379/0"

# Email Configuration
$env:EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST = "smtp.gmail.com"
$env:EMAIL_PORT = "587"
$env:EMAIL_USE_TLS = "True"
$env:EMAIL_HOST_USER = "your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD = "your-app-password"

# File Upload Settings
$env:MAX_UPLOAD_SIZE = "5242880"
$env:ALLOWED_FILE_TYPES = "jpg,jpeg,png,gif,pdf"

# API Rate Limiting
$env:API_THROTTLE_RATE_ANON = "100/hour"
$env:API_THROTTLE_RATE_USER = "1000/hour"

# Logging
$env:LOG_LEVEL = "INFO"

# Localization
$env:TIME_ZONE = "Africa/Nairobi"
$env:LANGUAGE_CODE = "en-us"

# Security Settings (for development)
$env:SECURE_SSL_REDIRECT = "False"
$env:SESSION_COOKIE_SECURE = "False"
$env:CSRF_COOKIE_SECURE = "False"
$env:SECURE_BROWSER_XSS_FILTER = "True"
$env:SECURE_CONTENT_TYPE_NOSNIFF = "True"

Write-Host "Django environment variables have been set!" -ForegroundColor Green
Write-Host ""
Write-Host "To use these variables:" -ForegroundColor Yellow
Write-Host "1. Run: .\setup-django-env.ps1" -ForegroundColor Cyan
Write-Host "2. Then start your Django server: python manage.py runserver" -ForegroundColor Cyan
Write-Host ""
Write-Host "Remember to:" -ForegroundColor Yellow
Write-Host "- Update DATABASE_URL with your actual database credentials" -ForegroundColor White
Write-Host "- Generate a new SECRET_KEY for production" -ForegroundColor White
Write-Host "- Set DEBUG=False in production" -ForegroundColor White
Write-Host "- Update email configuration with your SMTP details" -ForegroundColor White

# Display current environment variables for verification
Write-Host ""
Write-Host "Current Django Environment Variables:" -ForegroundColor Magenta
Write-Host "SECRET_KEY: $($env:SECRET_KEY.Substring(0, 20))..." -ForegroundColor Gray
Write-Host "DEBUG: $env:DEBUG" -ForegroundColor Gray
Write-Host "DATABASE_URL: $env:DATABASE_URL" -ForegroundColor Gray
Write-Host "CORS_ALLOWED_ORIGINS: $env:CORS_ALLOWED_ORIGINS" -ForegroundColor Gray