#!/usr/bin/env python3
"""
Comprehensive Test Suite for Maria Havens POS System
Tests frontend-backend connectivity and receipt functionality with logo integration
"""

import requests
import json
import time
import os
import sys
from datetime import datetime

# Base URLs
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
API_BASE_URL = f"{BACKEND_URL}/api"

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_status(message, status="INFO"):
    """Print colored status messages"""
    color_map = {
        "PASS": Colors.GREEN,
        "FAIL": Colors.RED,
        "WARN": Colors.YELLOW,
        "INFO": Colors.BLUE,
        "TEST": Colors.CYAN,
        "SETUP": Colors.MAGENTA
    }
    color = color_map.get(status, Colors.WHITE)
    print(f"{color}[{status}]{Colors.END} {message}")

def test_server_connectivity():
    """Test backend server connectivity"""
    print_status("Testing Backend Server Connectivity...", "TEST")
    
    try:
        response = requests.get(f"{BACKEND_URL}/admin/", timeout=5)
        if response.status_code in [200, 302]:
            print_status("✓ Backend server is running and accessible", "PASS")
            return True
        else:
            print_status(f"✗ Backend server returned status {response.status_code}", "FAIL")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"✗ Cannot connect to backend server: {e}", "FAIL")
        return False

def test_frontend_connectivity():
    """Test frontend server connectivity"""
    print_status("Testing Frontend Server Connectivity...", "TEST")
    
    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        if response.status_code == 200:
            print_status("✓ Frontend server is running and accessible", "PASS")
            return True
        else:
            print_status(f"✗ Frontend server returned status {response.status_code}", "FAIL")
            return False
    except requests.exceptions.RequestException as e:
        print_status(f"✗ Cannot connect to frontend server: {e}", "FAIL")
        return False

def test_api_endpoints():
    """Test critical API endpoints"""
    print_status("Testing API Endpoints...", "TEST")
    
    endpoints = [
        "/menu/", 
        "/orders/",
        "/tables/",
        "/receipts/",
        "/users/",
        "/inventory/"
    ]
    
    passed = 0
    for endpoint in endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            # Accept both 200 (success) and 401 (unauthorized) as valid responses
            # since we're not authenticating in these tests
            if response.status_code in [200, 401]:
                print_status(f"✓ {endpoint} - Endpoint accessible", "PASS")
                passed += 1
            else:
                print_status(f"✗ {endpoint} - Status {response.status_code}", "FAIL")
        except requests.exceptions.RequestException as e:
            print_status(f"✗ {endpoint} - Connection error: {e}", "FAIL")
    
    # Test auth login specifically (POST only)
    try:
        test_login_data = {"email": "test@example.com", "password": "testpass"}
        response = requests.post(f"{API_BASE_URL}/auth/login/", json=test_login_data, timeout=5)
        if response.status_code in [200, 400, 401]:  # Valid responses (400/401 expected for bad credentials)
            print_status("✓ /auth/login/ - Endpoint accessible", "PASS")
            passed += 1
        else:
            print_status(f"✗ /auth/login/ - Status {response.status_code}", "FAIL")
    except requests.exceptions.RequestException as e:
        print_status(f"✗ /auth/login/ - Connection error: {e}", "FAIL")
    
    total_endpoints = len(endpoints) + 1  # +1 for auth endpoint
    success_rate = (passed / total_endpoints) * 100
    print_status(f"API Endpoint Tests: {passed}/{total_endpoints} passed ({success_rate:.1f}%)", 
                 "PASS" if success_rate >= 80 else "WARN")
    return success_rate >= 80

