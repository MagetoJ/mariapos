from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator
import uuid
import os

def upload_category_image(instance, filename):
    """Generate upload path for category images"""
    ext = filename.split('.')[-1]
    filename = f"{instance.id}.{ext}"
    return os.path.join('categories', filename)

def upload_menu_item_image(instance, filename):
    """Generate upload path for menu item images"""
    ext = filename.split('.')[-1]
    filename = f"{instance.id}.{ext}"
    return os.path.join('menu_items', filename)

class Category(models.Model):
    """Menu category model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to=upload_category_image, blank=True, null=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_categories'
        ordering = ['display_order', 'name']
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
    
    def __str__(self):
        return self.name
    
    @property
    def image_url(self):
        """Generate full URL for category image"""
        if self.image:
            from django.conf import settings
            return f"{settings.MEDIA_URL}{self.image.name}"
        return None

class MenuItem(models.Model):
    """Menu item model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(upload_to=upload_menu_item_image, blank=True, null=True)
    
    # Availability and status
    is_available = models.BooleanField(default=True)
    is_popular = models.BooleanField(default=False)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    
    # Preparation details
    preparation_time = models.PositiveIntegerField(
        help_text="Preparation time in minutes",
        default=15
    )
    calories = models.PositiveIntegerField(blank=True, null=True)
    spice_level = models.CharField(
        max_length=10,
        choices=[
            ('mild', 'Mild'),
            ('medium', 'Medium'),
            ('hot', 'Hot'),
            ('extra_hot', 'Extra Hot')
        ],
        default='mild'
    )
    
    # Inventory tracking
    requires_ingredients = models.BooleanField(default=True)
    
    # Display settings
    display_order = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['category', 'display_order', 'name']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        unique_together = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.category.name}"
    
    @property
    def price_str(self):
        """Format price for display"""
        return f"KSh {self.price:,.2f}"
    
    @property
    def image_url(self):
        """Generate full URL for menu item image"""
        if self.image:
            from django.conf import settings
            return f"{settings.MEDIA_URL}{self.image.name}"
        return None

class MenuItemIngredient(models.Model):
    """Relationship between menu items and inventory ingredients"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    ingredient_name = models.CharField(max_length=100)
    quantity_required = models.DecimalField(max_digits=8, decimal_places=3)
    unit = models.CharField(max_length=20)  # kg, liters, pieces, etc.
    is_optional = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'menu_item_ingredients'
        unique_together = ['menu_item', 'ingredient_name']
        verbose_name = 'Menu Item Ingredient'
        verbose_name_plural = 'Menu Item Ingredients'
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.ingredient_name}"

class MenuItemModifier(models.Model):
    """Menu item modifiers (extras, substitutions, etc.)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='modifiers')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price_adjustment = models.DecimalField(
        max_digits=8, 
        decimal_places=2, 
        default=0,
        help_text="Additional cost for this modifier"
    )
    modifier_type = models.CharField(
        max_length=20,
        choices=[
            ('extra', 'Extra'),
            ('substitute', 'Substitute'),
            ('remove', 'Remove'),
            ('sauce', 'Sauce'),
            ('size', 'Size')
        ]
    )
    is_required = models.BooleanField(default=False)
    max_quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        db_table = 'menu_item_modifiers'
        verbose_name = 'Menu Item Modifier'
        verbose_name_plural = 'Menu Item Modifiers'
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.name}"