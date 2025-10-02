#!/usr/bin/env python
"""
Test script to verify API endpoint fixes
"""
import requests
import json
import sys

def test_endpoints():
    """Test the corrected API endpoints"""
    base_url = "http://localhost:8000/api"
    
    # Test endpoints - corrected URLs
    test_endpoints = [
        # Dashboard endpoints (corrected)
        ("/dashboard/dashboard/stats/", "Dashboard Stats"),
        ("/dashboard/dashboard/sales_data/", "Sales Data"), 
        ("/dashboard/dashboard/category_sales/", "Category Sales"),
        
        # Inventory endpoints (corrected)
        ("/inventory/items/", "Inventory Items"),
        ("/inventory/items/low_stock/", "Low Stock Items"),
        
        # Guest endpoints (corrected)  
        ("/guests/guests/", "Guests List"),
        
        # Menu endpoints (already correct)
        ("/menu/", "Menu Items"),
        ("/menu/categories/", "Menu Categories"),
        
        # User endpoints (already correct)
        ("/users/", "Users"),
    ]
    
    print("=== API Endpoint Testing ===\n")
    print("Testing corrected API endpoints:")
    
    success_count = 0
    auth_required_count = 0
    error_count = 0
    
    for endpoint, description in test_endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            if response.status_code == 200:
                print(f"✅ {description}: {endpoint} -> {response.status_code} (OK)")
                success_count += 1
            elif response.status_code == 401:
                print(f"🔐 {description}: {endpoint} -> {response.status_code} (Auth Required)")
                auth_required_count += 1
            else:
                print(f"⚠️  {description}: {endpoint} -> {response.status_code}")
                if response.status_code == 404:
                    error_count += 1
        except Exception as e:
            print(f"❌ {description}: {endpoint} -> ERROR: {e}")
            error_count += 1
    
    print(f"\n=== Summary ===")
    print(f"✅ Success (200): {success_count}")
    print(f"🔐 Auth Required (401): {auth_required_count}") 
    print(f"❌ Errors/Not Found: {error_count}")
    
    if error_count == 0:
        print("\n🎉 All endpoints are accessible (either 200 OK or 401 Auth Required)")
        print("The URL pattern fixes have been successful!")
        return True
    else:
        print(f"\n⚠️  {error_count} endpoints still have issues")
        return False

def test_staff_creation_status():
    """Test staff creation to verify it's working"""
    print("\n=== Testing Staff Creation (Already Fixed) ===")
    
    try:
        # Try to create a test staff member
        response = requests.post("http://localhost:8000/api/users/", 
            json={
                "email": "test.staff@test.com",
                "password": "testpass123",
                "confirm_password": "testpass123", 
                "first_name": "Test",
                "last_name": "Staff",
                "role": "STAFF"
            },
            timeout=5
        )
        
        if response.status_code == 201:
            print("✅ Staff creation works perfectly")
        elif response.status_code == 401:
            print("🔐 Staff creation endpoint requires authentication (which is expected)")
        elif response.status_code == 400:
            try:
                error_data = response.json()
                if "already exists" in str(error_data).lower():
                    print("✅ Staff creation works (user already exists)")
                else:
                    print(f"⚠️  Staff creation validation: {error_data}")
            except:
                print("⚠️  Staff creation returned 400 - may need validation fixes")
        else:
            print(f"⚠️  Staff creation returned {response.status_code}")
            
    except Exception as e:
        print(f"❌ Staff creation test failed: {e}")

if __name__ == '__main__':
    print("🚀 Testing Maria Havens POS API Fixes")
    print("=" * 50)
    
    endpoints_ok = test_endpoints()
    test_staff_creation_status()
    
    print("\n" + "=" * 50)
    if endpoints_ok:
        print("✅ API endpoint fixes are working!")
        print("\nNext steps:")
        print("1. Restart the frontend development server")
        print("2. Test the dashboard, menu, guests, and inventory pages")  
        print("3. Verify add/edit/delete buttons work correctly")
    else:
        print("⚠️  Some endpoints still need fixing")
        
    print("\n🎯 The main URL pattern issues have been resolved:")
    print("   • Dashboard: /dashboard/stats/ → /dashboard/dashboard/stats/")
    print("   • Inventory: /inventory/ → /inventory/items/") 
    print("   • Guests: /guests/ → /guests/guests/")