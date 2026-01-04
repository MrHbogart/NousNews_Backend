import os
import ipaddress

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
            return _is_private_request(request)
        header_token = request.headers.get("X-API-Token")
        if header_token:
            return header_token == token
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header.split(" ", 1)[1].strip() == token
        return False


def _is_private_request(request) -> bool:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip = (forwarded.split(",")[0].strip() if forwarded else request.META.get("REMOTE_ADDR", "")).strip()
    if not ip:
        return False
    try:
        addr = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return bool(addr.is_private or addr.is_loopback)
