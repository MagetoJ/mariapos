# Environment Variables Setup for Maria Havens POS

This document explains how to set up environment variables for both the frontend (Next.js) and backend (Django) components of the Maria Havens POS system.

## Frontend Environment Variables

### 1. Next.js Environment File

The frontend uses `.env.local` file to configure connection to the Django backend:

```bash
# Django Backend API URL
NEXT_PUBLIC_API_URL=http://localhost:8000/api

# JWT Token Configuration (used by frontend)
NEXT_PUBLIC_JWT_SECRET=your-frontend-jwt-secret-key-here

# App Configuration
NEXT_PUBLIC_APP_NAME=Maria Havens POS
NEXT_PUBLIC_APP_VERSION=1.0.0
NEXT_PUBLIC_ENVIRONMENT=development
```

### 2. Frontend Setup Steps

1. The `.env.local` file has been created in the project root
2. Update the `NEXT_PUBLIC_API_URL` if your Django backend runs on a different port
3. Start the development server:
   ```bash
   npm run dev
   # or
   pnpm dev
   ```

## Django Backend Environment Variables

### 1. Environment Files Created

- `.env.django` - Template for Django environment variables
- `setup-django-env.sh` - Bash script for Unix/Linux/Mac
- `setup-django-env.ps1` - PowerShell script for Windows
- `django-settings-example.py` - Example Django settings configuration

### 2. Backend Setup Steps (for Django project)

#### Option A: Using .env file (Recommended)
1. Copy `.env.django` to your Django project root
2. Rename it to `.env`
3. Update the values with your actual configuration
4. Install python-decouple: `pip install python-decouple`
5. Use the settings example provided in `django-settings-example.py`

#### Option B: Using Shell Scripts

**For Windows (PowerShell):**
```powershell
# Set execution policy if needed
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Run the setup script
.\setup-django-env.ps1

# Start Django development server
python manage.py runserver
```

**For Unix/Linux/Mac (Bash):**
```bash
# Make script executable
chmod +x setup-django-env.sh

# Source the script to set environment variables
source ./setup-django-env.sh

# Start Django development server
python manage.py runserver
```

### 3. Key Environment Variables Explained

#### Essential Django Settings
- `SECRET_KEY`: Django secret key (generate a new one for production)
- `DEBUG`: Debug mode (True for development, False for production)
- `ALLOWED_HOSTS`: Comma-separated list of allowed hosts
- `DATABASE_URL`: Complete database URL or individual DB settings

#### CORS Configuration
- `CORS_ALLOWED_ORIGINS`: Frontend URLs that can access the API
- `CORS_ALLOW_CREDENTIALS`: Allow credentials in CORS requests

#### JWT Authentication
- `JWT_SECRET_KEY`: Secret key for JWT token signing
- `JWT_ACCESS_TOKEN_LIFETIME`: Access token expiry time in seconds
- `JWT_REFRESH_TOKEN_LIFETIME`: Refresh token expiry time in seconds

#### Database Configuration
```bash
# Option 1: Single DATABASE_URL
DATABASE_URL=postgresql://username:password@localhost:5432/mariahavens_pos

# Option 2: Individual settings
DB_ENGINE=django.db.backends.postgresql
DB_NAME=mariahavens_pos
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432
```

### 4. Database Setup

#### PostgreSQL (Recommended)
```bash
# Install PostgreSQL and create database
createdb mariahavens_pos

# Install Python PostgreSQL adapter
pip install psycopg2-binary

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

#### SQLite (Development)
```bash
# For SQLite, just set:
DATABASE_URL=sqlite:///db.sqlite3

# Run migrations
python manage.py makemigrations
python manage.py migrate
```

### 5. Production Considerations

#### Security Settings for Production
```bash
DEBUG=False
SECRET_KEY=generate-a-new-secure-secret-key
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
```

#### Database for Production
- Use PostgreSQL or MySQL instead of SQLite
- Use connection pooling
- Set up database backups

#### Email Configuration
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### 6. Required Django Packages

Add these to your Django requirements.txt:
```
Django>=4.2.0
djangorestframework
djangorestframework-simplejwt
django-cors-headers
django-filter
dj-database-url
python-decouple  # for .env file support
psycopg2-binary  # for PostgreSQL
redis  # for caching (optional)
```

### 7. Integration Steps

1. Set up the Django backend with the environment variables
2. Create the API endpoints as documented in `DJANGO_API_DOCUMENTATION.md`
3. Update the frontend `data-service.ts` to use real API calls instead of mock data
4. Test the integration between frontend and backend

### 8. Testing the Setup

#### Test Frontend Environment
```bash
# Check if environment variables are loaded
npm run dev

# The console should show the API URL when making requests
```

#### Test Backend Environment
```bash
# Check Django can access environment variables
python manage.py shell

# In the Django shell:
from django.conf import settings
print(settings.SECRET_KEY)
print(settings.DEBUG)
print(settings.DATABASES)
```

### 9. Troubleshooting

#### Common Issues

1. **CORS Errors**: Ensure `CORS_ALLOWED_ORIGINS` includes your frontend URL
2. **Database Connection**: Verify database credentials and server status
3. **JWT Issues**: Ensure JWT secret keys match between frontend and backend
4. **File Uploads**: Check `MEDIA_URL` and `MEDIA_ROOT` settings
5. **Static Files**: Configure `STATIC_URL` and `STATIC_ROOT` for production

#### Environment Variable Priority
1. System environment variables
2. .env file (if using python-decouple)
3. Default values in settings.py

---

## Quick Start Commands

### Frontend
```bash
# Start frontend development server
npm run dev
```

### Backend (after setting up Django project)
```bash
# Set environment variables (Windows)
.\setup-django-env.ps1

# Set environment variables (Unix/Linux/Mac)
source ./setup-django-env.sh

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

Both servers should now be running and able to communicate with each other!