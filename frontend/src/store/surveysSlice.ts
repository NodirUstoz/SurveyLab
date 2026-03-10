import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import surveysApi, { CreateSurveyPayload, Survey } from '../api/surveys';

interface SurveysState {
  surveys: Survey[];
  currentSurvey: Survey | null;
  totalCount: number;
  currentPage: number;
  isLoading: boolean;
  isDetailLoading: boolean;
  error: string | null;
  filters: {
    status: string;
    category: string;
    search: string;
  };
}

const initialState: SurveysState = {
  surveys: [],
  currentSurvey: null,
  totalCount: 0,
  currentPage: 1,
  isLoading: false,
  isDetailLoading: false,
  error: null,
  filters: {
    status: '',
    category: '',
    search: '',
  },
};

export const fetchSurveys = createAsyncThunk(
  'surveys/fetchSurveys',
  async (params: Record<string, string> | undefined, { rejectWithValue }) => {
    try {
      const response = await surveysApi.list(params);
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to load surveys.');
    }
  }
);

export const fetchSurveyDetail = createAsyncThunk(
  'surveys/fetchSurveyDetail',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await surveysApi.get(id);
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to load survey details.');
    }
  }
);

export const createSurvey = createAsyncThunk(
  'surveys/createSurvey',
  async (data: CreateSurveyPayload, { rejectWithValue }) => {
    try {
      const response = await surveysApi.create(data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Failed to create survey.'
      );
    }
  }
);

export const updateSurvey = createAsyncThunk(
  'surveys/updateSurvey',
  async ({ id, data }: { id: string; data: Partial<Survey> }, { rejectWithValue }) => {
    try {
      const response = await surveysApi.update(id, data);
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to update survey.');
    }
  }
);

export const publishSurvey = createAsyncThunk(
  'surveys/publishSurvey',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await surveysApi.publish(id);
      return response.data;
    } catch (error: any) {
      const errors = error.response?.data?.errors;
      return rejectWithValue(
        errors ? errors.join(' ') : 'Failed to publish survey.'
      );
    }
  }
);

export const deleteSurvey = createAsyncThunk(
  'surveys/deleteSurvey',
  async (id: string, { rejectWithValue }) => {
    try {
      await surveysApi.delete(id);
      return id;
    } catch (error: any) {
      return rejectWithValue('Failed to delete survey.');
    }
  }
);

export const duplicateSurvey = createAsyncThunk(
  'surveys/duplicateSurvey',
  async (id: string, { rejectWithValue }) => {
    try {
      const response = await surveysApi.duplicate(id);
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to duplicate survey.');
    }
  }
);

const surveysSlice = createSlice({
  name: 'surveys',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setFilters: (state, action: PayloadAction<Partial<SurveysState['filters']>>) => {
      state.filters = { ...state.filters, ...action.payload };
    },
    clearCurrentSurvey: (state) => {
      state.currentSurvey = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchSurveys.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchSurveys.fulfilled, (state, action) => {
        state.isLoading = false;
        state.surveys = action.payload.results;
        state.totalCount = action.payload.count;
      })
      .addCase(fetchSurveys.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      .addCase(fetchSurveyDetail.pending, (state) => {
        state.isDetailLoading = true;
      })
      .addCase(fetchSurveyDetail.fulfilled, (state, action) => {
        state.isDetailLoading = false;
        state.currentSurvey = action.payload;
      })
      .addCase(fetchSurveyDetail.rejected, (state, action) => {
        state.isDetailLoading = false;
        state.error = action.payload as string;
      })
      .addCase(createSurvey.fulfilled, (state, action) => {
        state.surveys.unshift(action.payload);
        state.totalCount += 1;
      })
      .addCase(updateSurvey.fulfilled, (state, action) => {
        const index = state.surveys.findIndex((s) => s.id === action.payload.id);
        if (index !== -1) {
          state.surveys[index] = action.payload;
        }
        if (state.currentSurvey?.id === action.payload.id) {
          state.currentSurvey = action.payload;
        }
      })
      .addCase(publishSurvey.fulfilled, (state, action) => {
        const index = state.surveys.findIndex((s) => s.id === action.payload.id);
        if (index !== -1) {
          state.surveys[index] = action.payload;
        }
        if (state.currentSurvey?.id === action.payload.id) {
          state.currentSurvey = action.payload;
        }
      })
      .addCase(deleteSurvey.fulfilled, (state, action) => {
        state.surveys = state.surveys.filter((s) => s.id !== action.payload);
        state.totalCount -= 1;
        if (state.currentSurvey?.id === action.payload) {
          state.currentSurvey = null;
        }
      })
      .addCase(duplicateSurvey.fulfilled, (state, action) => {
        state.surveys.unshift(action.payload);
        state.totalCount += 1;
      });
  },
});

export const { clearError, setFilters, clearCurrentSurvey } = surveysSlice.actions;
export default surveysSlice.reducer;
