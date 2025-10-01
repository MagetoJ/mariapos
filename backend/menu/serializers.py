from rest_framework import serializers
from .models import Category, MenuItem, MenuItemIngredient, MenuItemModifier
from inventory.models import InventoryItem

class CategorySerializer(serializers.ModelSerializer):
    """Category serializer"""
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image_url', 'image', 'display_order', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']

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
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'category', 'category_name', 'price', 'price_str',
            'image_url', 'image', 'is_available', 'is_popular', 'is_vegetarian', 'is_vegan', 
            'is_gluten_free', 'preparation_time', 'spice_level', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class MenuItemSerializer(serializers.ModelSerializer):
    """Full menu item serializer with ingredients and modifiers"""
    
    category_name = serializers.CharField(source='category.name', read_only=True)
    ingredients = MenuItemIngredientSerializer(many=True, read_only=True)
    modifiers = MenuItemModifierSerializer(many=True, read_only=True)
    price_str = serializers.ReadOnlyField()
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'category', 'category_name', 
            'price', 'price_str', 'image_url', 'image', 'is_available', 'is_popular',
            'is_vegetarian', 'is_vegan', 'is_gluten_free', 'preparation_time', 
            'calories', 'spice_level', 'requires_ingredients', 'display_order',
            'ingredients', 'modifiers', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class MenuItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Menu item serializer for create/update operations"""
    
    ingredients = MenuItemIngredientSerializer(many=True, required=False)
    modifiers = MenuItemModifierSerializer(many=True, required=False)
    
    class Meta:
        model = MenuItem
        fields = [
            'name', 'description', 'category', 'price', 'image_url', 'image',
            'is_available', 'is_popular', 'is_vegetarian', 'is_vegan', 'is_gluten_free',
            'preparation_time', 'calories', 'spice_level', 'requires_ingredients',
            'display_order', 'ingredients', 'modifiers'
        ]
    
    def validate_ingredients(self, ingredients_data):
        """Validate ingredients data"""
        for ingredient_data in ingredients_data:
            if not ingredient_data.get('ingredient_name'):
                raise serializers.ValidationError("Ingredient name is required")
        return ingredients_data
    
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', [])
        modifiers_data = validated_data.pop('modifiers', [])
        
        menu_item = MenuItem.objects.create(**validated_data)
        
        # Create ingredients
        for ingredient_data in ingredients_data:
            MenuItemIngredient.objects.create(menu_item=menu_item, **ingredient_data)
        
        # Create modifiers
        for modifier_data in modifiers_data:
            MenuItemModifier.objects.create(menu_item=menu_item, **modifier_data)
        
        return menu_item
    
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        modifiers_data = validated_data.pop('modifiers', None)
        
        # Update menu item fields
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
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image_url', 'image', 'display_order', 
                  'is_active', 'menu_items', 'items_count']
        read_only_fields = ['id', 'created_at']
    
    def get_items_count(self, obj):
        return obj.menu_items.filter(is_available=True).count()