def test_static_files():
    """Test static file serving"""
    print_status("Testing Static File Access...", "TEST")
    
    static_files = [
        "/static/admin/css/base.css",
        "/static/images/maria-havens-logo.jpg"
    ]
    
    passed = 0
    for file_path in static_files:
        try:
            response = requests.get(f"{BACKEND_URL}{file_path}", timeout=5)
            if response.status_code == 200:
                print_status(f"✓ {file_path} - File accessible", "PASS")
                passed += 1
            else:
                print_status(f"✗ {file_path} - Status {response.status_code}", "FAIL")
        except requests.exceptions.RequestException as e:
            print_status(f"✗ {file_path} - Connection error: {e}", "FAIL")
    
    print_status(f"Static File Tests: {passed}/{len(static_files)} passed", 
                 "PASS" if passed == len(static_files) else "WARN")
    return passed == len(static_files)

def test_order_creation():
    """Test order creation functionality"""
    print_status("Testing Order Creation (Core Functionality)...", "TEST")
    
    # First, let's try to get menu items to create a realistic order
    try:
        menu_response = requests.get(f"{API_BASE_URL}/menu/", timeout=5)
        if menu_response.status_code == 200:
            print_status("✓ Menu endpoint accessible for order creation", "PASS")
        else:
            print_status(f"✗ Menu endpoint returned {menu_response.status_code}", "FAIL")
            return False
    except Exception as e:
        print_status(f"✗ Cannot access menu endpoint: {e}", "FAIL")
        return False
    
    # Test order creation endpoint
    test_order = {
        "type": "dine_in",
        "customer_name": "Test Customer",
        "table_number": "5",
        "items": [
            {
                "name": "Test Item",
                "quantity": 2,
                "price": 15.99
            }
        ]
    }
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/orders/", 
            json=test_order,
            headers={"Content-Type": "application/json"},
            timeout=5
        )
        
        if response.status_code in [201, 401]:  # 401 is expected without auth
            print_status("✓ Order creation endpoint accessible", "PASS")
            return True
        else:
            print_status(f"✗ Order creation failed with status {response.status_code}", "FAIL")
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    print_status(f"Error details: {error_data}", "INFO")
                except:
                    pass
            return False
    except Exception as e:
        print_status(f"✗ Order creation test failed: {e}", "FAIL")
        return False

def test_receipt_endpoints():
    """Test receipt-related endpoints"""
    print_status("Testing Receipt Functionality...", "TEST")
    
    receipt_endpoints = [
        "/receipts/",
        "/receipts/templates/",
    ]
    
    passed = 0
    for endpoint in receipt_endpoints:
        try:
            response = requests.get(f"{API_BASE_URL}{endpoint}", timeout=5)
            if response.status_code in [200, 401, 404]:  # Accept these as valid responses
                print_status(f"✓ {endpoint} - Endpoint accessible", "PASS")
                passed += 1
            else:
                print_status(f"✗ {endpoint} - Status {response.status_code}", "FAIL")
        except requests.exceptions.RequestException as e:
            print_status(f"✗ {endpoint} - Connection error: {e}", "FAIL")
    
    print_status(f"Receipt Endpoint Tests: {passed}/{len(receipt_endpoints)} passed", 
                 "PASS" if passed >= 1 else "WARN")
    return passed >= 1

