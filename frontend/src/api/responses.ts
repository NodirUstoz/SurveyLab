import apiClient, { PaginatedResponse } from './client';

export interface SurveyResponse {
  id: string;
  survey: string;
  respondent: string | null;
  status: 'complete' | 'partial' | 'disqualified';
  language: string;
  duration_seconds: number | null;
  metadata: Record<string, unknown>;
  answers: Answer[];
  submitted_at: string;
}

export interface SurveyResponseListItem {
  id: string;
  survey: string;
  status: string;
  language: string;
  duration_seconds: number | null;
  answer_count: number;
  submitted_at: string;
}

export interface Answer {
  id: string;
  question: string;
  question_text: string;
  question_type: string;
  text_value: string;
  numeric_value: number | null;
  selected_option_ids: string[];
  matrix_values: Record<string, string>;
  file_upload: string | null;
  ranking_values: string[];
  display_value: string;
  answered_at: string;
}

export interface SubmitAnswerPayload {
  question_id: string;
  text_value?: string;
  numeric_value?: number | null;
  selected_option_ids?: string[];
  matrix_values?: Record<string, string>;
  ranking_values?: string[];
}

export interface SubmitResponsePayload {
  survey_id: string;
  session_key?: string;
  language?: string;
  answers: SubmitAnswerPayload[];
  duration_seconds?: number;
  metadata?: Record<string, unknown>;
}

export interface ExportRequest {
  format: 'csv' | 'xlsx' | 'pdf';
  date_from?: string;
  date_to?: string;
  status_filter?: 'all' | 'complete' | 'partial' | 'disqualified';
}

const responsesApi = {
  listForSurvey: (surveyId: string, params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<SurveyResponseListItem>>(
      `/responses/survey/${surveyId}/`, { params }
    ),

  get: (id: string) =>
    apiClient.get<SurveyResponse>(`/responses/${id}/`),

  delete: (id: string) =>
    apiClient.delete(`/responses/${id}/`),

  submit: (data: SubmitResponsePayload) =>
    apiClient.post<{ detail: string; response_id: string }>('/responses/submit/', data),

  savePartial: (data: {
    survey_id: string;
    session_key: string;
    current_page: number;
    answers: SubmitAnswerPayload[];
    language?: string;
  }) =>
    apiClient.post('/responses/save-partial/', data),

  resumeSession: (sessionKey: string) =>
    apiClient.get(`/responses/resume/${sessionKey}/`),

  export: (surveyId: string, data: ExportRequest) =>
    apiClient.post(`/responses/survey/${surveyId}/export/`, data, {
      responseType: data.format === 'csv' ? 'text' : 'blob',
    }),
};

export default responsesApi;
