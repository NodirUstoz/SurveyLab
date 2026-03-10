import apiClient, { PaginatedResponse } from './client';

export interface Report {
  id: string;
  survey: string;
  survey_title: string;
  created_by: string;
  created_by_name: string;
  title: string;
  report_type: 'summary' | 'detailed' | 'executive' | 'cross_tab' | 'trend' | 'comparison' | 'custom';
  output_format: 'pdf' | 'docx' | 'pptx' | 'html';
  status: 'draft' | 'generating' | 'ready' | 'failed';
  config: Record<string, unknown>;
  include_summary: boolean;
  include_charts: boolean;
  include_individual_responses: boolean;
  include_open_ended: boolean;
  include_cross_tabs: boolean;
  date_range_start: string | null;
  date_range_end: string | null;
  response_status_filter: string;
  file: string | null;
  file_size_bytes: number | null;
  is_shared: boolean;
  share_token: string;
  created_at: string;
  updated_at: string;
  generated_at: string | null;
}

export interface CreateReportPayload {
  survey: string;
  title: string;
  report_type: string;
  output_format: string;
  include_summary?: boolean;
  include_charts?: boolean;
  include_individual_responses?: boolean;
  include_open_ended?: boolean;
  include_cross_tabs?: boolean;
  date_range_start?: string;
  date_range_end?: string;
  response_status_filter?: string;
}

const reportsApi = {
  list: (params?: Record<string, string>) =>
    apiClient.get<PaginatedResponse<Report>>('/reports/', { params }),

  get: (id: string) =>
    apiClient.get<Report>(`/reports/${id}/`),

  create: (data: CreateReportPayload) =>
    apiClient.post<Report>('/reports/', data),

  update: (id: string, data: Partial<Report>) =>
    apiClient.patch<Report>(`/reports/${id}/`, data),

  delete: (id: string) =>
    apiClient.delete(`/reports/${id}/`),

  generate: (id: string) =>
    apiClient.post(`/reports/${id}/generate/`),

  share: (id: string, isShared: boolean, password?: string) =>
    apiClient.post(`/reports/${id}/share/`, { is_shared: isShared, password }),

  download: (id: string) =>
    apiClient.get<{ download_url: string; file_size_bytes: number }>(`/reports/${id}/download/`),

  listForSurvey: (surveyId: string) =>
    apiClient.get<Report[]>(`/reports/survey/${surveyId}/`),

  getSharedReport: (shareToken: string, password?: string) =>
    apiClient.get<Report>(`/reports/shared/${shareToken}/`, {
      params: password ? { password } : {},
    }),
};

export default reportsApi;