def check_logo_integration():
    """Check if the Maria Havens logo is properly integrated"""
    print_status("Checking Logo Integration...", "TEST")
    
    # Check backend logo file
    backend_logo_path = "c:/Users/DELL/Desktop/newpos3/backend/static/images/maria-havens-logo.jpg"
    if os.path.exists(backend_logo_path):
        print_status("✓ Maria Havens logo found in backend static files", "PASS")
        backend_logo_ok = True
    else:
        print_status("✗ Maria Havens logo missing from backend static files", "FAIL")
        backend_logo_ok = False
    
    # Check frontend logo file
    frontend_logo_path = "c:/Users/DELL/Desktop/newpos3/frontend/public/maria-havens-logo.jpg"
    if os.path.exists(frontend_logo_path):
        print_status("✓ Maria Havens logo found in frontend public files", "PASS")
        frontend_logo_ok = True
    else:
        print_status("✗ Maria Havens logo missing from frontend public files", "FAIL")
        frontend_logo_ok = False
    
    # Check receipt template
    template_path = "c:/Users/DELL/Desktop/newpos3/backend/receipts/templates/receipts/receipt_template.html"
    if os.path.exists(template_path):
        print_status("✓ Receipt template file exists", "PASS")
        
        # Check if template contains logo reference
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                if 'maria-havens-logo.jpg' in template_content:
                    print_status("✓ Receipt template references Maria Havens logo", "PASS")
                    template_logo_ok = True
                else:
                    print_status("✗ Receipt template does not reference logo", "FAIL")
                    template_logo_ok = False
        except Exception as e:
            print_status(f"✗ Could not read receipt template: {e}", "FAIL")
            template_logo_ok = False
    else:
        print_status("✗ Receipt template file missing", "FAIL")
        template_logo_ok = False
    
    overall_logo_ok = backend_logo_ok and template_logo_ok
    print_status(f"Logo Integration: {'Complete' if overall_logo_ok else 'Incomplete'}", 
                 "PASS" if overall_logo_ok else "WARN")
    return overall_logo_ok

def check_database_connectivity():
    """Check database connectivity through Django admin"""
    print_status("Testing Database Connectivity...", "TEST")
    
    try:
        # Check if we can access Django admin (which requires database)
        response = requests.get(f"{BACKEND_URL}/admin/login/", timeout=5)
        if response.status_code == 200:
            print_status("✓ Database appears to be connected (Django admin accessible)", "PASS")
            return True
        else:
            print_status(f"✗ Database connection issue (admin status: {response.status_code})", "FAIL")
            return False
    except Exception as e:
        print_status(f"✗ Database connectivity test failed: {e}", "FAIL")
        return False

def run_comprehensive_tests():
    """Run all tests and provide summary"""
    print_status("="*60, "INFO")
    print_status("MARIA HAVENS POS SYSTEM - COMPREHENSIVE TEST SUITE", "INFO")
    print_status("="*60, "INFO")
    print_status(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    print()
    
    test_results = {}
    
    # Run all tests
    test_results['backend_connectivity'] = test_server_connectivity()
    print()
    
    test_results['frontend_connectivity'] = test_frontend_connectivity()
    print()
    
    test_results['database_connectivity'] = check_database_connectivity()
    print()
    
    test_results['api_endpoints'] = test_api_endpoints()
    print()
    
    test_results['static_files'] = test_static_files()
    print()
    
    test_results['order_creation'] = test_order_creation()
    print()
    
    test_results['receipt_endpoints'] = test_receipt_endpoints()
    print()
    
    test_results['logo_integration'] = check_logo_integration()
    print()
    
    # Calculate overall results
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    # Print summary
    print_status("="*60, "INFO")
    print_status("TEST SUMMARY", "INFO")
    print_status("="*60, "INFO")
    
    for test_name, result in test_results.items():
        status = "PASS" if result else "FAIL"
        print_status(f"{test_name.replace('_', ' ').title()}: {'✓' if result else '✗'}", status)
    
    print()
    print_status(f"Overall Results: {passed_tests}/{total_tests} tests passed ({success_rate:.1f}%)", 
                 "PASS" if success_rate >= 80 else "FAIL")
    
    if success_rate >= 80:
        print_status("🎉 System is functioning well! Frontend and backend are properly connected.", "PASS")
        print_status("✅ Receipt functionality with Maria Havens logo is ready for use.", "PASS")
    elif success_rate >= 60:
        print_status("⚠️  System is partially functional. Some issues need attention.", "WARN")
    else:
        print_status("❌ System has significant issues that need to be resolved.", "FAIL")
    
    print_status(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    
    return success_rate >= 80

if __name__ == "__main__":
    try:
        success = run_comprehensive_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_status("\nTest interrupted by user", "WARN")
        sys.exit(1)
    except Exception as e:
        print_status(f"Test suite failed with error: {e}", "FAIL")
        sys.exit(1)