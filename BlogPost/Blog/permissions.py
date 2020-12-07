from rest_framework import permissions


class IsAdminOrReadOnly(permissions.IsAdminUser):
    def has_permission(self, request,view, obj):
        is_admin = super().has_permission(request, view)        
        return request.method in permissions.SAFE_METHODS or is_admin

        

class IsAuthorOrIsAdminOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:            
            if request.user.is_authenticated:                
                return True                
        return obj.author == request.user or request.user.is_superuser 


            