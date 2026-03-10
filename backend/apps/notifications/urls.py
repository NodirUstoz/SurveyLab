from django.urls import path

from . import views

app_name = "notifications"

urlpatterns = [
    path("", views.NotificationListView.as_view(), name="list"),
    path("unread-count/", views.UnreadCountView.as_view(), name="unread_count"),
    path("mark-read/", views.MarkNotificationsReadView.as_view(), name="mark_read"),
    path(
        "preferences/",
        views.NotificationPreferenceView.as_view(),
        name="preferences",
    ),
    path(
        "<uuid:pk>/",
        views.DeleteNotificationView.as_view(),
        name="delete",
    ),
]
