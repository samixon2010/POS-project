from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotFound, PermissionDenied
from .models import Product

class IsOwnerOfProduct(BasePermission):
    def has_object_permission(self, request, view, obj):
        if not obj:
            raise NotFound("Product not found.")

        if obj.owner != request.user:
            raise PermissionDenied("This product was created by another user.")
        return True