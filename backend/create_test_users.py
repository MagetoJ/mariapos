#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mariahavens_pos_backend.settings')
django.setup()

from accounts.models import User

# Create test users if they don't exist
users_to_create = [
    {'email': 'manager@mariahavens.com', 'password': 'manager123', 'name': 'Manager User', 'role': 'manager'},
    {'email': 'waiter1@mariahavens.com', 'password': 'waiter123', 'name': 'Waiter One', 'role': 'waiter'},
    {'email': 'kitchen@mariahavens.com', 'password': 'kitchen123', 'name': 'Kitchen Staff', 'role': 'kitchen'},
    {'email': 'cashier@mariahavens.com', 'password': 'cashier123', 'name': 'Cashier User', 'role': 'cashier'},
    {'email': 'reception@mariahavens.com', 'password': 'reception123', 'name': 'Reception Staff', 'role': 'receptionist'},
]

for user_data in users_to_create:
    user, created = User.objects.get_or_create(
        email=user_data['email'],
        defaults={
            'name': user_data['name'],
            'role': user_data['role']
        }
    )
    if created:
        user.set_password(user_data['password'])
        user.save()
        print(f"Created user: {user_data['email']}")
    else:
        print(f"User already exists: {user_data['email']}")

print("Test users setup complete!")