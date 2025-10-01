#!/usr/bin/env python3
"""
Test script for image upload functionality
"""
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
LOGIN_URL = f"{BASE_URL}/api/auth/login/"
CATEGORY_URL = f"{BASE_URL}/api/menu/categories/"

# Login credentials
credentials = {
    "email": "admin@mariahavens.com",
    "password": "admin123"
}

def get_auth_token():
    """Get authentication token"""
    response = requests.post(LOGIN_URL, json=credentials)
    response.raise_for_status()
    return response.json()["access"]

def test_category_image_upload():
    """Test category image upload"""
    try:
        # Get auth token
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get categories
        response = requests.get(CATEGORY_URL, headers=headers)
        response.raise_for_status()
        categories = response.json()["results"]
        
        if not categories:
            print("No categories found")
            return
            
        # Test uploading image to first category
        category_id = categories[0]["id"]
        category_name = categories[0]["name"]
        upload_url = f"{CATEGORY_URL}{category_id}/upload-image/"
        
        print(f"Testing image upload for category: {category_name} (ID: {category_id})")
        
        # Upload image
        with open("test_images/appetizer_test.jpg", "rb") as f:
            files = {"image": f}
            response = requests.post(upload_url, headers=headers, files=files)
            
        print(f"Upload response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Upload successful!")
            print(f"Image URL: {result.get('image_url')}")
        else:
            print(f"Upload failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

def test_menu_item_image_upload():
    """Test menu item image upload"""
    try:
        # Get auth token
        token = get_auth_token()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Get menu items
        response = requests.get(f"{BASE_URL}/api/menu/", headers=headers)
        response.raise_for_status()
        menu_items = response.json()["results"]
        
        if not menu_items:
            print("No menu items found")
            return
            
        # Test uploading image to first menu item
        item_id = menu_items[0]["id"]
        item_name = menu_items[0]["name"]
        upload_url = f"{BASE_URL}/api/menu/{item_id}/upload-image/"
        
        print(f"Testing image upload for menu item: {item_name} (ID: {item_id})")
        
        # Upload image
        with open("test_images/appetizer_test.jpg", "rb") as f:
            files = {"image": f}
            response = requests.post(upload_url, headers=headers, files=files)
            
        print(f"Upload response status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print("Upload successful!")
            print(f"Image URL: {result.get('image_url')}")
        else:
            print(f"Upload failed: {response.text}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    print("=== Testing Image Upload Functionality ===")
    print("\n1. Testing Category Image Upload:")
    test_category_image_upload()
    
    print("\n2. Testing Menu Item Image Upload:")
    test_menu_item_image_upload()