"""Custom permissions for the SurveyLab API."""
from rest_framework import permissions


class IsOrganizationOwnerOrAdmin(permissions.BasePermission):
    """Allow access only to organization owners or admins."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role in ("owner", "admin")


class IsOrganizationMember(permissions.BasePermission):
    """Allow access to any member of the same organization."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.organization is not None


class IsSurveyOwner(permissions.BasePermission):
    """Allow access only to the owner of the survey."""

    def has_object_permission(self, request, view, obj):
        survey = getattr(obj, "survey", obj)
        return survey.owner == request.user


class IsSurveyOwnerOrOrganizationAdmin(permissions.BasePermission):
    """Allow access to survey owner or organization admin."""

    def has_object_permission(self, request, view, obj):
        survey = getattr(obj, "survey", obj)
        user = request.user

        if survey.owner == user:
            return True

        if (
            user.organization
            and survey.organization == user.organization
            and user.role in ("owner", "admin")
        ):
            return True

        return False


class ReadOnlyOrAuthenticated(permissions.BasePermission):
    """Allow read-only access to anyone, write access to authenticated users."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated


class CanManagePanels(permissions.BasePermission):
    """Allow panel management to organization owners, admins, and editors."""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if not request.user.organization:
            return False
        return request.user.role in ("owner", "admin", "editor")
