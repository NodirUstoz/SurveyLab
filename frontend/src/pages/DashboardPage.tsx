import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchSurveys } from '../store/surveysSlice';
import { fetchDashboardSummaries } from '../store/analyticsSlice';
import { fetchUnreadCount } from '../store/notificationsSlice';
import { formatDuration, formatDate, formatNumber } from '../utils/formatters';

const DashboardPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { user } = useAppSelector((state) => state.auth);
  const { surveys, isLoading: surveysLoading } = useAppSelector((state) => state.surveys);
  const { dashboardSummaries, isLoading: analyticsLoading } = useAppSelector((state) => state.analytics);
  const { unreadCount } = useAppSelector((state) => state.notifications);

  useEffect(() => {
    dispatch(fetchSurveys({ page_size: '5', ordering: '-created_at' }));
    dispatch(fetchDashboardSummaries());
    dispatch(fetchUnreadCount());
  }, [dispatch]);

  const totalResponses = dashboardSummaries.reduce(
    (sum, s) => sum + s.total_responses, 0
  );
  const activeSurveys = surveys.filter((s) => s.status === 'published').length;
  const averageCompletionRate = dashboardSummaries.length > 0
    ? dashboardSummaries.reduce((sum, s) => sum + s.completion_rate, 0) / dashboardSummaries.length
    : 0;

  const statusColorMap: Record<string, string> = {
    draft: '#6b7280',
    published: '#10b981',
    closed: '#ef4444',
    archived: '#8b5cf6',
  };

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div>
          <h1>Welcome back, {user?.first_name || user?.username || 'User'}</h1>
          <p className="text-muted">
            Here is an overview of your survey activity.
          </p>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/surveys/new')}
        >
          Create Survey
        </button>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-value">{formatNumber(surveys.length)}</div>
          <div className="stat-label">Total Surveys</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatNumber(activeSurveys)}</div>
          <div className="stat-label">Active Surveys</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatNumber(totalResponses)}</div>
          <div className="stat-label">Total Responses</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{averageCompletionRate.toFixed(1)}%</div>
          <div className="stat-label">Avg Completion Rate</div>
        </div>
      </div>

      {unreadCount > 0 && (
        <div className="notification-banner" onClick={() => navigate('/notifications')}>
          You have {unreadCount} unread notification{unreadCount !== 1 ? 's' : ''}.
        </div>
      )}

      <div className="dashboard-sections">
        <section className="recent-surveys">
          <div className="section-header">
            <h2>Recent Surveys</h2>
            <button className="btn btn-text" onClick={() => navigate('/surveys')}>
              View All
            </button>
          </div>
          {surveysLoading ? (
            <div className="loading-spinner">Loading surveys...</div>
          ) : surveys.length === 0 ? (
            <div className="empty-state">
              <p>No surveys yet. Create your first survey to get started.</p>
              <button
                className="btn btn-primary"
                onClick={() => navigate('/surveys/new')}
              >
                Create Your First Survey
              </button>
            </div>
          ) : (
            <div className="survey-list">
              {surveys.slice(0, 5).map((survey) => (
                <div
                  key={survey.id}
                  className="survey-card"
                  onClick={() => navigate(`/surveys/${survey.id}`)}
                >
                  <div className="survey-card-header">
                    <h3>{survey.title}</h3>
                    <span
                      className="status-badge"
                      style={{ backgroundColor: statusColorMap[survey.status] || '#6b7280' }}
                    >
                      {survey.status}
                    </span>
                  </div>
                  <p className="survey-card-description">
                    {survey.description || 'No description'}
                  </p>
                  <div className="survey-card-footer">
                    <span>{survey.question_count} questions</span>
                    <span>{survey.response_count} responses</span>
                    <span>{formatDate(survey.created_at)}</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>

        <section className="analytics-summary">
          <div className="section-header">
            <h2>Analytics Overview</h2>
            <button className="btn btn-text" onClick={() => navigate('/analytics')}>
              View Details
            </button>
          </div>
          {analyticsLoading ? (
            <div className="loading-spinner">Loading analytics...</div>
          ) : dashboardSummaries.length === 0 ? (
            <div className="empty-state">
              <p>No analytics data available yet.</p>
            </div>
          ) : (
            <div className="analytics-list">
              {dashboardSummaries.slice(0, 5).map((summary) => (
                <div key={summary.id} className="analytics-item">
                  <div className="analytics-item-title">{summary.survey_title}</div>
                  <div className="analytics-item-stats">
                    <span>{summary.total_responses} responses</span>
                    <span>{summary.completion_rate.toFixed(1)}% completion</span>
                    <span>
                      {summary.average_duration_seconds > 0
                        ? formatDuration(summary.average_duration_seconds)
                        : 'N/A'}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default DashboardPage;
