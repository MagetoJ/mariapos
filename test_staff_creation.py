#!/usr/bin/env python3
"""
Test script to verify staff creation functionality
"""

import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api"

def test_staff_creation():
    """Test staff member creation"""
    print("🧪 Testing Staff Creation...")
    
    # First, let's try to login as admin to get a token
    login_data = {
        "email": "admin@mariahavens.com",
        "password": "admin123"
    }
    
    print(f"🔐 Logging in as admin...")
    login_response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        print(f"Response: {login_response.text}")
        return
    
    login_result = login_response.json()
    token = login_result.get('access')
    print(f"✅ Login successful! Token obtained.")
    
    # Now test staff creation
    headers = {'Authorization': f'Bearer {token}'}
    
    staff_data = {
        "name": "Test Waiter",
        "email": "test.waiter@mariahavens.com",
        "password": "testpass123",
        "confirm_password": "testpass123",
        "role": "waiter",
        "isActive": True
    }
    
    print(f"👥 Creating staff member...")
    create_response = requests.post(f"{API_BASE}/users/", json=staff_data, headers=headers)
    
    print(f"Status: {create_response.status_code}")
    print(f"Response: {create_response.text}")
    
    if create_response.status_code == 201:
        print("✅ Staff creation successful!")
        created_staff = create_response.json()
        print(f"Created staff: {created_staff['name']} ({created_staff['email']})")
        
        # Clean up - delete the created user
        user_id = created_staff['id']
        delete_response = requests.delete(f"{API_BASE}/users/{user_id}/", headers=headers)
        print(f"🗑️ Cleanup: {delete_response.status_code}")
    else:
        print(f"❌ Staff creation failed!")
        try:
            error_data = create_response.json()
            print(f"Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"Raw response: {create_response.text}")

if __name__ == "__main__":
    test_staff_creation()