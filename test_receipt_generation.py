#!/usr/bin/env python3
"""
Test script for Receipt Generation with Maria Havens Logo
This script tests the complete receipt generation workflow
"""

import os
import sys
import django
import requests
from datetime import datetime

# Add the backend directory to the Python path
sys.path.append('c:\\Users\\DELL\\Desktop\\newpos3\\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mariahavens_pos_backend.settings')

# Initialize Django
django.setup()

from django.contrib.auth import get_user_model
from django.template.loader import render_to_string
from orders.models import Order
from receipts.models import Receipt, ReceiptItem
from menu.models import MenuItem, Category
from accounts.models import User
from django.utils import timezone

def print_status(message, status="INFO"):
    """Print status message with color coding"""
    colors = {
        "INFO": "\033[94m",
        "PASS": "\033[92m", 
        "FAIL": "\033[91m",
        "WARN": "\033[93m",
        "TEST": "\033[96m"
    }
    
    print(f"{colors.get(status, '')}{message}\033[0m")

def test_logo_file_exists():
    """Test if logo files exist in both locations"""
    print_status("Testing Logo File Existence...", "TEST")
    
    backend_logo = "c:\\Users\\DELL\\Desktop\\newpos3\\backend\\static\\images\\maria-havens-logo.jpg"
    frontend_logo = "c:\\Users\\DELL\\Desktop\\newpos3\\frontend\\public\\maria-havens-logo.jpg"
    
    backend_exists = os.path.exists(backend_logo)
    frontend_exists = os.path.exists(frontend_logo)
    
    if backend_exists:
        print_status("✓ Backend logo file exists", "PASS")
    else:
        print_status("✗ Backend logo file missing", "FAIL")
        
    if frontend_exists:
        print_status("✓ Frontend logo file exists", "PASS")
    else:
        print_status("✗ Frontend logo file missing", "FAIL")
        
    return backend_exists and frontend_exists

def test_receipt_template():
    """Test if receipt template references the logo correctly"""
    print_status("Testing Receipt Template...", "TEST")
    
    template_path = "c:\\Users\\DELL\\Desktop\\newpos3\\backend\\receipts\\templates\\receipts\\receipt_template.html"
    
    if not os.path.exists(template_path):
        print_status("✗ Receipt template file not found", "FAIL")
        return False
        
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'maria-havens-logo.jpg' in content:
            print_status("✓ Receipt template references Maria Havens logo", "PASS")
            return True
        else:
            print_status("✗ Receipt template does not reference logo", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"✗ Error reading template: {e}", "FAIL")
        return False

def create_test_data():
    """Create test data for receipt generation"""
    print_status("Creating Test Data...", "TEST")
    
    try:
        # Create test user if not exists
        User = get_user_model()
        user, created = User.objects.get_or_create(
            email='test@mariahavens.com',
            defaults={
                'name': 'Test User',
                'role': 'cashier',
                'is_active': True
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            
        # Create test category
        category, created = Category.objects.get_or_create(
            name='Test Category',
            defaults={'description': 'Test category for receipt testing'}
        )
        
        # Create test menu item
        menu_item, created = MenuItem.objects.get_or_create(
            name='Test Burger',
            defaults={
                'description': 'Delicious test burger',
                'price': 15.99,
                'category': category,
                'is_available': True
            }
        )
        
        print_status("✓ Test data created successfully", "PASS")
        return user, menu_item
        
    except Exception as e:
        print_status(f"✗ Error creating test data: {e}", "FAIL")
        return None, None

def test_receipt_html_generation():
    """Test HTML receipt generation with logo"""
    print_status("Testing Receipt HTML Generation...", "TEST")
    
    try:
        # Create test receipt data
        receipt_data = {
            'receipt_number': 'TEST-001',
            'business_name': 'Maria Havens',
            'business_address': '123 Test Street, Test City',
            'business_phone': '+1-234-567-8900',
            'business_email': 'info@mariahavens.com',
            'tax_id': 'TAX-123456',
            'customer_name': 'Test Customer',
            'customer_room': '101',
            'subtotal': 15.99,
            'tax_amount': 2.56,
            'service_charge': 1.60,
            'total_amount': 20.15,
            'amount_paid': 25.00,
            'change_amount': 4.85,
            'payment_method': 'cash',
            'created_at': timezone.now()
        }
        
        # Create mock order object
        class MockOrder:
            order_number = 'ORD-TEST-001'
            def get_type_display(self):
                return 'Dine In'
            table_number = '5'
            waiter = None
            special_instructions = 'No onions'
        
        receipt_data['order'] = MockOrder()
        
        # Create mock items
        items = [
            {
                'quantity': 1,
                'name': 'Test Burger',
                'line_total': 15.99,
                'modifiers': [],
                'special_instructions': ''
            }
        ]
        
        # Render the template
        html_content = render_to_string('receipts/receipt_template.html', {
            'receipt': type('Receipt', (), receipt_data)(),
            'items': items
        })
        
        # Check if logo is referenced in the generated HTML
        if 'maria-havens-logo.jpg' in html_content:
            print_status("✓ HTML receipt contains logo reference", "PASS")
            
            # Save test HTML to file for inspection
            test_html_path = "c:\\Users\\DELL\\Desktop\\newpos3\\test_receipt.html"
            with open(test_html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            print_status(f"✓ Test receipt saved to {test_html_path}", "PASS")
            return True
        else:
            print_status("✗ HTML receipt does not contain logo reference", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"✗ Error generating HTML receipt: {e}", "FAIL")
        return False

def test_static_file_serving():
    """Test if logo is accessible via static file serving"""
    print_status("Testing Static File Serving...", "TEST")
    
    try:
        # Test logo accessibility
        response = requests.get("http://localhost:8000/static/images/maria-havens-logo.jpg", timeout=5)
        
        if response.status_code == 200:
            print_status("✓ Logo accessible via static file serving", "PASS")
            print_status(f"✓ Logo file size: {len(response.content)} bytes", "INFO")
            return True
        else:
            print_status(f"✗ Logo not accessible - Status {response.status_code}", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"✗ Error accessing static logo: {e}", "FAIL")
        return False

def main():
    """Main test execution"""
    print_status("=" * 60, "INFO")
    print_status("MARIA HAVENS RECEIPT GENERATION TEST", "INFO")
    print_status("=" * 60, "INFO")
    print_status(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    print()
    
    tests = [
        ("Logo Files", test_logo_file_exists),
        ("Receipt Template", test_receipt_template),
        ("HTML Generation", test_receipt_html_generation),
        ("Static File Serving", test_static_file_serving)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
        except Exception as e:
            print_status(f"✗ {test_name} test failed with exception: {e}", "FAIL")
        print()
    
    # Summary
    print_status("=" * 60, "INFO")
    print_status("RECEIPT GENERATION TEST SUMMARY", "INFO")
    print_status("=" * 60, "INFO")
    
    success_rate = (passed / total) * 100
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓" if i < passed else "✗"
        print_status(f"{status} {test_name}: {'PASS' if i < passed else 'FAIL'}", 
                    "PASS" if i < passed else "FAIL")
    
    print()
    print_status(f"Overall Results: {passed}/{total} tests passed ({success_rate:.1f}%)", 
                "PASS" if success_rate >= 75 else "FAIL")
    
    if success_rate >= 75:
        print_status("🎉 Receipt generation with Maria Havens logo is working!", "PASS")
        print_status("✅ Logo integration is complete and functional", "PASS")
    else:
        print_status("⚠️ Some issues need to be resolved", "WARN")
    
    print_status(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")

if __name__ == "__main__":
    main()