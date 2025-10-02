#!/usr/bin/env python3
"""
Maria Havens POS System - Mobile Responsiveness & Data Flow Test

This script tests:
1. Django admin accessibility and functionality
2. Mobile-responsive frontend functionality  
3. Complete data flow from frontend to backend to database
4. API integration and data persistence
5. Receipt generation with logo integration
"""

import asyncio
import json
import os
import sys
import time
import requests
import sqlite3
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path

# Test configuration
BACKEND_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
ADMIN_URL = f"{BACKEND_URL}/admin"
API_URL = f"{BACKEND_URL}/api"
DB_PATH = Path("c:/Users/DELL/Desktop/newpos3/backend/db.sqlite3")

class Colors:
    """ANSI color codes for colored output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class MobileSystemTester:
    def __init__(self):
        self.results = {
            'admin_tests': [],
            'mobile_tests': [],
            'data_flow_tests': [],
            'api_tests': [],
            'integration_tests': []
        }
        self.auth_token = None
        self.test_data = {}
        
    def print_status(self, message, status="INFO"):
        """Print colored status messages"""
        color_map = {
            "PASS": Colors.GREEN,
            "FAIL": Colors.RED,
            "WARNING": Colors.YELLOW,
            "INFO": Colors.BLUE,
            "TEST": Colors.PURPLE
        }
        color = color_map.get(status, Colors.WHITE)
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"{color}[{timestamp}] [{status}] {message}{Colors.END}")

    def test_django_admin_access(self):
        """Test Django admin interface accessibility"""
        self.print_status("Testing Django Admin Access...", "TEST")
        
        try:
            # Test admin login page
            response = requests.get(f"{ADMIN_URL}/login/", timeout=10)
            if response.status_code == 200:
                self.print_status("✓ Admin login page accessible", "PASS")
                self.results['admin_tests'].append({"test": "admin_login_page", "status": "pass"})
            else:
                self.print_status(f"✗ Admin login page failed: {response.status_code}", "FAIL")
                self.results['admin_tests'].append({"test": "admin_login_page", "status": "fail"})
                
            # Test admin static files
            admin_css_url = f"{BACKEND_URL}/static/admin/css/base.css"
            response = requests.get(admin_css_url, timeout=10)
            if response.status_code == 200:
                self.print_status("✓ Admin static files loading", "PASS")
                self.results['admin_tests'].append({"test": "admin_static_files", "status": "pass"})
            else:
                self.print_status("✗ Admin static files not loading", "FAIL")
                self.results['admin_tests'].append({"test": "admin_static_files", "status": "fail"})
                
        except requests.RequestException as e:
            self.print_status(f"✗ Admin access failed: {str(e)}", "FAIL")
            self.results['admin_tests'].append({"test": "admin_access", "status": "fail", "error": str(e)})

    def test_mobile_responsiveness(self):
        """Test mobile-responsive frontend features"""
        self.print_status("Testing Mobile Responsiveness...", "TEST")
        
        try:
            # Test main frontend page
            response = requests.get(FRONTEND_URL, timeout=10)
            if response.status_code == 200:
                self.print_status("✓ Frontend accessible", "PASS")
                self.results['mobile_tests'].append({"test": "frontend_access", "status": "pass"})
                
                # Check for mobile viewport meta tag
                content = response.text
                if 'viewport' in content and 'width=device-width' in content:
                    self.print_status("✓ Mobile viewport meta tag present", "PASS")
                    self.results['mobile_tests'].append({"test": "mobile_viewport", "status": "pass"})
                else:
                    self.print_status("✗ Mobile viewport meta tag missing", "FAIL")
                    self.results['mobile_tests'].append({"test": "mobile_viewport", "status": "fail"})
                    
                # Check for responsive CSS framework (Tailwind CSS)
                if 'tailwindcss' in content or 'md:' in content or 'sm:' in content:
                    self.print_status("✓ Responsive CSS framework detected", "PASS")
                    self.results['mobile_tests'].append({"test": "responsive_css", "status": "pass"})
                else:
                    self.print_status("? Responsive CSS framework status unclear", "WARNING")
                    self.results['mobile_tests'].append({"test": "responsive_css", "status": "warning"})
                    
            else:
                self.print_status(f"✗ Frontend not accessible: {response.status_code}", "FAIL")
                self.results['mobile_tests'].append({"test": "frontend_access", "status": "fail"})
                
        except requests.RequestException as e:
            self.print_status(f"✗ Mobile test failed: {str(e)}", "FAIL")
            self.results['mobile_tests'].append({"test": "mobile_access", "status": "fail", "error": str(e)})

    def test_api_authentication(self):
        """Test API authentication for data flow"""
        self.print_status("Testing API Authentication...", "TEST")
        
        try:
            # Test login endpoint
            login_data = {
                "email": "admin@mariahavens.com",
                "password": "admin123"
            }
            
            response = requests.post(f"{API_URL}/auth/login/", json=login_data, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if 'access' in data:
                    self.auth_token = data['access']
                    self.print_status("✓ API authentication successful", "PASS")
                    self.results['api_tests'].append({"test": "api_auth", "status": "pass"})
                    return True
                else:
                    self.print_status("✗ Authentication response invalid", "FAIL")
                    self.results['api_tests'].append({"test": "api_auth", "status": "fail"})
            else:
                self.print_status(f"✗ Authentication failed: {response.status_code}", "FAIL")
                self.results['api_tests'].append({"test": "api_auth", "status": "fail"})
                
        except requests.RequestException as e:
            self.print_status(f"✗ API authentication error: {str(e)}", "FAIL")
            self.results['api_tests'].append({"test": "api_auth", "status": "fail", "error": str(e)})
            
        return False

    def get_auth_headers(self):
        """Get authorization headers for API requests"""
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}

    def test_menu_data_flow(self):
        """Test complete menu data flow: Frontend → API → Database"""
        self.print_status("Testing Menu Data Flow...", "TEST")
        
        try:
            headers = self.get_auth_headers()
            
            # 1. Test creating a category
            category_data = {
                "name": f"Test Category {int(time.time())}",
                "description": "Mobile test category",
                "display_order": 1,
                "is_active": True
            }
            
            response = requests.post(f"{API_URL}/menu/categories/", json=category_data, headers=headers, timeout=10)
            if response.status_code == 201:
                category = response.json()
                self.test_data['category'] = category
                self.print_status("✓ Category creation successful", "PASS")
                self.results['data_flow_tests'].append({"test": "category_creation", "status": "pass"})
                
                # 2. Test creating a menu item
                menu_item_data = {
                    "name": f"Test Menu Item {int(time.time())}",
                    "description": "Mobile test menu item",
                    "category": category['id'],
                    "price": "25.50",
                    "is_available": True,
                    "is_popular": False,
                    "preparation_time": 15
                }
                
                response = requests.post(f"{API_URL}/menu/", json=menu_item_data, headers=headers, timeout=10)
                if response.status_code == 201:
                    menu_item = response.json()
                    self.test_data['menu_item'] = menu_item
                    self.print_status("✓ Menu item creation successful", "PASS")
                    self.results['data_flow_tests'].append({"test": "menu_item_creation", "status": "pass"})
                    
                    # 3. Verify data in database
                    if self.verify_database_entry('menu_items', menu_item['id']):
                        self.print_status("✓ Menu item persisted to database", "PASS")
                        self.results['data_flow_tests'].append({"test": "menu_db_persistence", "status": "pass"})
                    else:
                        self.print_status("✗ Menu item not found in database", "FAIL")
                        self.results['data_flow_tests'].append({"test": "menu_db_persistence", "status": "fail"})
                        
                else:
                    self.print_status(f"✗ Menu item creation failed: {response.status_code}", "FAIL")
                    self.results['data_flow_tests'].append({"test": "menu_item_creation", "status": "fail"})
                    
            else:
                self.print_status(f"✗ Category creation failed: {response.status_code}", "FAIL")
                self.results['data_flow_tests'].append({"test": "category_creation", "status": "fail"})
                
        except Exception as e:
            self.print_status(f"✗ Menu data flow test failed: {str(e)}", "FAIL")
            self.results['data_flow_tests'].append({"test": "menu_data_flow", "status": "fail", "error": str(e)})

    def test_order_data_flow(self):
        """Test complete order data flow: Frontend → API → Database"""
        self.print_status("Testing Order Data Flow...", "TEST")
        
        try:
            headers = self.get_auth_headers()
            
            # Get current user for customer field
            user_response = requests.get(f"{API_URL}/auth/me/", headers=headers, timeout=10)
            if user_response.status_code != 200:
                self.print_status("✗ Could not get current user", "FAIL")
                return
                
            current_user = user_response.json()
            
            # Create test order
            if 'menu_item' in self.test_data:
                order_data = {
                    "customer": current_user['id'],
                    "type": "dine_in",
                    "table_number": "5",
                    "status": "pending",
                    "items": [
                        {
                            "menu_item": self.test_data['menu_item']['id'],
                            "quantity": 2,
                            "special_instructions": "Extra spicy"
                        }
                    ]
                }
                
                response = requests.post(f"{API_URL}/orders/", json=order_data, headers=headers, timeout=10)
                if response.status_code == 201:
                    order = response.json()
                    self.test_data['order'] = order
                    self.print_status("✓ Order creation successful", "PASS")
                    self.results['data_flow_tests'].append({"test": "order_creation", "status": "pass"})
                    
                    # Verify in database
                    if self.verify_database_entry('orders', order['id']):
                        self.print_status("✓ Order persisted to database", "PASS")
                        self.results['data_flow_tests'].append({"test": "order_db_persistence", "status": "pass"})
                    else:
                        self.print_status("✗ Order not found in database", "FAIL")
                        self.results['data_flow_tests'].append({"test": "order_db_persistence", "status": "fail"})
                        
                else:
                    self.print_status(f"✗ Order creation failed: {response.status_code} - {response.text}", "FAIL")
                    self.results['data_flow_tests'].append({"test": "order_creation", "status": "fail"})
            else:
                self.print_status("✗ No menu item available for order test", "WARNING")
                self.results['data_flow_tests'].append({"test": "order_creation", "status": "skip"})
                
        except Exception as e:
            self.print_status(f"✗ Order data flow test failed: {str(e)}", "FAIL")
            self.results['data_flow_tests'].append({"test": "order_data_flow", "status": "fail", "error": str(e)})

    def test_receipt_generation(self):
        """Test receipt generation with logo integration"""
        self.print_status("Testing Receipt Generation...", "TEST")
        
        try:
            headers = self.get_auth_headers()
            
            if 'order' in self.test_data:
                # Test receipt generation
                receipt_data = {
                    "order_id": self.test_data['order']['id']
                }
                
                response = requests.post(f"{API_URL}/receipts/", json=receipt_data, headers=headers, timeout=10)
                if response.status_code == 201:
                    receipt = response.json()
                    self.test_data['receipt'] = receipt
                    self.print_status("✓ Receipt generation successful", "PASS")
                    self.results['integration_tests'].append({"test": "receipt_generation", "status": "pass"})
                    
                    # Test receipt download
                    download_response = requests.get(f"{API_URL}/receipts/{receipt['id']}/download/", headers=headers, timeout=10)
                    if download_response.status_code == 200:
                        content = download_response.text
                        if 'maria-havens-logo.jpg' in content:
                            self.print_status("✓ Receipt contains logo reference", "PASS")
                            self.results['integration_tests'].append({"test": "receipt_logo", "status": "pass"})
                        else:
                            self.print_status("✗ Receipt missing logo reference", "FAIL")
                            self.results['integration_tests'].append({"test": "receipt_logo", "status": "fail"})
                    else:
                        self.print_status(f"✗ Receipt download failed: {download_response.status_code}", "FAIL")
                        self.results['integration_tests'].append({"test": "receipt_download", "status": "fail"})
                        
                else:
                    self.print_status(f"✗ Receipt generation failed: {response.status_code}", "FAIL")
                    self.results['integration_tests'].append({"test": "receipt_generation", "status": "fail"})
            else:
                self.print_status("✗ No order available for receipt test", "WARNING")
                self.results['integration_tests'].append({"test": "receipt_generation", "status": "skip"})
                
        except Exception as e:
            self.print_status(f"✗ Receipt generation test failed: {str(e)}", "FAIL")
            self.results['integration_tests'].append({"test": "receipt_generation", "status": "fail", "error": str(e)})

    def verify_database_entry(self, table, record_id):
        """Verify data exists in SQLite database"""
        try:
            if not DB_PATH.exists():
                self.print_status(f"Database file not found: {DB_PATH}", "WARNING")
                return False
                
            conn = sqlite3.connect(str(DB_PATH))
            cursor = conn.cursor()
            
            # Query based on table name
            cursor.execute(f"SELECT id FROM {table} WHERE id = ?", (str(record_id),))
            result = cursor.fetchone()
            
            conn.close()
            return result is not None
            
        except Exception as e:
            self.print_status(f"Database verification error: {str(e)}", "WARNING")
            return False

    def test_all_api_endpoints(self):
        """Test all major API endpoints for connectivity"""
        self.print_status("Testing API Endpoint Connectivity...", "TEST")
        
        endpoints = [
            ("/auth/me/", "GET"),
            ("/users/", "GET"),
            ("/menu/", "GET"),
            ("/menu/categories/", "GET"),
            ("/orders/", "GET"),
            ("/tables/", "GET"),
            ("/inventory/", "GET"),
            ("/receipts/", "GET"),
            ("/dashboard/stats/", "GET")
        ]
        
        headers = self.get_auth_headers()
        successful_endpoints = 0
        
        for endpoint, method in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{API_URL}{endpoint}", headers=headers, timeout=10)
                else:
                    response = requests.post(f"{API_URL}{endpoint}", headers=headers, timeout=10)
                    
                if response.status_code in [200, 201]:
                    self.print_status(f"✓ {endpoint} - {response.status_code}", "PASS")
                    successful_endpoints += 1
                else:
                    self.print_status(f"✗ {endpoint} - {response.status_code}", "FAIL")
                    
            except Exception as e:
                self.print_status(f"✗ {endpoint} - Error: {str(e)}", "FAIL")
        
        success_rate = (successful_endpoints / len(endpoints)) * 100
        self.results['api_tests'].append({
            "test": "endpoint_connectivity", 
            "status": "pass" if success_rate >= 80 else "fail",
            "success_rate": success_rate
        })
        
        self.print_status(f"API Endpoint Success Rate: {success_rate:.1f}%", 
                         "PASS" if success_rate >= 80 else "FAIL")

    def test_static_file_serving(self):
        """Test static file serving including Maria Havens logo"""
        self.print_status("Testing Static File Serving...", "TEST")
        
        static_files = [
            "/static/images/maria-havens-logo.jpg",
            "/static/admin/css/base.css",
            "/static/admin/js/core.js"
        ]
        
        for file_path in static_files:
            try:
                response = requests.get(f"{BACKEND_URL}{file_path}", timeout=10)
                if response.status_code == 200:
                    self.print_status(f"✓ {file_path} - {len(response.content)} bytes", "PASS")
                    if 'maria-havens-logo.jpg' in file_path:
                        self.results['integration_tests'].append({"test": "logo_static_file", "status": "pass"})
                else:
                    self.print_status(f"✗ {file_path} - {response.status_code}", "FAIL")
                    if 'maria-havens-logo.jpg' in file_path:
                        self.results['integration_tests'].append({"test": "logo_static_file", "status": "fail"})
                        
            except Exception as e:
                self.print_status(f"✗ {file_path} - Error: {str(e)}", "FAIL")

    def generate_report(self):
        """Generate comprehensive test report"""
        self.print_status("Generating Test Report...", "INFO")
        
        total_tests = 0
        passed_tests = 0
        
        for category, tests in self.results.items():
            category_total = len(tests)
            category_passed = len([t for t in tests if t.get('status') == 'pass'])
            total_tests += category_total
            passed_tests += category_passed
            
            if category_total > 0:
                category_rate = (category_passed / category_total) * 100
                self.print_status(f"{category.replace('_', ' ').title()}: {category_passed}/{category_total} ({category_rate:.1f}%)", 
                                 "PASS" if category_rate >= 80 else "FAIL")
        
        overall_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"\n{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"{Colors.BOLD}MARIA HAVENS POS SYSTEM - MOBILE & DATA FLOW TEST REPORT{Colors.END}")
        print(f"{Colors.BOLD}{'='*60}{Colors.END}")
        print(f"Test Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total Tests: {total_tests}")
        print(f"Passed Tests: {passed_tests}")
        print(f"Failed Tests: {total_tests - passed_tests}")
        
        color = Colors.GREEN if overall_rate >= 80 else Colors.RED
        print(f"Overall Success Rate: {color}{overall_rate:.1f}%{Colors.END}")
        
        print(f"\n{Colors.BOLD}DETAILED RESULTS:{Colors.END}")
        for category, tests in self.results.items():
            print(f"\n{Colors.CYAN}{category.replace('_', ' ').title()}:{Colors.END}")
            for test in tests:
                status_color = Colors.GREEN if test['status'] == 'pass' else Colors.RED
                print(f"  • {test['test']}: {status_color}{test['status'].upper()}{Colors.END}")
                if 'error' in test:
                    print(f"    Error: {test['error']}")
        
        # Save detailed report to file
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'overall_rate': overall_rate,
            'total_tests': total_tests,
            'passed_tests': passed_tests,
            'results': self.results,
            'test_data': self.test_data
        }
        
        report_file = Path("c:/Users/DELL/Desktop/newpos3/mobile_system_test_report.json")
        with open(report_file, 'w') as f:
            json.dump(report_data, f, indent=2, default=str)
            
        print(f"\n{Colors.BLUE}Detailed report saved to: {report_file}{Colors.END}")
        
        return overall_rate >= 80

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.print_status("Starting Maria Havens POS System Mobile & Data Flow Tests", "INFO")
        
        # Step 1: Basic connectivity tests
        self.test_django_admin_access()
        self.test_mobile_responsiveness()
        self.test_static_file_serving()
        
        # Step 2: API and authentication tests
        if self.test_api_authentication():
            # Step 3: Data flow tests (only if authenticated)
            self.test_all_api_endpoints()
            self.test_menu_data_flow()
            self.test_order_data_flow()
            self.test_receipt_generation()
        else:
            self.print_status("Skipping data flow tests due to authentication failure", "WARNING")
        
        # Step 4: Generate report
        success = self.generate_report()
        
        return success

def main():
    """Main test execution function"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║              MARIA HAVENS POS SYSTEM                         ║")
    print("║          Mobile Responsiveness & Data Flow Test             ║")
    print("║                                                              ║")
    print("║  Testing: Django Admin, Mobile UI, API Integration,         ║")
    print("║          Database Persistence, Receipt Generation           ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    tester = MobileSystemTester()
    
    try:
        success = tester.run_all_tests()
        
        if success:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✓ TESTS PASSED: System is mobile-ready with working data flow!{Colors.END}")
            return 0
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}✗ TESTS FAILED: System needs attention before mobile deployment{Colors.END}")
            return 1
            
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Test interrupted by user{Colors.END}")
        return 1
    except Exception as e:
        print(f"\n{Colors.RED}Test failed with error: {str(e)}{Colors.END}")
        return 1

if __name__ == "__main__":
    sys.exit(main())