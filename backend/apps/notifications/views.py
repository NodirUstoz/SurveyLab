from django.utils import timezone
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification, NotificationPreference
from .serializers import (
    MarkReadSerializer,
    NotificationPreferenceSerializer,
    NotificationSerializer,
)


class NotificationListView(generics.ListAPIView):
    """List notifications for the authenticated user."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["is_read", "notification_type", "priority"]
    ordering_fields = ["created_at", "priority"]

    def get_queryset(self):
        return Notification.objects.filter(
            recipient=self.request.user
        ).select_related("related_survey")


class UnreadCountView(APIView):
    """Get the count of unread notifications."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(
            recipient=request.user, is_read=False
        ).count()
        return Response({"unread_count": count})


class MarkNotificationsReadView(APIView):
    """Mark specific notifications or all notifications as read."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = MarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        now = timezone.now()
        queryset = Notification.objects.filter(
            recipient=request.user, is_read=False
        )

        if data.get("mark_all"):
            updated = queryset.update(is_read=True, read_at=now)
        elif data.get("notification_ids"):
            updated = queryset.filter(
                id__in=data["notification_ids"]
            ).update(is_read=True, read_at=now)
        else:
            return Response(
                {"detail": "Provide notification_ids or set mark_all to true."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({"marked_read": updated})


class NotificationPreferenceView(APIView):
    """Get or update notification preferences."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        return Response(NotificationPreferenceSerializer(prefs).data)

    def put(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(prefs, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def patch(self, request):
        prefs, _ = NotificationPreference.objects.get_or_create(
            user=request.user
        )
        serializer = NotificationPreferenceSerializer(
            prefs, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DeleteNotificationView(generics.DestroyAPIView):
    """Delete a single notification."""

    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user)
