from rest_framework import serializers

from .models import Notification, NotificationPreference


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = [
            "id", "notification_type", "priority", "title", "message",
            "action_url", "related_survey", "metadata",
            "is_read", "read_at", "created_at",
        ]
        read_only_fields = [
            "id", "notification_type", "priority", "title", "message",
            "action_url", "related_survey", "metadata", "created_at",
        ]


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationPreference
        fields = [
            "email_on_response", "email_on_quota",
            "email_on_survey_close", "email_digest",
            "in_app_enabled", "quiet_hours_start", "quiet_hours_end",
        ]


class MarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""

    notification_ids = serializers.ListField(
        child=serializers.UUIDField(), required=False, default=list
    )
    mark_all = serializers.BooleanField(default=False)
