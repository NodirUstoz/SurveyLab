import { createAsyncThunk, createSlice } from '@reduxjs/toolkit';
import analyticsApi, { AnalyticsSummary, SurveyAnalytics } from '../api/analytics';

interface AnalyticsState {
  dashboardSummaries: AnalyticsSummary[];
  currentAnalytics: SurveyAnalytics | null;
  isLoading: boolean;
  isRefreshing: boolean;
  error: string | null;
}

const initialState: AnalyticsState = {
  dashboardSummaries: [],
  currentAnalytics: null,
  isLoading: false,
  isRefreshing: false,
  error: null,
};

export const fetchDashboardSummaries = createAsyncThunk(
  'analytics/fetchDashboardSummaries',
  async (_, { rejectWithValue }) => {
    try {
      const response = await analyticsApi.getDashboardSummaries();
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to load dashboard analytics.');
    }
  }
);

export const fetchSurveyAnalytics = createAsyncThunk(
  'analytics/fetchSurveyAnalytics',
  async (surveyId: string, { rejectWithValue }) => {
    try {
      const response = await analyticsApi.getSurveyAnalytics(surveyId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to load survey analytics.');
    }
  }
);

export const refreshSurveyAnalytics = createAsyncThunk(
  'analytics/refreshSurveyAnalytics',
  async (surveyId: string, { rejectWithValue }) => {
    try {
      const response = await analyticsApi.refreshAnalytics(surveyId);
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to refresh analytics.');
    }
  }
);

const analyticsSlice = createSlice({
  name: 'analytics',
  initialState,
  reducers: {
    clearCurrentAnalytics: (state) => {
      state.currentAnalytics = null;
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchDashboardSummaries.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchDashboardSummaries.fulfilled, (state, action) => {
        state.isLoading = false;
        state.dashboardSummaries = action.payload;
      })
      .addCase(fetchDashboardSummaries.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchSurveyAnalytics.pending, (state) => {
        state.isLoading = true;
      })
      .addCase(fetchSurveyAnalytics.fulfilled, (state, action) => {
        state.isLoading = false;
        state.currentAnalytics = action.payload;
      })
      .addCase(fetchSurveyAnalytics.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(refreshSurveyAnalytics.pending, (state) => {
        state.isRefreshing = true;
      })
      .addCase(refreshSurveyAnalytics.fulfilled, (state, action) => {
        state.isRefreshing = false;
        state.currentAnalytics = action.payload;
      })
      .addCase(refreshSurveyAnalytics.rejected, (state, action) => {
        state.isRefreshing = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearCurrentAnalytics, clearError } = analyticsSlice.actions;
export default analyticsSlice.reducer;
