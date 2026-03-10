import { useEffect } from 'react';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchProfile, logout as logoutAction, login, register } from '../store/authSlice';
import { LoginPayload, RegisterPayload } from '../api/auth';

export function useAuth() {
  const dispatch = useAppDispatch();
  const { user, isAuthenticated, isLoading, error } = useAppSelector(
    (state) => state.auth
  );

  useEffect(() => {
    if (isAuthenticated && !user) {
      dispatch(fetchProfile());
    }
  }, [dispatch, isAuthenticated, user]);

  const handleLogin = async (credentials: LoginPayload) => {
    const result = await dispatch(login(credentials));
    return login.fulfilled.match(result);
  };

  const handleRegister = async (data: RegisterPayload) => {
    const result = await dispatch(register(data));
    return register.fulfilled.match(result);
  };

  const handleLogout = async () => {
    await dispatch(logoutAction());
  };

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login: handleLogin,
    register: handleRegister,
    logout: handleLogout,
  };
}
