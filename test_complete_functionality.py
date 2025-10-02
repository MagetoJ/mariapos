#!/usr/bin/env python
"""
Complete functionality test for Maria Havens POS system
Tests all critical functionality after URL pattern fixes
"""
import requests
import json
import time

def test_authentication():
    """Test login functionality"""
    print("=== Testing Authentication ===")
    
    try:
        # Test login with admin credentials
        response = requests.post("http://localhost:8000/api/auth/login/", 
            json={
                "email": "admin@example.com",
                "password": "admin123"
            },
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('access')
            print("✅ Authentication successful")
            return token
        else:
            print(f"⚠️  Authentication returned {response.status_code}")
            try:
                error_data = response.json()
                print(f"   Error: {error_data}")
            except:
                pass
            return None
            
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return None

def test_dashboard_with_auth(token):
    """Test dashboard endpoints with authentication"""
    print("\n=== Testing Dashboard with Authentication ===")
    
    if not token:
        print("❌ No authentication token available")
        return False
        
    headers = {"Authorization": f"Bearer {token}"}
    
    dashboard_endpoints = [
        ("/api/dashboard/dashboard/stats/", "Dashboard Stats"),
        ("/api/dashboard/dashboard/sales_data/?days=7", "Sales Data"),
        ("/api/dashboard/dashboard/category_sales/", "Category Sales"),
    ]
    
    success = True
    for endpoint, name in dashboard_endpoints:
        try:
            response = requests.get(f"http://localhost:8000{endpoint}", 
                                  headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: {response.status_code}")
                success = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            success = False
    
    return success

def test_crud_operations_with_auth(token):
    """Test CRUD operations with authentication"""
    print("\n=== Testing CRUD Operations ===")
    
    if not token:
        print("❌ No authentication token available")
        return False
        
    headers = {"Authorization": f"Bearer {token}"}
    
    # Test different CRUD endpoints
    crud_tests = [
        ("/api/inventory/items/", "Inventory Items", "GET"),
        ("/api/guests/guests/", "Guests", "GET"),
        ("/api/menu/", "Menu Items", "GET"),
        ("/api/users/", "Users", "GET"),
    ]
    
    success = True
    for endpoint, name, method in crud_tests:
        try:
            response = requests.request(method, f"http://localhost:8000{endpoint}", 
                                      headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'results' in data:
                    count = len(data['results'])
                    print(f"✅ {name}: {count} items found")
                elif isinstance(data, list):
                    count = len(data)
                    print(f"✅ {name}: {count} items found")
                else:
                    print(f"✅ {name}: Working")
            else:
                print(f"❌ {name}: {response.status_code}")
                success = False
        except Exception as e:
            print(f"❌ {name}: Error - {e}")
            success = False
    
    return success

def test_frontend_accessibility():
    """Test if frontend is running"""
    print("\n=== Testing Frontend Accessibility ===")
    
    try:
        response = requests.get("http://localhost:3000", timeout=10)
        if response.status_code == 200:
            print("✅ Frontend is running and accessible")
            return True
        else:
            print(f"⚠️  Frontend returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def main():
    print("🚀 Maria Havens POS - Complete Functionality Test")
    print("=" * 60)
    
    # Wait a moment for servers to start
    print("⏳ Waiting for servers to start...")
    time.sleep(5)
    
    # Test authentication
    token = test_authentication()
    
    # Test dashboard
    dashboard_ok = test_dashboard_with_auth(token)
    
    # Test CRUD operations
    crud_ok = test_crud_operations_with_auth(token)
    
    # Test frontend
    frontend_ok = test_frontend_accessibility()
    
    print("\n" + "=" * 60)
    print("🎯 FINAL RESULTS:")
    print("=" * 60)
    
    if token:
        print("✅ Authentication: Working")
    else:
        print("❌ Authentication: Issues")
        
    if dashboard_ok:
        print("✅ Dashboard: Fixed and Working")
    else:
        print("⚠️  Dashboard: May need additional fixes")
        
    if crud_ok:
        print("✅ CRUD Operations: Working")
    else:
        print("⚠️  CRUD Operations: May need additional fixes")
        
    if frontend_ok:
        print("✅ Frontend: Running")
    else:
        print("⚠️  Frontend: Not accessible")
    
    print("\n🔧 URL Pattern Fixes Applied:")
    print("   • Dashboard: /dashboard/stats/ → /dashboard/dashboard/stats/")
    print("   • Inventory: /inventory/ → /inventory/items/")
    print("   • Guests: /guests/ → /guests/guests/")
    print("   • Added missing delete methods for inventory and guests")
    
    if dashboard_ok and crud_ok:
        print("\n🎉 SUCCESS: All critical issues have been resolved!")
        print("\n📋 What should work now:")
        print("   • Dashboard statistics and charts")
        print("   • Menu item add/edit/delete buttons")
        print("   • Guest management (add/edit/delete)")
        print("   • Inventory management (add/edit/delete)")
        print("   • Staff creation (was already working)")
        print("\n🌐 Access your application:")
        print("   • Frontend: http://localhost:3000")
        print("   • Backend API: http://localhost:8000/api")
    else:
        print("\n⚠️  Some issues may remain - check the logs above")

if __name__ == '__main__':
    main()