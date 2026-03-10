from django.contrib import admin

from .models import Notification, NotificationPreference


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        "title_short", "recipient", "notification_type",
        "priority", "is_read", "created_at",
    ]
    list_filter = ["notification_type", "priority", "is_read", "created_at"]
    search_fields = ["title", "message", "recipient__email"]
    readonly_fields = ["id", "created_at", "read_at"]

    @admin.display(description="Title")
    def title_short(self, obj):
        return obj.title[:60]


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = [
        "user", "email_on_response", "email_digest",
        "in_app_enabled",
    ]
    list_filter = ["email_digest", "in_app_enabled"]
    search_fields = ["user__email"]
