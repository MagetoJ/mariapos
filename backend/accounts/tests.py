from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from .models import WorkShift, UserSession
from .serializers import (
    UserSerializer, UserListSerializer, CustomTokenObtainPairSerializer,
    ChangePasswordSerializer, UserProfileSerializer, GuestUserSerializer
)

User = get_user_model()


class UserModelTest(TestCase):
    """Test cases for User model"""

    def setUp(self):
        self.user_data = {
            'name': 'John Doe',
            'email': 'john@example.com',
            'role': 'waiter',
            'phone': '1234567890',
        }

    def test_create_user(self):
        """Test creating a regular user"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            role='waiter'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.role, 'waiter')
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        """Test creating a superuser"""
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123',
            name='Admin User'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertEqual(user.role, 'admin')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_user_string_representation(self):
        """Test user string representation"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User'
        )
        self.assertEqual(str(user), 'Test User (test@example.com)')

    def test_email_normalization(self):
        """Test email normalization"""
        user = User.objects.create_user(
            email='TEST@EXAMPLE.COM',
            password='testpass123',
            name='Test User'
        )
        self.assertEqual(user.email, 'TEST@example.com')  # Domain is normalized but not the local part

    def test_create_user_without_email(self):
        """Test creating user without email raises error"""
        with self.assertRaises(ValueError):
            User.objects.create_user(
                email='',
                password='testpass123',
                name='Test User'
            )

    def test_guest_user_with_room_number(self):
        """Test creating guest user with room number"""
        user = User.objects.create_user(
            email='guest@example.com',
            password='guestpass123',
            name='Guest User',
            role='guest',
            room_number='101',
            check_in_date=timezone.now()
        )
        self.assertEqual(user.role, 'guest')
        self.assertEqual(user.room_number, '101')
        self.assertIsNotNone(user.check_in_date)

    def test_user_table_assignment(self):
        """Test user table assignment"""
        user = User.objects.create_user(
            email='waiter@example.com',
            password='waiterpass123',
            name='Waiter User',
            role='waiter',
            table_number='T5'
        )
        self.assertEqual(user.table_number, 'T5')


