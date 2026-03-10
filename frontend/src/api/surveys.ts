import apiClient, { PaginatedResponse } from './client';

export interface Survey {
  id: string;
  title: string;
  description: string;
  slug: string;
  status: 'draft' | 'published' | 'closed' | 'archived';
  category: string;
  tags: string[];
  default_language: string;
  supported_languages: string[];
  welcome_message: string;
  thank_you_message: string;
  question_count: number;
  response_count: number;
  owner_name: string;
  published_at: string | null;
  closes_at: string | null;
  created_at: string;
  updated_at: string;
  pages?: SurveyPage[];
  settings?: SurveySettings;
  branching_rules?: BranchingRule[];
}

export interface SurveySettings {
  allow_anonymous: boolean;
  require_login: boolean;
  one_response_per_user: boolean;
  show_progress_bar: boolean;
  shuffle_questions: boolean;
  allow_back_navigation: boolean;
  show_question_numbers: boolean;
  max_responses: number | null;
  quota_rules: unknown[];
  theme_color: string;
  logo: string | null;
  custom_css: string;
  notify_on_response: boolean;
  notification_emails: string[];
}

export interface SurveyPage {
  id: string;
  survey: string;
  title: string;
  description: string;
  order: number;
  is_visible: boolean;
  questions: Question[];
}

export interface Question {
  id: string;
  page: string;
  question_type: string;
  text: string;
  description: string;
  is_required: boolean;
  order: number;
  translations: Record<string, string>;
  config: Record<string, unknown>;
  matrix_rows: string[];
  matrix_columns: string[];
  rating_min: number;
  rating_max: number;
  rating_min_label: string;
  rating_max_label: string;
  min_length: number | null;
  max_length: number | null;
  validation_regex: string;
  options: QuestionOption[];
  created_at: string;
  updated_at: string;
}

export interface QuestionOption {
  id: string;
  text: string;
  value: string;
  order: number;
  is_other: boolean;
  translations: Record<string, string>;
  quota_limit: number | null;
  quota_count: number;
}

export interface BranchingRule {
  id: string;
  survey: string;
  source_question: string;
  operator: string;
  value: string;
  action: string;
  target_page: string | null;
  target_question: string | null;
  order: number;
  is_active: boolean;
}

export interface CreateSurveyPayload {
  title: string;
  description?: string;
  slug?: string;
  category?: string;
  tags?: string[];
  settings?: Partial<SurveySettings>;
}

const surveysApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Survey>>('/surveys/', { params }),

  get: (id: string) =>
    apiClient.get<Survey>(`/surveys/${id}/`),

  create: (data: CreateSurveyPayload) =>
    apiClient.post<Survey>('/surveys/', data),

  update: (id: string, data: Partial<Survey>) =>
    apiClient.patch<Survey>(`/surveys/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/surveys/${id}/`),

  publish: (id: string) =>
    apiClient.post<Survey>(`/surveys/${id}/publish/`),

  close: (id: string) =>
    apiClient.post<Survey>(`/surveys/${id}/close/`),

  duplicate: (id: string) =>
    apiClient.post<Survey>(`/surveys/${id}/duplicate/`),

  getSettings: (id: string) =>
    apiClient.get<SurveySettings>(`/surveys/${id}/settings/`),

  updateSettings: (id: string, data: Partial<SurveySettings>) =>
    apiClient.patch<SurveySettings>(`/surveys/${id}/settings/`, data),

  reorderPages: (id: string, pageOrder: string[]) =>
    apiClient.post(`/surveys/${id}/reorder-pages/`, { page_order: pageOrder }),

  // Pages
  listPages: (surveyId: string) =>
    apiClient.get<SurveyPage[]>(`/surveys/${surveyId}/pages/`),

  createPage: (surveyId: string, data: Partial<SurveyPage>) =>
    apiClient.post<SurveyPage>(`/surveys/${surveyId}/pages/`, data),

  updatePage: (surveyId: string, pageId: string, data: Partial<SurveyPage>) =>
    apiClient.patch<SurveyPage>(`/surveys/${surveyId}/pages/${pageId}/`, data),

  deletePage: (surveyId: string, pageId: string) =>
    apiClient.delete(`/surveys/${surveyId}/pages/${pageId}/`),

  // Questions
  createQuestion: (surveyId: string, pageId: string, data: Partial<Question>) =>
    apiClient.post<Question>(`/surveys/${surveyId}/pages/${pageId}/questions/`, data),

  updateQuestion: (surveyId: string, pageId: string, questionId: string, data: Partial<Question>) =>
    apiClient.patch<Question>(`/surveys/${surveyId}/pages/${pageId}/questions/${questionId}/`, data),

  deleteQuestion: (surveyId: string, pageId: string, questionId: string) =>
    apiClient.delete(`/surveys/${surveyId}/pages/${pageId}/questions/${questionId}/`),

  // Public
  getPublicSurvey: (slug: string) =>
    apiClient.get<Survey>(`/surveys/public/${slug}/`),
};

export default surveysApi;
