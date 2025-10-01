#!/usr/bin/env python
"""
Data Import Script for Maria Havens POS System
Imports product data from PDF files into the Django database
"""

import os
import sys
import django
import PyPDF2
import re
from decimal import Decimal
from pathlib import Path

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mariahavens_pos_backend.settings')
django.setup()

from menu.models import Category, MenuItem

class PDFDataImporter:
    """Imports product data from PDF files"""
    
    def __init__(self):
        self.categories_created = 0
        self.items_created = 0
        self.items_updated = 0
        
    def extract_text_from_pdf(self, pdf_path):
        """Extract text content from PDF file"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                return text
        except Exception as e:
            print(f"Error reading PDF: {e}")
            return None
    
    def parse_product_data(self, text):
        """Parse product data from extracted text"""
        products = []
        
        # Try to find structured data patterns
        # This is a generic parser - you may need to adjust based on your PDF format
        lines = text.split('\n')
        
        current_category = None
        current_product = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for category patterns (usually in caps or specific format)
            if self.is_category_line(line):
                if current_product:
                    products.append(current_product)
                    current_product = {}
                current_category = self.clean_category_name(line)
                continue
            
            # Look for product patterns
            product_match = self.extract_product_info(line)
            if product_match and current_category:
                if current_product:
                    products.append(current_product)
                
                current_product = {
                    'category': current_category,
                    'name': product_match.get('name'),
                    'price': product_match.get('price'),
                    'description': product_match.get('description', ''),
                }
        
        # Add the last product
        if current_product:
            products.append(current_product)
        
        return products
    
    def is_category_line(self, line):
        """Determine if a line represents a category"""
        # Common patterns for categories
        category_patterns = [
            r'^[A-Z\s&]{3,}$',  # All caps with spaces
            r'^\d+\.\s*[A-Z]',  # Numbered categories
            r'^CATEGORY:',       # Explicit category markers
        ]
        
        for pattern in category_patterns:
            if re.match(pattern, line):
                return True
        return False
    
    def clean_category_name(self, line):
        """Clean and normalize category names"""
        # Remove numbering, colons, etc.
        cleaned = re.sub(r'^\d+\.\s*', '', line)
        cleaned = re.sub(r'^CATEGORY:\s*', '', cleaned)
        return cleaned.title().strip()
    
    def extract_product_info(self, line):
        """Extract product information from a line"""
        # Pattern to match: Name Price Description (adjust as needed)
        patterns = [
            r'^(.+?)\s+\$?(\d+\.?\d*)\s*(.*)$',  # Name Price Description
            r'^(.+?)\s+(\d+\.?\d*)\s+(.*)$',     # Name Price Description without $
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                name = match.group(1).strip()
                try:
                    price = Decimal(match.group(2))
                except:
                    continue
                description = match.group(3).strip() if match.group(3) else ''
                
                # Filter out obviously wrong matches
                if len(name) < 2 or price <= 0:
                    continue
                    
                return {
                    'name': name,
                    'price': price,
                    'description': description
                }
        
        return None
    
    def create_category(self, category_name):
        """Create or get category"""
        category, created = Category.objects.get_or_create(
            name=category_name,
            defaults={
                'description': f'Category for {category_name} items',
                'is_active': True,
            }
        )
        if created:
            self.categories_created += 1
            print(f"Created category: {category_name}")
        return category
    
    def create_menu_item(self, product_data):
        """Create or update menu item"""
        category = self.create_category(product_data['category'])
        
        # Check if item already exists
        existing_item = MenuItem.objects.filter(
            name=product_data['name'],
            category=category
        ).first()
        
        if existing_item:
            # Update existing item
            existing_item.price = product_data['price']
            existing_item.description = product_data['description']
            existing_item.save()
            self.items_updated += 1
            print(f"Updated item: {product_data['name']}")
        else:
            # Create new item
            MenuItem.objects.create(
                name=product_data['name'],
                category=category,
                price=product_data['price'],
                description=product_data['description'],
                is_available=True,
            )
            self.items_created += 1
            print(f"Created item: {product_data['name']}")
    
    def import_from_pdf(self, pdf_path):
        """Main import function"""
        print(f"Starting import from: {pdf_path}")
        
        # Extract text from PDF
        text = self.extract_text_from_pdf(pdf_path)
        if not text:
            print("Failed to extract text from PDF")
            return False
        
        # Parse product data
        products = self.parse_product_data(text)
        print(f"Found {len(products)} products to import")
        
        # Import products
        for product in products:
            try:
                self.create_menu_item(product)
            except Exception as e:
                print(f"Error importing {product.get('name', 'unknown')}: {e}")
        
        # Print summary
        print("\nImport Summary:")
        print(f"Categories created: {self.categories_created}")
        print(f"Items created: {self.items_created}")
        print(f"Items updated: {self.items_updated}")
        
        return True
    
    def create_sample_data(self):
        """Create sample data if PDF parsing fails"""
        print("Creating sample data...")
        
        sample_categories = [
            {"name": "Appetizers", "items": [
                {"name": "Buffalo Wings", "price": "12.99", "description": "Spicy chicken wings with blue cheese dip"},
                {"name": "Mozzarella Sticks", "price": "8.99", "description": "Breaded mozzarella with marinara sauce"},
                {"name": "Spinach Artichoke Dip", "price": "10.99", "description": "Creamy dip with tortilla chips"},
            ]},
            {"name": "Main Courses", "items": [
                {"name": "Grilled Salmon", "price": "24.99", "description": "Fresh Atlantic salmon with vegetables"},
                {"name": "Ribeye Steak", "price": "29.99", "description": "12oz ribeye cooked to perfection"},
                {"name": "Chicken Parmesan", "price": "18.99", "description": "Breaded chicken with pasta and marinara"},
            ]},
            {"name": "Beverages", "items": [
                {"name": "Coffee", "price": "3.99", "description": "Freshly brewed coffee"},
                {"name": "Soft Drinks", "price": "2.99", "description": "Coca-Cola, Pepsi, Sprite"},
                {"name": "Fresh Juice", "price": "4.99", "description": "Orange, Apple, or Cranberry"},
            ]},
        ]
        
        for cat_data in sample_categories:
            category = self.create_category(cat_data["name"])
            for item_data in cat_data["items"]:
                item_data["category"] = cat_data["name"]
                self.create_menu_item(item_data)
        
        print("Sample data created successfully!")

def main():
    """Main execution function"""
    if len(sys.argv) < 2:
        print("Usage: python data_import.py <pdf_file_path> [--sample]")
        print("       python data_import.py --sample  # Create sample data")
        return
    
    importer = PDFDataImporter()
    
    if sys.argv[1] == '--sample':
        importer.create_sample_data()
    else:
        pdf_path = sys.argv[1]
        if not os.path.exists(pdf_path):
            print(f"Error: PDF file '{pdf_path}' not found")
            return
        
        success = importer.import_from_pdf(pdf_path)
        if not success:
            print("PDF import failed, creating sample data instead...")
            importer.create_sample_data()

if __name__ == "__main__":
    main()