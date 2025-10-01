from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

app_name = 'accounts'

urlpatterns = [
    # Authentication
    path('auth/login/', views.LoginView.as_view(), name='login'),
    path('auth/logout/', views.LogoutView.as_view(), name='logout'),
    path('auth/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # Users
    path('users/', views.UserListCreateView.as_view(), name='user-list-create'),
    path('users/<uuid:pk>/', views.UserDetailView.as_view(), name='user-detail'),
    path('users/<uuid:pk>/change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('users/<uuid:pk>/activate/', views.activate_user, name='activate-user'),
    
    # Staff and Guests
    path('staff/', views.StaffListView.as_view(), name='staff-list'),
    path('guests/users/', views.GuestListView.as_view(), name='guest-users-list'),
]