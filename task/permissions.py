import os
from rest_framework.permissions import SAFE_METHODS, BasePermission
from dotenv import load_dotenv


load_dotenv()


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        if os.getenv("PERMISSIONS_OFF") is True:
            return True

        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
