from rest_framework.permissions import BasePermission


class IsOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class HasAPIKey(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request, 'api_key') and request.api_key is not None


class HasSufficientCredits(BasePermission):
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.subscription.available_credits > 0
