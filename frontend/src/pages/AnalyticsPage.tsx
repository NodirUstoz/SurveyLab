import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchSurveyAnalytics, refreshSurveyAnalytics } from '../store/analyticsSlice';
import { fetchSurveyDetail } from '../store/surveysSlice';
import { QuestionAnalytics } from '../api/analytics';
import { formatDuration, formatNumber } from '../utils/formatters';

const AnalyticsPage: React.FC = () => {
  const { surveyId } = useParams<{ surveyId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { currentSurvey } = useAppSelector((state) => state.surveys);
  const { currentAnalytics, isLoading, isRefreshing } = useAppSelector(
    (state) => state.analytics
  );
  const [activeTab, setActiveTab] = useState<'overview' | 'questions' | 'trends'>('overview');

  useEffect(() => {
    if (surveyId) {
      dispatch(fetchSurveyDetail(surveyId));
      dispatch(fetchSurveyAnalytics(surveyId));
    }
  }, [dispatch, surveyId]);

  const handleRefresh = () => {
    if (surveyId) {
      dispatch(refreshSurveyAnalytics(surveyId));
    }
  };

  if (isLoading || !currentAnalytics) {
    return <div className="loading-spinner">Loading analytics...</div>;
  }

  const analytics = currentAnalytics;

  return (
    <div className="analytics-page">
      <div className="page-header">
        <div>
          <button className="btn btn-text" onClick={() => navigate(`/surveys/${surveyId}`)}>
            Back to Survey
          </button>
          <h1>Analytics{currentSurvey ? `: ${currentSurvey.title}` : ''}</h1>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={handleRefresh}
            disabled={isRefreshing}
          >
            {isRefreshing ? 'Refreshing...' : 'Refresh Data'}
          </button>
          <button
            className="btn btn-primary"
            onClick={() => navigate(`/surveys/${surveyId}/reports`)}
          >
            Generate Report
          </button>
        </div>
      </div>

      <div className="analytics-stats-grid">
        <div className="stat-card large">
          <div className="stat-value">{formatNumber(analytics.total_responses)}</div>
          <div className="stat-label">Total Responses</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatNumber(analytics.complete_responses)}</div>
          <div className="stat-label">Complete</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{formatNumber(analytics.partial_responses)}</div>
          <div className="stat-label">Partial</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{analytics.completion_rate.toFixed(1)}%</div>
          <div className="stat-label">Completion Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {analytics.average_duration_seconds > 0
              ? formatDuration(analytics.average_duration_seconds)
              : 'N/A'}
          </div>
          <div className="stat-label">Avg Duration</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">
            {analytics.median_duration_seconds > 0
              ? formatDuration(analytics.median_duration_seconds)
              : 'N/A'}
          </div>
          <div className="stat-label">Median Duration</div>
        </div>
      </div>

      <div className="analytics-tabs">
        <button
          className={`tab ${activeTab === 'overview' ? 'active' : ''}`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`tab ${activeTab === 'questions' ? 'active' : ''}`}
          onClick={() => setActiveTab('questions')}
        >
          Question Results
        </button>
        <button
          className={`tab ${activeTab === 'trends' ? 'active' : ''}`}
          onClick={() => setActiveTab('trends')}
        >
          Trends
        </button>
      </div>

      <div className="analytics-content">
        {activeTab === 'overview' && (
          <div className="overview-section">
            <div className="analytics-grid">
              <div className="analytics-panel">
                <h3>Language Distribution</h3>
                <div className="distribution-list">
                  {Object.entries(analytics.language_distribution).map(([lang, count]) => (
                    <div key={lang} className="distribution-item">
                      <span className="dist-label">{lang.toUpperCase()}</span>
                      <div className="dist-bar-container">
                        <div
                          className="dist-bar"
                          style={{
                            width: `${(count / analytics.total_responses) * 100}%`,
                          }}
                        />
                      </div>
                      <span className="dist-count">{count}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="analytics-panel">
                <h3>Drop-off Rates by Page</h3>
                <div className="dropoff-list">
                  {Object.entries(analytics.drop_off_rates).map(([pageId, data]) => (
                    <div key={pageId} className="dropoff-item">
                      <span className="dropoff-label">{data.page_title}</span>
                      <div className="dropoff-bar-container">
                        <div
                          className="dropoff-bar"
                          style={{ width: `${100 - data.rate}%` }}
                        />
                      </div>
                      <span className="dropoff-rate">{data.rate}% drop-off</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'questions' && (
          <div className="questions-analytics">
            {analytics.question_analytics.map((qa) => (
              <QuestionAnalyticsCard key={qa.id} data={qa} totalResponses={analytics.total_responses} />
            ))}
          </div>
        )}

        {activeTab === 'trends' && (
          <div className="trends-section">
            <h3>Response Trend (Last 30 Days)</h3>
            <div className="trend-chart">
              {analytics.response_trend.length === 0 ? (
                <p className="text-muted">No trend data available.</p>
              ) : (
                <div className="simple-bar-chart">
                  {analytics.response_trend.map((point) => {
                    const maxCount = Math.max(...analytics.response_trend.map((p) => p.count), 1);
                    return (
                      <div key={point.date} className="bar-item">
                        <div
                          className="bar"
                          style={{ height: `${(point.count / maxCount) * 150}px` }}
                          title={`${point.date}: ${point.count} responses`}
                        />
                        <span className="bar-label">{point.date.slice(5)}</span>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

interface QuestionAnalyticsCardProps {
  data: QuestionAnalytics;
  totalResponses: number;
}

const QuestionAnalyticsCard: React.FC<QuestionAnalyticsCardProps> = ({ data, totalResponses }) => {
  const isChoiceBased = ['multiple_choice', 'checkbox', 'dropdown'].includes(data.question_type);
  const isNumeric = ['rating', 'nps'].includes(data.question_type);

  return (
    <div className="question-analytics-card">
      <div className="qa-header">
        <h4>{data.question_text}</h4>
        <span className="qa-type">{data.question_type.replace('_', ' ')}</span>
      </div>
      <div className="qa-stats">
        <span>{data.total_answers} answers</span>
        <span>{data.skip_count} skipped</span>
        <span>{data.answer_rate.toFixed(1)}% answer rate</span>
      </div>

      {isChoiceBased && Object.keys(data.option_distribution).length > 0 && (
        <div className="qa-distribution">
          {Object.entries(data.option_distribution).map(([optionId, count]) => (
            <div key={optionId} className="option-bar">
              <div className="option-info">
                <span className="option-id">{optionId.slice(0, 8)}</span>
                <span className="option-count">{count} ({((count / data.total_answers) * 100).toFixed(1)}%)</span>
              </div>
              <div className="bar-container">
                <div
                  className="bar-fill"
                  style={{ width: `${(count / Math.max(data.total_answers, 1)) * 100}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      )}

      {isNumeric && data.numeric_average !== null && (
        <div className="qa-numeric">
          <div className="numeric-stat">
            <span className="label">Average</span>
            <span className="value">{data.numeric_average.toFixed(2)}</span>
          </div>
          <div className="numeric-stat">
            <span className="label">Median</span>
            <span className="value">{data.numeric_median?.toFixed(2) ?? 'N/A'}</span>
          </div>
          {data.numeric_std_dev !== null && (
            <div className="numeric-stat">
              <span className="label">Std Dev</span>
              <span className="value">{data.numeric_std_dev.toFixed(2)}</span>
            </div>
          )}
          <div className="numeric-stat">
            <span className="label">Range</span>
            <span className="value">{data.numeric_min} - {data.numeric_max}</span>
          </div>
        </div>
      )}

      {data.question_type === 'nps' && data.nps_score !== null && (
        <div className="qa-nps">
          <div className="nps-score">
            <span className="nps-value">{data.nps_score.toFixed(0)}</span>
            <span className="nps-label">NPS Score</span>
          </div>
          <div className="nps-breakdown">
            <span className="promoters">Promoters: {data.nps_promoters}</span>
            <span className="passives">Passives: {data.nps_passives}</span>
            <span className="detractors">Detractors: {data.nps_detractors}</span>
          </div>
        </div>
      )}

      {data.question_type === 'open_ended' && Object.keys(data.word_cloud_data).length > 0 && (
        <div className="qa-wordcloud">
          <p>Avg text length: {data.average_text_length?.toFixed(0)} chars</p>
          <div className="word-tags">
            {Object.entries(data.word_cloud_data)
              .sort(([, a], [, b]) => b - a)
              .slice(0, 20)
              .map(([word, count]) => (
                <span key={word} className="word-tag" title={`${count} occurrences`}>
                  {word} ({count})
                </span>
              ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyticsPage;
