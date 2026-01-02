import os

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsStaffOrReadOnly(BasePermission):
    def has_permission(self, request, view) -> bool:
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class HasCrawlerToken(BasePermission):
    def has_permission(self, request, view) -> bool:
        token = os.getenv("CRAWLER_API_TOKEN", "").strip()
        if not token:
            return True
        header_token = request.headers.get("X-API-Token")
        if header_token:
            return header_token == token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ", 1)[1].strip() == token
        return False
