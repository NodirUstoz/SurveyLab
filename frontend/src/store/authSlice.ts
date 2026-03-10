import { createAsyncThunk, createSlice, PayloadAction } from '@reduxjs/toolkit';
import authApi, { LoginPayload, RegisterPayload, User } from '../api/auth';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  isAuthenticated: !!localStorage.getItem('access_token'),
  isLoading: false,
  error: null,
};

export const login = createAsyncThunk(
  'auth/login',
  async (credentials: LoginPayload, { rejectWithValue }) => {
    try {
      const response = await authApi.login(credentials);
      const { access, refresh } = response.data;
      localStorage.setItem('access_token', access);
      localStorage.setItem('refresh_token', refresh);

      const profileResponse = await authApi.getProfile();
      return profileResponse.data;
    } catch (error: any) {
      return rejectWithValue(
        error.response?.data?.detail || 'Login failed. Please check your credentials.'
      );
    }
  }
);

export const register = createAsyncThunk(
  'auth/register',
  async (data: RegisterPayload, { rejectWithValue }) => {
    try {
      const response = await authApi.register(data);
      const { user, tokens } = response.data;
      localStorage.setItem('access_token', tokens.access);
      localStorage.setItem('refresh_token', tokens.refresh);
      return user;
    } catch (error: any) {
      const errorData = error.response?.data;
      if (errorData && typeof errorData === 'object') {
        const firstError = Object.values(errorData).flat()[0];
        return rejectWithValue(String(firstError) || 'Registration failed.');
      }
      return rejectWithValue('Registration failed. Please try again.');
    }
  }
);

export const fetchProfile = createAsyncThunk(
  'auth/fetchProfile',
  async (_, { rejectWithValue }) => {
    try {
      const response = await authApi.getProfile();
      return response.data;
    } catch (error: any) {
      return rejectWithValue('Failed to fetch profile.');
    }
  }
);

export const logout = createAsyncThunk('auth/logout', async () => {
  const refreshToken = localStorage.getItem('refresh_token');
  if (refreshToken) {
    try {
      await authApi.logout(refreshToken);
    } catch {
      // Proceed with logout even if API call fails
    }
  }
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
});

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setUser: (state, action: PayloadAction<User>) => {
      state.user = action.payload;
      state.isAuthenticated = true;
    },
  },
  extraReducers: (builder) => {
    builder
      // Login
      .addCase(login.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(login.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(login.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Register
      .addCase(register.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(register.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload;
        state.isAuthenticated = true;
        state.error = null;
      })
      .addCase(register.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Fetch Profile
      .addCase(fetchProfile.fulfilled, (state, action) => {
        state.user = action.payload;
        state.isAuthenticated = true;
      })
      .addCase(fetchProfile.rejected, (state) => {
        state.user = null;
        state.isAuthenticated = false;
      })
      // Logout
      .addCase(logout.fulfilled, (state) => {
        state.user = null;
        state.isAuthenticated = false;
        state.error = null;
      });
  },
});

export const { clearError, setUser } = authSlice.actions;
export default authSlice.reducer;
