import apiClient from './client';

export interface User {
  id: string;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  organization: Organization | null;
  role: 'owner' | 'admin' | 'editor' | 'viewer';
  avatar: string | null;
  phone: string;
  preferred_language: string;
  timezone: string;
  email_notifications: boolean;
  created_at: string;
  updated_at: string;
}

export interface Organization {
  id: string;
  name: string;
  slug: string;
  logo: string | null;
  website: string;
  plan: 'free' | 'starter' | 'professional' | 'enterprise';
  max_surveys: number;
  max_responses_per_survey: number;
  is_active: boolean;
  member_count: number;
  created_at: string;
  updated_at: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  email: string;
  username: string;
  password: string;
  password_confirm: string;
  first_name?: string;
  last_name?: string;
  organization_name?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
}

export interface RegisterResponse {
  user: User;
  tokens: AuthTokens;
}

const authApi = {
  login: (data: LoginPayload) =>
    apiClient.post<LoginResponse>('/auth/login/', data),

  register: (data: RegisterPayload) =>
    apiClient.post<RegisterResponse>('/auth/register/', data),

  logout: (refreshToken: string) =>
    apiClient.post('/auth/logout/', { refresh: refreshToken }),

  refreshToken: (refreshToken: string) =>
    apiClient.post<{ access: string }>('/auth/token/refresh/', { refresh: refreshToken }),

  getProfile: () =>
    apiClient.get<User>('/auth/profile/'),

  updateProfile: (data: Partial<User>) =>
    apiClient.patch<User>('/auth/profile/', data),

  changePassword: (data: { old_password: string; new_password: string; new_password_confirm: string }) =>
    apiClient.post('/auth/change-password/', data),

  getOrganization: () =>
    apiClient.get<Organization>('/auth/organization/'),

  updateOrganization: (data: Partial<Organization>) =>
    apiClient.patch<Organization>('/auth/organization/', data),

  getOrganizationMembers: () =>
    apiClient.get<User[]>('/auth/organization/members/'),
};

export default authApi;
