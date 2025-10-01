#!/usr/bin/env python
import requests
import json

# Test the Django API endpoints
BASE_URL = 'http://localhost:8000/api'

def test_api():
    print("Testing Django API endpoints...")
    
    # Test login
    print("\n1. Testing login...")
    login_data = {
        'email': 'admin@mariahavens.com',
        'password': 'admin123'
    }
    
    try:
        response = requests.post(f'{BASE_URL}/auth/login/', json=login_data)
        print(f"Login status: {response.status_code}")
        if response.status_code == 200:
            auth_data = response.json()
            token = auth_data.get('access')
            print("Login successful!")
            
            # Test menu endpoints
            print("\n2. Testing menu endpoints...")
            headers = {'Authorization': f'Bearer {token}'}
            
            # Get menu items
            response = requests.get(f'{BASE_URL}/menu/', headers=headers)
            print(f"Get menu items status: {response.status_code}")
            if response.status_code == 200:
                menu_items = response.json()
                print(f"Found {len(menu_items)} menu items")
                for item in menu_items[:3]:  # Show first 3 items
                    print(f"  - {item.get('name', 'N/A')}: ${item.get('price', 'N/A')}")
            
            # Get categories
            response = requests.get(f'{BASE_URL}/menu/categories/', headers=headers)
            print(f"Get categories status: {response.status_code}")
            if response.status_code == 200:
                categories = response.json()
                print(f"Found {len(categories)} categories")
                for cat in categories:
                    print(f"  - {cat.get('name', 'N/A')}")
                    
        else:
            print("Login failed:", response.text)
            
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to Django server. Make sure it's running on localhost:8000")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()