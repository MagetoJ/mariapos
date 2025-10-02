#!/usr/bin/env python3
"""
Test script to verify dashboard endpoints
"""

import requests
import json

# API base URL
API_BASE = "http://localhost:8000/api"

def test_dashboard_endpoints():
    """Test all dashboard endpoints"""
    print("🧪 Testing Dashboard Endpoints...")
    
    # Login as admin
    login_data = {
        "email": "admin@mariahavens.com",
        "password": "admin123"
    }
    
    print(f"🔐 Logging in as admin...")
    login_response = requests.post(f"{API_BASE}/auth/login/", json=login_data)
    
    if login_response.status_code != 200:
        print(f"❌ Login failed: {login_response.status_code}")
        return
    
    token = login_response.json().get('access')
    headers = {'Authorization': f'Bearer {token}'}
    print(f"✅ Login successful!")
    
    # Test dashboard endpoints
    endpoints = [
        "/dashboard/stats/",
        "/dashboard/sales/?days=7",
        "/dashboard/category-sales/",
        "/users/",
        "/menu/",
        "/inventory/",
        "/inventory/low-stock/",
        "/orders/",
        "/service-requests/",
        "/guests/"
    ]
    
    for endpoint in endpoints:
        print(f"\n📊 Testing {endpoint}")
        try:
            response = requests.get(f"{API_BASE}{endpoint}", headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, list):
                    print(f"✅ Success! Returned {len(data)} items")
                elif isinstance(data, dict):
                    print(f"✅ Success! Returned data keys: {list(data.keys())}")
                else:
                    print(f"✅ Success! Returned: {type(data)}")
            else:
                print(f"❌ Failed: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_dashboard_endpoints()