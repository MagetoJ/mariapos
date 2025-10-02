from rest_framework import serializers
from .models import Category, MenuItem, MenuItemIngredient, MenuItemModifier

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'description', 'image', 'is_active']
        read_only_fields = ['id', 'image']

class MenuItemIngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemIngredient
        fields = ['ingredient', 'quantity_required', 'unit']

class MenuItemModifierSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItemModifier
        fields = ['name', 'price', 'type']

class MenuItemSerializer(serializers.ModelSerializer):
    """Serializer for displaying menu item details"""
    category = serializers.CharField(source='category.name', read_only=True)
    ingredients = MenuItemIngredientSerializer(many=True, read_only=True)
    modifiers = MenuItemModifierSerializer(many=True, read_only=True)
    
    class Meta:
        model = MenuItem
        fields = [
            'id', 'name', 'description', 'image', 'category', 'price',
            'preparation_time', 'is_available', 'ingredients', 'modifiers',
            'created_at', 'updated_at'
        ]

class MenuItemCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for creating and updating menu items with file upload"""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='name'
    )
    
    class Meta:
        model = MenuItem
        fields = [
            'name', 'description', 'image', 'category', 'price',
            'preparation_time', 'is_available'
        ]
        extra_kwargs = {
            'image': {'required': False}
        }