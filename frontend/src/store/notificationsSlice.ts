import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import apiClient from '../api/client';

export interface Notification {
  id: string;
  notification_type: string;
  priority: string;
  title: string;
  message: string;
  action_url: string;
  related_survey: string | null;
  metadata: Record<string, unknown>;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
}

interface NotificationsState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
}

const initialState: NotificationsState = {
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null,
};

export const fetchNotifications = createAsyncThunk(
  'notifications/fetch',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/notifications/');
      return response.data.results || response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to load notifications.');
    }
  }
);

export const fetchUnreadCount = createAsyncThunk(
  'notifications/fetchUnreadCount',
  async (_, { rejectWithValue }) => {
    try {
      const response = await apiClient.get('/notifications/unread-count/');
      return response.data.unread_count;
    } catch (error: any) {
      return rejectWithValue('Failed to fetch unread count.');
    }
  }
);

export const markNotificationsRead = createAsyncThunk(
  'notifications/markRead',
  async (
    payload: { notification_ids?: string[]; mark_all?: boolean },
    { rejectWithValue }
  ) => {
    try {
      const response = await apiClient.post('/notifications/mark-read/', payload);
      return { ...payload, marked: response.data.marked_read };
    } catch (error: any) {
      return rejectWithValue('Failed to mark notifications as read.');
    }
  }
);

const notificationsSlice = createSlice({
  name: 'notifications',
  initialState,
  reducers: {
    clearNotificationError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchNotifications.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchNotifications.fulfilled, (state, action) => {
        state.isLoading = false;
        state.notifications = action.payload;
      })
      .addCase(fetchNotifications.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchUnreadCount.fulfilled, (state, action) => {
        state.unreadCount = action.payload;
      })
      .addCase(markNotificationsRead.fulfilled, (state, action) => {
        const { notification_ids, mark_all } = action.payload;
        if (mark_all) {
          state.notifications.forEach((n) => { n.is_read = true; });
          state.unreadCount = 0;
        } else if (notification_ids) {
          state.notifications.forEach((n) => {
            if (notification_ids.includes(n.id)) {
              n.is_read = true;
            }
          });
          state.unreadCount = Math.max(0, state.unreadCount - notification_ids.length);
        }
      });
  },
});

export const { clearNotificationError } = notificationsSlice.actions;
export default notificationsSlice.reducer;
