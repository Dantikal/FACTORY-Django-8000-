from rest_framework.permissions import BasePermission, SAFE_METHODS


class WarehouseOrderPermission(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        role = request.user.role
        if request.method == 'POST':
            return role == 'warehouse_manager'
        if request.method in SAFE_METHODS:
            return role in ('admin', 'factory', 'warehouse_manager')
        return False
