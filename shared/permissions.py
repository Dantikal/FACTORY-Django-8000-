from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenficated and request.user.role == "admin"

class IsFactory(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenficated and request.user.role in ('admin', 'factory')
    
class IsManager(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenficated and request.user.role in ('admin', 'manager')
    
class IsAccountant(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenficated and request.user.role in ('admin', 'accountant')