class WorkShiftModelTest(TestCase):
    """Test cases for WorkShift model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            role='waiter'
        )

    def test_create_work_shift(self):
        """Test creating a work shift"""
        shift = WorkShift.objects.create(
            name='Morning Shift',
            start_time='08:00:00',
            end_time='16:00:00'
        )
        self.assertEqual(shift.name, 'Morning Shift')
        self.assertTrue(shift.is_active)

    def test_work_shift_string_representation(self):
        """Test work shift string representation"""
        shift = WorkShift.objects.create(
            name='Evening Shift',
            start_time='16:00:00',
            end_time='00:00:00'
        )
        expected_str = "Evening Shift (16:00:00 - 00:00:00)"
        self.assertEqual(str(shift), expected_str)

    def test_end_work_shift(self):
        """Test ending a work shift"""
        shift = WorkShift.objects.create(
            name='Morning Shift',
            start_time='08:00:00',
            end_time='16:00:00'
        )
        shift.is_active = False
        shift.save()
        
        self.assertFalse(shift.is_active)


class UserSessionModelTest(TestCase):
    """Test cases for UserSession model"""

    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            role='waiter'
        )
        self.shift = WorkShift.objects.create(
            name='Morning Shift',
            start_time='08:00:00',
            end_time='16:00:00'
        )

    def test_create_user_session(self):
        """Test creating a user session"""
        session = UserSession.objects.create(
            user=self.user,
            shift=self.shift,
            login_time=timezone.now()
        )
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.shift, self.shift)

    def test_user_session_string_representation(self):
        """Test user session string representation"""
        session = UserSession.objects.create(
            user=self.user,
            shift=self.shift,
            login_time=timezone.now()
        )
        # Check the actual string representation from the model
        self.assertIn(self.user.name, str(session))


class UserSerializerTest(TestCase):
    """Test cases for User serializers"""

    def setUp(self):
        self.user_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'waiter',
            'phone': '1234567890',
            'password': 'testpass123',
            'confirm_password': 'testpass123'
        }

    def test_user_serializer_create(self):
        """Test UserSerializer create method"""
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.name, 'Test User')
        self.assertTrue(user.check_password('testpass123'))

    def test_user_serializer_password_mismatch(self):
        """Test UserSerializer with password mismatch"""
        data = self.user_data.copy()
        data['confirm_password'] = 'differentpass'
        serializer = UserSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("Password fields didn't match.", str(serializer.errors))

    def test_user_list_serializer(self):
        """Test UserListSerializer"""
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            name='Test User',
            role='waiter'
        )
        serializer = UserListSerializer(user)
        self.assertEqual(serializer.data['name'], 'Test User')
        self.assertEqual(serializer.data['email'], 'test@example.com')
        self.assertNotIn('password', serializer.data)

    def test_guest_user_serializer(self):
        """Test GuestUserSerializer"""
        user = User.objects.create_user(
            email='guest@example.com',
            password='guestpass123',
            name='Guest User',
            role='guest',
            room_number='101'
        )
        serializer = GuestUserSerializer(user)
        self.assertEqual(serializer.data['room_number'], '101')
        self.assertEqual(serializer.data['name'], 'Guest User')

    def test_change_password_serializer_valid(self):
        """Test ChangePasswordSerializer with valid data"""
        user = User.objects.create_user(
            email='test@example.com',
            password='oldpass123',
            name='Test User'
        )
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': type('Request', (), {'user': user})()})
        self.assertTrue(serializer.is_valid())

    def test_change_password_serializer_mismatch(self):
        """Test ChangePasswordSerializer with password mismatch"""
        user = User.objects.create_user(
            email='test@example.com',
            password='oldpass123',
            name='Test User'
        )
        data = {
            'current_password': 'oldpass123',
            'new_password': 'newpass123',
            'confirm_password': 'differentpass'
        }
        serializer = ChangePasswordSerializer(data=data, context={'request': type('Request', (), {'user': user})()})
        self.assertFalse(serializer.is_valid())


class AuthenticationAPITest(APITestCase):
    """Test cases for authentication API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            name='Admin User',
            role='admin'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123',
            name='Regular User',
            role='waiter'
        )
        self.guest_user = User.objects.create_user(
            email='guest@example.com',
            password='guestpass123',
            name='Guest User',
            role='guest',
            room_number='101'
        )

    def test_login_success(self):
        """Test successful login"""
        url = reverse('accounts:login')
        data = {
            'email': 'user@example.com',
            'password': 'userpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)
        self.assertIn('user', response.data)

    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        url = reverse('accounts:login')
        data = {
            'email': 'user@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_guest_login_with_room_number(self):
        """Test guest login with room number"""
        url = reverse('accounts:login')
        data = {
            'email': 'guest@example.com',
            'password': 'guestpass123',
            'room_number': '101'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_guest_login_without_room_number(self):
        """Test guest login without room number fails"""
        url = reverse('accounts:login')
        data = {
            'email': 'guest@example.com',
            'password': 'guestpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_guest_login_wrong_room_number(self):
        """Test guest login with wrong room number fails"""
        url = reverse('accounts:login')
        data = {
            'email': 'guest@example.com',
            'password': 'guestpass123',
            'room_number': '999'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_success(self):
        """Test successful logout"""
        # Login first to get tokens
        refresh = RefreshToken.for_user(self.regular_user)
        self.client.force_authenticate(user=self.regular_user)
        
        url = reverse('accounts:logout')
        data = {'refresh_token': str(refresh)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_current_user_get(self):
        """Test getting current user info"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:current-user')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'user@example.com')

    def test_current_user_update(self):
        """Test updating current user info"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:current-user')
        data = {'name': 'Updated Name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], 'Updated Name')


class UserManagementAPITest(APITestCase):
    """Test cases for user management API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            name='Admin User',
            role='admin'
        )
        self.manager_user = User.objects.create_user(
            email='manager@example.com',
            password='managerpass123',
            name='Manager User',
            role='manager'
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123',
            name='Regular User',
            role='waiter'
        )

    def test_user_list_as_admin(self):
        """Test user list access as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:user-list-create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)

    def test_user_list_filtering_by_role(self):
        """Test user list filtering by role"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:user-list-create')
        response = self.client.get(url, {'role': 'admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_user_list_search(self):
        """Test user list search functionality"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:user-list-create')
        response = self.client.get(url, {'search': 'Admin'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_user_as_admin(self):
        """Test creating user as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:user-list-create')
        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'role': 'cashier',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_as_regular_user_fails(self):
        """Test creating user as regular user fails"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:user-list-create')
        data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'role': 'cashier',
            'password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_detail_as_owner(self):
        """Test accessing user detail as owner"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:user-detail', kwargs={'pk': self.regular_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_detail_as_admin(self):
        """Test accessing user detail as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:user-detail', kwargs={'pk': self.regular_user.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_other_user_as_regular_user_fails(self):
        """Test updating other user as regular user fails"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:user-detail', kwargs={'pk': self.admin_user.pk})
        data = {'name': 'Hacked Name'}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user_as_admin(self):
        """Test deleting user as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:user-detail', kwargs={'pk': self.regular_user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_as_manager_fails(self):
        """Test deleting user as manager fails"""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('accounts:user-detail', kwargs={'pk': self.regular_user.pk})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_change_password_own_account(self):
        """Test changing own password"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:change-password', kwargs={'pk': self.regular_user.pk})
        data = {
            'current_password': 'userpass123',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_change_password_wrong_current_password(self):
        """Test changing password with wrong current password"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:change-password', kwargs={'pk': self.regular_user.pk})
        data = {
            'current_password': 'wrongpass',
            'new_password': 'newpass123',
            'confirm_password': 'newpass123'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_activate_user_as_admin(self):
        """Test activating/deactivating user as admin"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:activate-user', kwargs={'pk': self.regular_user.pk})
        data = {'is_active': False}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_active'])

    def test_staff_list_as_manager(self):
        """Test staff list access as manager"""
        self.client.force_authenticate(user=self.manager_user)
        url = reverse('accounts:staff-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_staff_list_as_regular_user_fails(self):
        """Test staff list access as regular user fails"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:staff-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class GuestManagementAPITest(APITestCase):
    """Test cases for guest management API endpoints"""

    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            email='admin@example.com',
            password='adminpass123',
            name='Admin User',
            role='admin'
        )
        self.receptionist_user = User.objects.create_user(
            email='receptionist@example.com',
            password='receptionistpass123',
            name='Receptionist User',
            role='receptionist'
        )
        self.guest_user = User.objects.create_user(
            email='guest@example.com',
            password='guestpass123',
            name='Guest User',
            role='guest',
            room_number='101',
            check_in_date=timezone.now()
        )
        self.regular_user = User.objects.create_user(
            email='user@example.com',
            password='userpass123',
            name='Regular User',
            role='waiter'
        )

    def test_guest_list_as_receptionist(self):
        """Test guest list access as receptionist"""
        self.client.force_authenticate(user=self.receptionist_user)
        url = reverse('accounts:guest-users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_guest_list_as_regular_user_fails(self):
        """Test guest list access as regular user fails"""
        self.client.force_authenticate(user=self.regular_user)
        url = reverse('accounts:guest-users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_guest_list_filter_by_room(self):
        """Test guest list filtering by room number"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:guest-users-list')
        response = self.client.get(url, {'roomNumber': '101'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['room_number'], '101')

    def test_guest_list_filter_checked_in(self):
        """Test guest list filtering by checked-in status"""
        self.client.force_authenticate(user=self.admin_user)
        url = reverse('accounts:guest-users-list')
        response = self.client.get(url, {'checkedIn': 'true'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)