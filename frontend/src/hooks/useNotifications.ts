import { useEffect, useCallback } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import {
  fetchNotifications,
  fetchUnreadCount,
  markNotificationsRead,
} from '../store/notificationsSlice';

const POLL_INTERVAL = 60000; // 1 minute

export function useNotifications() {
  const dispatch = useAppDispatch();
  const { notifications, unreadCount, isLoading } = useAppSelector(
    (state) => state.notifications
  );
  const { isAuthenticated } = useAppSelector((state) => state.auth);

  useEffect(() => {
    if (!isAuthenticated) return;

    dispatch(fetchNotifications());
    dispatch(fetchUnreadCount());

    const intervalId = setInterval(() => {
      dispatch(fetchUnreadCount());
    }, POLL_INTERVAL);

    return () => clearInterval(intervalId);
  }, [dispatch, isAuthenticated]);

  const markAsRead = useCallback(
    (notificationIds: string[]) => {
      dispatch(markNotificationsRead({ notification_ids: notificationIds }));
    },
    [dispatch]
  );

  const markAllAsRead = useCallback(() => {
    dispatch(markNotificationsRead({ mark_all: true }));
  }, [dispatch]);

  const refresh = useCallback(() => {
    dispatch(fetchNotifications());
    dispatch(fetchUnreadCount());
  }, [dispatch]);

  return {
    notifications,
    unreadCount,
    isLoading,
    markAsRead,
    markAllAsRead,
    refresh,
  };
}
