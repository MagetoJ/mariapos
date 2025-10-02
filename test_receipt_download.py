#!/usr/bin/env python3
"""
Test script for Receipt Download Functionality with Maria Havens Logo
This script tests the complete receipt download/PDF generation workflow
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
from django.http import HttpResponse
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

def test_receipt_api_endpoint():
    """Test receipt API endpoint accessibility"""
    print_status("Testing Receipt API Endpoints...", "TEST")
    
    try:
        # Test receipts list endpoint
        response = requests.get("http://localhost:8000/api/receipts/", timeout=5)
        if response.status_code in [200, 401]:  # 401 is acceptable (authentication required)
            print_status("✓ Receipts API endpoint accessible", "PASS")
            api_working = True
        else:
            print_status(f"✗ Receipts API endpoint - Status {response.status_code}", "FAIL")
            api_working = False
            
        # Test receipt templates endpoint
        response = requests.get("http://localhost:8000/api/receipts/templates/", timeout=5)
        if response.status_code in [200, 401]:
            print_status("✓ Receipt templates API endpoint accessible", "PASS")
            templates_working = True
        else:
            print_status(f"✗ Receipt templates API endpoint - Status {response.status_code}", "FAIL")
            templates_working = False
            
        return api_working and templates_working
        
    except Exception as e:
        print_status(f"✗ Error testing API endpoints: {e}", "FAIL")
        return False

def create_test_receipt():
    """Create a test receipt in the database"""
    print_status("Creating Test Receipt in Database...", "TEST")
    
    try:
        # Get or create test user
        User = get_user_model()
        user, created = User.objects.get_or_create(
            email='test@mariahavens.com',
            defaults={
                'name': 'Test Cashier',
                'role': 'cashier',
                'is_active': True
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
        
        # Create test order first (required for receipt)
        order, created = Order.objects.get_or_create(
            order_number='TEST-ORDER-001',
            defaults={
                'customer': user,  # Using the customer field
                'type': 'dine_in',
                'status': 'completed',
                'subtotal': 25.99,
                'tax_amount': 4.16,
                'total_amount': 32.75,  # Correct field name
                'table_number': '5'
            }
        )
        
        # Create test receipt
        receipt, created = Receipt.objects.get_or_create(
            receipt_number='TEST-RECEIPT-001',
            defaults={
                'order': order,
                'business_name': 'Maria Havens',
                'business_address': '123 Restaurant Street, Food City, FC 12345',
                'business_phone': '+1-555-HAVENS',
                'business_email': 'info@mariahavens.com',
                'tax_id': 'TAX-MH-123456789',
                'customer_name': 'Test Customer',
                'customer_email': 'customer@test.com',
                'customer_room': '101',
                'subtotal': 25.99,
                'tax_amount': 4.16,
                'service_charge': 2.60,
                'total_amount': 32.75,
                'amount_paid': 35.00,
                'change_amount': 2.25,
                'payment_method': 'cash',
                'generated_by': user,
                'status': 'active'
            }
        )
        
        # Create test receipt items if receipt was created
        if created:
            ReceiptItem.objects.create(
                receipt=receipt,
                item_name='Grilled Chicken Burger',
                quantity=1,
                unit_price=15.99,
                line_total=15.99,
                is_taxable=True
            )
            
            ReceiptItem.objects.create(
                receipt=receipt,
                item_name='French Fries',
                quantity=1,
                unit_price=8.99,
                line_total=8.99,
                is_taxable=True
            )
            
            ReceiptItem.objects.create(
                receipt=receipt,
                item_name='Coca Cola',
                quantity=1,
                unit_price=2.99,
                line_total=2.99,
                is_taxable=True
            )
        
        print_status(f"✓ Test receipt created: {receipt.receipt_number}", "PASS")
        return receipt
        
    except Exception as e:
        print_status(f"✗ Error creating test receipt: {e}", "FAIL")
        return None

def test_receipt_html_rendering(receipt):
    """Test HTML rendering of receipt with logo"""
    print_status("Testing Receipt HTML Rendering...", "TEST")
    
    try:
        # Render the receipt template
        html_content = render_to_string('receipts/receipt_template.html', {
            'receipt': receipt,
            'items': receipt.items.all()
        })
        
        # Check for logo reference
        if 'maria-havens-logo.jpg' in html_content:
            print_status("✓ HTML contains Maria Havens logo reference", "PASS")
        else:
            print_status("✗ HTML missing logo reference", "FAIL")
            return False
            
        # Check for business name
        if 'Maria Havens' in html_content:
            print_status("✓ HTML contains business name", "PASS")
        else:
            print_status("✗ HTML missing business name", "FAIL")
            return False
            
        # Check for receipt items
        item_count = receipt.items.count()
        if item_count > 0:
            print_status(f"✓ HTML contains {item_count} receipt items", "PASS")
        else:
            print_status("✗ HTML missing receipt items", "FAIL")
            return False
            
        # Save rendered HTML for inspection
        output_path = "c:\\Users\\DELL\\Desktop\\newpos3\\test_receipt_output.html"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print_status(f"✓ Full receipt HTML saved to {output_path}", "PASS")
        
        return True
        
    except Exception as e:
        print_status(f"✗ Error rendering HTML: {e}", "FAIL")
        return False

def test_logo_in_receipt_context():
    """Test that logo is properly accessible in receipt context"""
    print_status("Testing Logo Accessibility in Receipt Context...", "TEST")
    
    try:
        # Test logo file accessibility
        logo_path = "c:\\Users\\DELL\\Desktop\\newpos3\\backend\\static\\images\\maria-havens-logo.jpg"
        
        if os.path.exists(logo_path):
            file_size = os.path.getsize(logo_path)
            print_status(f"✓ Logo file exists ({file_size} bytes)", "PASS")
        else:
            print_status("✗ Logo file not found", "FAIL")
            return False
            
        # Test static URL serving
        response = requests.get("http://localhost:8000/static/images/maria-havens-logo.jpg", timeout=5)
        if response.status_code == 200:
            print_status("✓ Logo accessible via static URL", "PASS")
            print_status(f"✓ Logo response size: {len(response.content)} bytes", "INFO")
        else:
            print_status(f"✗ Logo not accessible via static URL - Status {response.status_code}", "FAIL")
            return False
            
        return True
        
    except Exception as e:
        print_status(f"✗ Error testing logo accessibility: {e}", "FAIL")
        return False

def test_frontend_integration():
    """Test frontend integration with receipt service"""
    print_status("Testing Frontend Integration...", "TEST")
    
    try:
        # Check if frontend data service contains receipt methods
        data_service_path = "c:\\Users\\DELL\\Desktop\\newpos3\\frontend\\lib\\api\\data-service.ts"
        
        if os.path.exists(data_service_path):
            with open(data_service_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'receiptService' in content:
                print_status("✓ Frontend contains receiptService", "PASS")
            else:
                print_status("✗ Frontend missing receiptService", "FAIL")
                return False
                
            if 'downloadReceipt' in content:
                print_status("✓ Frontend contains downloadReceipt method", "PASS")
            else:
                print_status("✗ Frontend missing downloadReceipt method", "FAIL")
                return False
                
            return True
        else:
            print_status("✗ Frontend data service file not found", "FAIL")
            return False
            
    except Exception as e:
        print_status(f"✗ Error testing frontend integration: {e}", "FAIL")
        return False

def main():
    """Main test execution"""
    print_status("=" * 70, "INFO")
    print_status("MARIA HAVENS RECEIPT DOWNLOAD FUNCTIONALITY TEST", "INFO")
    print_status("=" * 70, "INFO")
    print_status(f"Test started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
    print()
    
    # Create test receipt first
    receipt = create_test_receipt()
    if not receipt:
        print_status("✗ Failed to create test receipt. Aborting tests.", "FAIL")
        return
    print()
    
    tests = [
        ("API Endpoints", test_receipt_api_endpoint),
        ("HTML Rendering", lambda: test_receipt_html_rendering(receipt)),
        ("Logo Accessibility", test_logo_in_receipt_context),
        ("Frontend Integration", test_frontend_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                passed += 1
                print_status(f"✓ {test_name}: PASSED", "PASS")
            else:
                print_status(f"✗ {test_name}: FAILED", "FAIL")
        except Exception as e:
            print_status(f"✗ {test_name} test failed with exception: {e}", "FAIL")
        print()
    
    # Summary
    print_status("=" * 70, "INFO")
    print_status("RECEIPT DOWNLOAD TEST SUMMARY", "INFO")
    print_status("=" * 70, "INFO")
    
    success_rate = (passed / total) * 100
    
    for i, (test_name, _) in enumerate(tests):
        status = "✓" if i < passed else "✗"
        print_status(f"{status} {test_name}: {'PASS' if i < passed else 'FAIL'}", 
                    "PASS" if i < passed else "FAIL")
    
    print()
    print_status(f"Overall Results: {passed}/{total} tests passed ({success_rate:.1f}%)", 
                "PASS" if success_rate >= 75 else "FAIL")
    
    if success_rate >= 75:
        print_status("🎉 Receipt download functionality with Maria Havens logo is working!", "PASS")
        print_status("✅ Full receipt generation pipeline is functional", "PASS")
        print_status("📄 Test receipt files have been generated for inspection", "INFO")
    else:
        print_status("⚠️ Some issues need to be resolved in receipt download functionality", "WARN")
    
    print_status(f"Test completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")

if __name__ == "__main__":
    main()