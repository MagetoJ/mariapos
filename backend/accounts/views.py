from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import PermissionDenied
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.db.models import Q
from .serializers import (
    UserSerializer, UserListSerializer, CustomTokenObtainPairSerializer,
    LoginSerializer, ChangePasswordSerializer, UserProfileSerializer,
    GuestUserSerializer
)

User = get_user_model()

class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token obtain view with room number support for guests"""
    serializer_class = CustomTokenObtainPairSerializer

class LoginView(APIView):
    """Login view that returns user data along with JWT tokens"""
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    """Logout view that blacklists the refresh token"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get("refresh_token")
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)

class CurrentUserView(APIView):
    """Get current authenticated user details"""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserListCreateView(generics.ListCreateAPIView):
    """List and create users"""
    queryset = User.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserSerializer
        return UserListSerializer
    
    def get_queryset(self):
        queryset = User.objects.all()
        
        # Filter by role
        role = self.request.query_params.get('role')
        if role:
            queryset = queryset.filter(role=role)
        
        # Filter by active status
        is_active = self.request.query_params.get('isActive')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Search by name or email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        # Only allow admin and manager to create users
        if self.request.user.role not in ['admin', 'manager']:
            raise PermissionDenied("Only admin and manager can create users")
        serializer.save()

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Retrieve, update, or delete a user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        # Users can only access their own data unless they're admin/manager
        if self.request.user.role in ['admin', 'manager']:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)
    
    def perform_update(self, serializer):
        # Only allow admin and manager to update other users
        if self.get_object().id != self.request.user.id:
            if self.request.user.role not in ['admin', 'manager']:
                raise PermissionDenied("Only admin and manager can update other users")
        serializer.save()
    
    def perform_destroy(self, instance):
        # Only allow admin to delete users
        if self.request.user.role != 'admin':
            raise PermissionDenied("Only admin can delete users")
        instance.delete()

class ChangePasswordView(APIView):
    """Change user password"""
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, pk=None):
        # Users can only change their own password unless they're admin
        if pk and str(pk) != str(request.user.id):
            if request.user.role != 'admin':
                raise PermissionDenied("Only admin can change other users' passwords")
            user = generics.get_object_or_404(User, pk=pk)
        else:
            user = request.user
        
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # For admin changing other users' passwords, skip current password check
            if request.user.role == 'admin' and user != request.user:
                user.set_password(serializer.validated_data['new_password'])
                user.save()
            else:
                user.set_password(serializer.validated_data['new_password'])
                user.save()
            
            return Response({"message": "Password changed successfully"}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class StaffListView(generics.ListAPIView):
    """List all staff members (non-guest users)"""
    serializer_class = UserListSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role not in ['admin', 'manager']:
            raise PermissionDenied("Only admin and manager can view staff list")
        
        return User.objects.filter(role__in=[
            'admin', 'manager', 'receptionist', 'waiter', 'kitchen', 'cashier'
        ]).order_by('role', 'name')

class GuestListView(generics.ListAPIView):
    """List all guest users"""
    serializer_class = GuestUserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role not in ['admin', 'manager', 'receptionist']:
            raise PermissionDenied("Only admin, manager, and receptionist can view guest list")
        
        queryset = User.objects.filter(role='guest')
        
        # Filter by room number
        room_number = self.request.query_params.get('roomNumber')
        if room_number:
            queryset = queryset.filter(room_number=room_number)
        
        # Filter by check-in status
        checked_in = self.request.query_params.get('checkedIn')
        if checked_in is not None:
            if checked_in.lower() == 'true':
                queryset = queryset.filter(check_in_date__isnull=False, check_out_date__isnull=True)
            else:
                queryset = queryset.filter(check_out_date__isnull=False)
        
        return queryset.order_by('-check_in_date')

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def activate_user(request, pk):
    """Activate/deactivate a user account"""
    if request.user.role not in ['admin', 'manager']:
        return Response(
            {"error": "Only admin and manager can activate/deactivate users"}, 
            status=status.HTTP_403_FORBIDDEN
        )
    
    try:
        user = User.objects.get(pk=pk)
        is_active = request.data.get('is_active', True)
        user.is_active = is_active
        user.save()
        
        serializer = UserListSerializer(user)
        return Response(serializer.data)
    except User.DoesNotExist:
        return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)