import apiClient from './client';

export interface SurveyAnalytics {
  id: string;
  survey: string;
  total_responses: number;
  complete_responses: number;
  partial_responses: number;
  disqualified_responses: number;
  completion_rate: number;
  average_duration_seconds: number;
  median_duration_seconds: number;
  total_views: number;
  unique_visitors: number;
  drop_off_rates: Record<string, { page_title: string; respondents_reached: number; rate: number }>;
  response_trend: Array<{ date: string; count: number }>;
  language_distribution: Record<string, number>;
  device_distribution: Record<string, number>;
  last_response_at: string | null;
  question_analytics: QuestionAnalytics[];
  updated_at: string;
}

export interface QuestionAnalytics {
  id: string;
  question: string;
  question_text: string;
  question_type: string;
  total_answers: number;
  skip_count: number;
  answer_rate: number;
  option_distribution: Record<string, number>;
  numeric_average: number | null;
  numeric_median: number | null;
  numeric_std_dev: number | null;
  numeric_min: number | null;
  numeric_max: number | null;
  nps_score: number | null;
  nps_promoters: number;
  nps_passives: number;
  nps_detractors: number;
  word_cloud_data: Record<string, number>;
  average_text_length: number | null;
  matrix_aggregation: Record<string, Record<string, number>>;
  updated_at: string;
}

export interface AnalyticsSummary {
  id: string;
  survey: string;
  survey_title: string;
  total_responses: number;
  complete_responses: number;
  completion_rate: number;
  average_duration_seconds: number;
  last_response_at: string | null;
  updated_at: string;
}

export interface CrossTabulation {
  id: string;
  survey: string;
  question_a: string;
  question_a_text: string;
  question_b: string;
  question_b_text: string;
  contingency_table: Record<string, Record<string, number>>;
  chi_square_statistic: number | null;
  p_value: number | null;
  cramers_v: number | null;
  created_at: string;
}

const analyticsApi = {
  getSurveyAnalytics: (surveyId: string) =>
    apiClient.get<SurveyAnalytics>(`/analytics/survey/${surveyId}/`),

  refreshAnalytics: (surveyId: string) =>
    apiClient.post<SurveyAnalytics>(`/analytics/survey/${surveyId}/refresh/`),

  getDashboardSummaries: () =>
    apiClient.get<AnalyticsSummary[]>('/analytics/dashboard/'),

  getCrossTabulations: (surveyId: string) =>
    apiClient.get<CrossTabulation[]>(`/analytics/survey/${surveyId}/cross-tabulation/`),

  createCrossTabulation: (surveyId: string, questionAId: string, questionBId: string) =>
    apiClient.post<CrossTabulation>(`/analytics/survey/${surveyId}/cross-tabulation/`, {
      question_a_id: questionAId,
      question_b_id: questionBId,
    }),
};

export default analyticsApi;
