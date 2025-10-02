from rest_framework import serializers
# Added missing imports needed for consistency, though not directly used in serializers
from rest_framework.parsers import MultiPartParser, FormParser 
from .models import Category, MenuItem, MenuItemIngredient, MenuItemModifier
from inventory.models import InventoryItem

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    # Added image_url as a read-only field
    image_url = serializers.ReadOnlyField(source='image.url')
    
    class Meta:
        model = Category
        # Ensure 'image' and 'image_url' are in fields
        fields = ['id', 'name', 'description', 'image', 'image_url', 'display_order', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'image_url']
        # Set extra kwargs to allow file upload/update
        extra_kwargs = {
            'image': {'required': False}
        }

class MenuItemIngredientSerializer(serializers.ModelSerializer):
    """Menu item ingredient serializer"""
    
    class Meta:
        model = MenuItemIngredient
        fields = ['id', 'ingredient_name', 'quantity_required', 'unit', 'is_optional']
        read_only_fields = ['id']

class MenuItemModifierSerializer(serializers.ModelSerializer):
    """Menu item modifier serializer"""
    
    class Meta:
        model = MenuItemModifier
        fields = ['id', 'name', 'description', 'price_adjustment', 'modifier_type', 'is_required', 'max_quantity']
        read_only_fields = ['id']

class MenuItemListSerializer(serializers.ModelSerializer):
    """Simplified menu item serializer for list views"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    price_str = serializers.ReadOnlyField()
    # Ensure image URL is available in list view
    image_url = serializers.ReadOnlyField(source='image_url') # Use property from model

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'category', 'category_name', 'price', 
            'price_str', 'image_url', 'is_available', 'preparation_time', 'is_special'
        ]
        read_only_fields = ['id', 'price_str', 'category_name', 'image_url']

class MenuItemSerializer(serializers.ModelSerializer):
    """Full menu item serializer for detail views"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    ingredients = MenuItemIngredientSerializer(many=True, read_only=True)
    modifiers = MenuItemModifierSerializer(many=True, read_only=True)
    price_str = serializers.ReadOnlyField()
    # Ensure image URL is available in detail view
    image_url = serializers.ReadOnlyField(source='image_url') # Use property from model

    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'category', 'category_name', 'price', 
            'price_str', 'image', 'image_url', 'is_available', 'preparation_time', 'is_special', 
            'ingredients', 'modifiers', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'price_str', 'category_name', 'image_url']
        # Set extra kwargs to allow file upload/update
        extra_kwargs = {
            'image': {'required': False}
        }

class MenuItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creation and updates, allowing nested modifications of ingredients/modifiers."""
    
    # Use nested serializers for writable fields
    ingredients = MenuItemIngredientSerializer(many=True, required=False, allow_null=True)
    modifiers = MenuItemModifierSerializer(many=True, required=False, allow_null=True)
    
    class Meta:
        model = MenuItem
        # Ensure 'image' is included
        fields = [
            'id', 'name', 'description', 'category', 'price', 'image', 'is_available', 
            'preparation_time', 'is_special', 'ingredients', 'modifiers'
        ]
        read_only_fields = ['id']
        # Set extra kwargs to allow file upload/update
        extra_kwargs = {
            'image': {'required': False}
        }

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        modifiers_data = validated_data.pop('modifiers', [])
        
        # Note: DRF handles the ImageField creation/update automatically 
        # when using ModelSerializer with MultiPartParser.
        menu_item = MenuItem.objects.create(**validated_data)
        
        for ingredient_data in ingredients_data:
            MenuItemIngredient.objects.create(menu_item=menu_item, **ingredient_data)
        
        for modifier_data in modifiers_data:
            MenuItemModifier.objects.create(menu_item=menu_item, **modifier_data)
            
        return menu_item

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        modifiers_data = validated_data.pop('modifiers', None)

        # Handle file replacement/update and other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update ingredients if provided
        if ingredients_data is not None:
            instance.ingredients.all().delete()
            for ingredient_data in ingredients_data:
                MenuItemIngredient.objects.create(menu_item=instance, **ingredient_data)
        
        # Update modifiers if provided
        if modifiers_data is not None:
            instance.modifiers.all().delete()
            for modifier_data in modifiers_data:
                MenuItemModifier.objects.create(menu_item=instance, **modifier_data)
        
        return instance

class MenuItemAvailabilitySerializer(serializers.ModelSerializer):
    """Serializer for updating menu item availability"""
    
    class Meta:
        model = MenuItem
        fields = ['is_available']

class CategoryWithItemsSerializer(serializers.ModelSerializer):
    """Category serializer with menu items"""
    
    menu_items = MenuItemListSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    # Added image_url as a read-only field
    image_url = serializers.ReadOnlyField(source='image.url')
    
    class Meta:
        model = Category
        # Ensure 'image_url' and 'image' are in fields
        fields = ['id', 'name', 'description', 'image_url', 'image', 'display_order', 
                  'is_active', 'menu_items', 'items_count']
        read_only_fields = ['id', 'created_at', 'image_url']
    
    def get_items_count(self, obj):
        return obj.menu_items.count()
