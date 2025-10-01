from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """User serializer for CRUD operations"""
    
    password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'phone', 'is_active',
            'created_at', 'room_number', 'check_in_date', 'check_out_date',
            'password', 'confirm_password'
        ]
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True},
            'confirm_password': {'write_only': True}
        }
    
    def validate(self, attrs):
        if 'password' in attrs and 'confirm_password' in attrs:
            if attrs['password'] != attrs['confirm_password']:
                raise serializers.ValidationError("Password fields didn't match.")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(password=password, **validated_data)
        return user
    
    def update(self, instance, validated_data):
        validated_data.pop('confirm_password', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class UserListSerializer(serializers.ModelSerializer):
    """Simplified user serializer for list views"""
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'phone', 'is_active',
            'created_at', 'room_number'
        ]
        read_only_fields = ['id', 'created_at']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Custom JWT token serializer with room number support"""
    
    room_number = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, attrs):
        credentials = {
            'email': attrs.get('email'),
            'password': attrs.get('password')
        }
        
        if not credentials['email'] or not credentials['password']:
            raise serializers.ValidationError('Must include "email" and "password".')
        
        user = authenticate(**credentials)
        
        if user:
            # For guest users, validate room number
            if user.role == 'guest':
                room_number = attrs.get('room_number')
                if not room_number:
                    raise serializers.ValidationError('Room number is required for guest login.')
                if user.room_number != room_number:
                    raise serializers.ValidationError('Invalid room number.')
            
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            
            # Generate tokens
            refresh = self.get_token(user)
            data = {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': UserListSerializer(user).data
            }
            
            return data
        else:
            raise serializers.ValidationError('No active account found with the given credentials.')

class LoginSerializer(serializers.Serializer):
    """Login serializer"""
    
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    room_number = serializers.CharField(required=False, allow_blank=True)

class ChangePasswordSerializer(serializers.Serializer):
    """Change password serializer"""
    
    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['confirm_password']:
            raise serializers.ValidationError("New password fields didn't match.")
        return attrs
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value

class UserProfileSerializer(serializers.ModelSerializer):
    """User profile serializer for current user info"""
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'role', 'phone', 'is_active',
            'created_at', 'room_number', 'check_in_date', 'check_out_date'
        ]
        read_only_fields = ['id', 'created_at', 'role', 'email']

class GuestUserSerializer(serializers.ModelSerializer):
    """Serializer specifically for guest users"""
    
    class Meta:
        model = User
        fields = [
            'id', 'name', 'email', 'phone', 'room_number',
            'check_in_date', 'check_out_date', 'is_active'
        ]
        read_only_fields = ['id']