from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "plan", "is_active", "max_surveys", "created_at"]
    list_filter = ["plan", "is_active"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ["id", "created_at", "updated_at"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = [
        "email", "username", "first_name", "last_name",
        "organization", "role", "is_active", "created_at",
    ]
    list_filter = ["role", "is_active", "is_staff", "organization"]
    search_fields = ["email", "username", "first_name", "last_name"]
    ordering = ["-created_at"]
    readonly_fields = ["id", "created_at", "updated_at"]

    fieldsets = (
        (None, {"fields": ("email", "username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "avatar", "phone")}),
        (
            _("Organization"),
            {"fields": ("organization", "role")},
        ),
        (
            _("Preferences"),
            {"fields": ("preferred_language", "timezone", "email_notifications")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active", "is_staff", "is_superuser",
                    "groups", "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
