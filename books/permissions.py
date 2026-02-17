from rest_framework import permissions


class IsLibrarian(permissions.BasePermission):
    """
    Allows access only to librarian users.
    Librarians have full access to all endpoints.
    """
    message = "Only librarians have access to this resource."

    def has_permission(self, request, view):
        """Check if user is authenticated and is a librarian"""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Librarian').exists()
        )


class IsMember(permissions.BasePermission):
    """
    Allows access only to member users.
    """
    message = "Only members have access to this resource."

    def has_permission(self, request, view):
        """Check if user is authenticated and is a member"""
        return (
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Member').exists()
        )


class IsLibrarianOrReadOnly(permissions.BasePermission):
    """
    Allows librarians to edit any object.
    Allows non-librarians (members) to read-only access.
    """
    message = "Only librarians can modify this resource."

    def has_permission(self, request, view):
        """Allow read access to everyone, write access to librarians only"""
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        return (
            request.user and
            request.user.is_authenticated and
            request.user.groups.filter(name='Librarian').exists()
        )


class IsLibrarianOrIsOwner(permissions.BasePermission):
    """
    Allows librarians to access any object.
    Allows members to access only their own objects.
    """
    message = "You do not have permission to access this resource."

    def has_permission(self, request, view):
        """Allow access to authenticated users only"""
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Librarians can access all objects.
        Others can only access their own objects.
        """
        is_librarian = request.user.groups.filter(name='Librarian').exists()
        if is_librarian:
            return True
        
        # For non-librarians, check if they are the owner
        # This assumes the object has a 'user' or 'owner' field
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'member') and hasattr(obj.member, 'user'):
            return obj.member.user == request.user
        
        return False


class CanBorrowAndReturn(permissions.BasePermission):
    """
    Allows members to borrow and return books.
    Allows librarians to manage all borrow records.
    """
    message = "You do not have permission to perform this action."

    def has_permission(self, request, view):
        """Check if user can access borrow operations"""
        if not (request.user and request.user.is_authenticated):
            return False
        
        # Librarians can do everything
        if request.user.groups.filter(name='Librarian').exists():
            return True
        
        # Members can only perform certain actions
        if request.user.groups.filter(name='Member').exists():
            # Allow members to borrow and return books
            if hasattr(view, 'action'):
                return view.action in ['list', 'retrieve', 'borrow', 'return']
        
        return False
