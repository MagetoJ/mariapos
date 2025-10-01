"""
Custom permission classes for the Maria Havens POS system.
"""

from rest_framework import permissions


class IsManagerOrAdmin(permissions.BasePermission):
    """
    Permission class to check if user is a manager or admin.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager']
        )


class IsStaffMember(permissions.BasePermission):
    """
    Permission class to check if user is a staff member (any role except guest).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role != 'guest'
        )


class IsAdminOnly(permissions.BasePermission):
    """
    Permission class to check if user is an admin only.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'admin'
        )


class IsManagerAdminOrInventoryStaff(permissions.BasePermission):
    """
    Permission class for inventory management.
    Allows managers, admins, and kitchen staff to manage inventory.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager', 'kitchen']
        )


class IsKitchenOrManager(permissions.BasePermission):
    """
    Permission class for kitchen operations.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['kitchen', 'manager', 'admin']
        )


class IsWaiterOrManager(permissions.BasePermission):
    """
    Permission class for order taking and table management.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['waiter', 'manager', 'admin']
        )


class IsCashierOrManager(permissions.BasePermission):
    """
    Permission class for payment processing.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['cashier', 'manager', 'admin']
        )


class IsCashierOrAbove(permissions.BasePermission):
    """
    Permission class for payment processing (alias for IsCashierOrManager).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['cashier', 'manager', 'admin']
        )


class IsReceptionistOrManager(permissions.BasePermission):
    """
    Permission class for guest management.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['receptionist', 'manager', 'admin']
        )


class IsReceptionistOrAbove(permissions.BasePermission):
    """
    Permission class for guest management (alias for IsReceptionistOrManager).
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['receptionist', 'manager', 'admin']
        )


class IsGuestOrStaff(permissions.BasePermission):
    """
    Permission class that allows both guests and staff.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated


class CanManageUsers(permissions.BasePermission):
    """
    Permission class for user management operations.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            # Read operations allowed for staff
            return (
                request.user.is_authenticated and
                request.user.role in ['admin', 'manager']
            )
        else:
            # Write operations only for admins
            return (
                request.user.is_authenticated and
                request.user.role == 'admin'
            )


class CanAccessReports(permissions.BasePermission):
    """
    Permission class for accessing reports and analytics.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ['admin', 'manager', 'cashier']
        )


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the object
        return obj.created_by == request.user or request.user.role in ['admin', 'manager']


class CanManageServiceRequests(permissions.BasePermission):
    """
    Permission class for service request management.
    """
    def has_permission(self, request, view):
        if request.method == 'POST':
            # Guests can create service requests
            return request.user.is_authenticated
        else:
            # Only staff can view/manage service requests
            return (
                request.user.is_authenticated and
                request.user.role != 'guest'
            )