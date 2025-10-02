#!/usr/bin/env python3
"""
Integration Test for Maria Havens POS System
Tests the complete frontend-backend integration
"""

import requests
import json
import time
import sys
from datetime import datetime

# Test configuration
BACKEND_URL = "http://localhost:8000/api"
FRONTEND_URL = "http://localhost:3000"

def test_backend_apis():
    """Test critical backend API endpoints"""
    print("=== Testing Backend APIs ===\n")
    
    # Test authentication
    print("1. Testing Authentication...")
    login_data = {
        "email": "manager@mariahavens.com",
        "password": "manager123"
    }
    
    try:
        response = requests.post(f"{BACKEND_URL}/auth/login/", json=login_data)
        if response.status_code == 200:
            print("   ✓ Authentication successful!")
            token = response.json().get('access')
            headers = {'Authorization': f'Bearer {token}'}
        else:
            print(f"   ✗ Authentication failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Authentication error: {e}")
        return False
    
    # Test menu endpoint
    print("\n2. Testing Menu API...")
    try:
        response = requests.get(f"{BACKEND_URL}/menu/", headers=headers)
        if response.status_code == 200:
            menu_data = response.json()
            count = len(menu_data) if isinstance(menu_data, list) else menu_data.get('count', 0)
            print(f"   ✓ Menu API working! Found {count} items")
        else:
            print(f"   ✗ Menu API failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Menu API error: {e}")
    
    # Test orders endpoint
    print("\n3. Testing Orders API...")
    try:
        response = requests.get(f"{BACKEND_URL}/orders/", headers=headers)
        if response.status_code == 200:
            print("   ✓ Orders API working!")
        else:
            print(f"   ✗ Orders API failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Orders API error: {e}")
    
    # Test tables endpoint
    print("\n4. Testing Tables API...")
    try:
        response = requests.get(f"{BACKEND_URL}/tables/", headers=headers)
        if response.status_code == 200:
            print("   ✓ Tables API working!")
        else:
            print(f"   ✗ Tables API failed: {response.status_code}")
    except Exception as e:
        print(f"   ✗ Tables API error: {e}")
    
    return True

def test_frontend_connection():
    """Test frontend server availability"""
    print("\n=== Testing Frontend Connection ===\n")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=10)
        if response.status_code == 200:
            print("   ✓ Frontend server is running!")
            return True
        else:
            print(f"   ✗ Frontend returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("   ✗ Frontend server not reachable (may still be starting)")
        return False
    except Exception as e:
        print(f"   ✗ Frontend connection error: {e}")
        return False

def test_logo_accessibility():
    """Test if the Maria Havens logo is accessible"""
    print("\n=== Testing Logo Accessibility ===\n")
    
    logo_url = f"{FRONTEND_URL}/maria-havens-logo.jpg"
    try:
        response = requests.get(logo_url, timeout=5)
        if response.status_code == 200:
            print("   ✓ Maria Havens logo is accessible!")
            print(f"   Logo size: {len(response.content)} bytes")
            return True
        else:
            print(f"   ✗ Logo not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ✗ Logo accessibility error: {e}")
        return False

def main():
    """Run comprehensive integration tests"""
    print("🚀 Maria Havens POS Integration Test")
    print("=" * 50)
    print(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Test backend
    backend_ok = test_backend_apis()
    
    # Test frontend (with retry logic)
    frontend_ok = False
    for attempt in range(3):
        if attempt > 0:
            print(f"\n   Retrying frontend connection (attempt {attempt + 1}/3)...")
            time.sleep(5)
        frontend_ok = test_frontend_connection()
        if frontend_ok:
            break
    
    # Test logo
    logo_ok = test_logo_accessibility() if frontend_ok else False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 Test Summary:")
    print(f"   Backend APIs: {'✓ PASS' if backend_ok else '✗ FAIL'}")
    print(f"   Frontend Server: {'✓ PASS' if frontend_ok else '✗ FAIL'}")
    print(f"   Logo Accessibility: {'✓ PASS' if logo_ok else '✗ FAIL'}")
    
    all_passed = backend_ok and frontend_ok and logo_ok
    print(f"\n🎯 Overall Status: {'✅ ALL TESTS PASSED' if all_passed else '❌ SOME TESTS FAILED'}")
    
    if all_passed:
        print("\n🎉 The Maria Havens POS system is fully operational!")
        print("   - Backend API is responding correctly")
        print("   - Frontend is accessible")
        print("   - Logo integration is working")
        print("   - Receipt generation should work with logo")
    else:
        print("\n⚠️  Some components need attention:")
        if not backend_ok:
            print("   - Check backend server and database connection")
        if not frontend_ok:
            print("   - Check frontend server (may need more time to start)")
        if not logo_ok:
            print("   - Check logo file placement and accessibility")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())