from django.db import models
from django.core.validators import MinValueValidator, DecimalValidator
import uuid
import os

# --- Helper functions (already present, ensuring they are complete) ---
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
# ---------------------------------------------------------------------

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

class MenuItem(models.Model):
    """Menu item model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0)])
    
    # --- ADDED: Image Field for Menu Item ---
    image = models.ImageField(upload_to=upload_menu_item_image, blank=True, null=True)
    # ------------------------------------------

    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(
        default=15, 
        help_text="Time in minutes"
    )
    is_special = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'menu_items'
        ordering = ['name']
        verbose_name = 'Menu Item'
        verbose_name_plural = 'Menu Items'
        
    @property
    def price_str(self):
        return f"${self.price}"
        
    @property
    def image_url(self):
        """Returns the full image URL if an image exists."""
        return self.image.url if self.image else None

    def __str__(self):
        return self.name

class MenuItemIngredient(models.Model):
    """Defines ingredients and quantities needed for a menu item"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='ingredients')
    ingredient_name = models.CharField(max_length=100)
    quantity_required = models.DecimalField(
        max_digits=8, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    unit = models.CharField(max_length=20, help_text="e.g., grams, ml, units")
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
        return f"{self.menu_item.name} modifier: {self.name}"
