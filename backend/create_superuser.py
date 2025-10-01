#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mariahavens_pos_backend.settings')
django.setup()

from accounts.models import User

# Create superuser
try:
    admin = User.objects.get(email='admin@mariahavens.com')
    print("Superuser already exists")
except User.DoesNotExist:
    User.objects.create_superuser(
        email='admin@mariahavens.com',
        password='admin123',
        name='Admin User',
        role='admin'
    )
    print("Superuser created successfully")