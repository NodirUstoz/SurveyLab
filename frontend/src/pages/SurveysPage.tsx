import React, { useEffect, useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchSurveys, deleteSurvey, duplicateSurvey, setFilters } from '../store/surveysSlice';
import { formatDate } from '../utils/formatters';
import { useDebounce } from '../hooks/useDebounce';

const STATUS_OPTIONS = [
  { value: '', label: 'All Statuses' },
  { value: 'draft', label: 'Draft' },
  { value: 'published', label: 'Published' },
  { value: 'closed', label: 'Closed' },
  { value: 'archived', label: 'Archived' },
];

const SurveysPage: React.FC = () => {
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { surveys, totalCount, isLoading, filters } = useAppSelector(
    (state) => state.surveys
  );
  const [searchInput, setSearchInput] = useState(filters.search);
  const [currentPage, setCurrentPage] = useState(1);
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);

  const debouncedSearch = useDebounce(searchInput, 300);

  const loadSurveys = useCallback(() => {
    const params: Record<string, string> = {
      page: String(currentPage),
      page_size: '12',
    };
    if (filters.status) params.status = filters.status;
    if (debouncedSearch) params.search = debouncedSearch;
    dispatch(fetchSurveys(params));
  }, [dispatch, currentPage, filters.status, debouncedSearch]);

  useEffect(() => {
    loadSurveys();
  }, [loadSurveys]);

  const handleDelete = async (id: string) => {
    await dispatch(deleteSurvey(id));
    setConfirmDelete(null);
  };

  const handleDuplicate = async (id: string) => {
    await dispatch(duplicateSurvey(id));
  };

  const totalPages = Math.ceil(totalCount / 12);

  const statusColorMap: Record<string, string> = {
    draft: '#6b7280',
    published: '#10b981',
    closed: '#ef4444',
    archived: '#8b5cf6',
  };

  return (
    <div className="surveys-page">
      <div className="page-header">
        <h1>Surveys</h1>
        <button
          className="btn btn-primary"
          onClick={() => navigate('/surveys/new')}
        >
          + Create Survey
        </button>
      </div>

      <div className="filters-bar">
        <input
          type="text"
          className="search-input"
          placeholder="Search surveys..."
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
        />
        <select
          className="filter-select"
          value={filters.status}
          onChange={(e) => {
            dispatch(setFilters({ status: e.target.value }));
            setCurrentPage(1);
          }}
        >
          {STATUS_OPTIONS.map((opt) => (
            <option key={opt.value} value={opt.value}>
              {opt.label}
            </option>
          ))}
        </select>
      </div>

      {isLoading ? (
        <div className="loading-spinner">Loading surveys...</div>
      ) : surveys.length === 0 ? (
        <div className="empty-state">
          <h3>No surveys found</h3>
          <p>
            {filters.status || searchInput
              ? 'Try adjusting your filters or search query.'
              : 'Create your first survey to get started.'}
          </p>
        </div>
      ) : (
        <>
          <div className="surveys-grid">
            {surveys.map((survey) => (
              <div key={survey.id} className="survey-card">
                <div className="survey-card-header">
                  <h3
                    className="survey-card-title"
                    onClick={() => navigate(`/surveys/${survey.id}`)}
                  >
                    {survey.title}
                  </h3>
                  <span
                    className="status-badge"
                    style={{ backgroundColor: statusColorMap[survey.status] || '#6b7280' }}
                  >
                    {survey.status}
                  </span>
                </div>
                <p className="survey-card-description">
                  {survey.description || 'No description provided'}
                </p>
                <div className="survey-card-stats">
                  <span>{survey.question_count} questions</span>
                  <span>{survey.response_count} responses</span>
                </div>
                <div className="survey-card-meta">
                  <span>Created {formatDate(survey.created_at)}</span>
                  {survey.published_at && (
                    <span>Published {formatDate(survey.published_at)}</span>
                  )}
                </div>
                <div className="survey-card-actions">
                  <button
                    className="btn btn-sm"
                    onClick={() => navigate(`/surveys/${survey.id}/builder`)}
                  >
                    Edit
                  </button>
                  <button
                    className="btn btn-sm"
                    onClick={() => navigate(`/surveys/${survey.id}/responses`)}
                  >
                    Responses
                  </button>
                  <button
                    className="btn btn-sm"
                    onClick={() => navigate(`/surveys/${survey.id}/analytics`)}
                  >
                    Analytics
                  </button>
                  <button
                    className="btn btn-sm"
                    onClick={() => handleDuplicate(survey.id)}
                  >
                    Duplicate
                  </button>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => setConfirmDelete(survey.id)}
                  >
                    Delete
                  </button>
                </div>
                {confirmDelete === survey.id && (
                  <div className="confirm-dialog">
                    <p>Are you sure you want to delete this survey?</p>
                    <button
                      className="btn btn-danger btn-sm"
                      onClick={() => handleDelete(survey.id)}
                    >
                      Confirm
                    </button>
                    <button
                      className="btn btn-sm"
                      onClick={() => setConfirmDelete(null)}
                    >
                      Cancel
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>

          {totalPages > 1 && (
            <div className="pagination">
              <button
                className="btn btn-sm"
                disabled={currentPage === 1}
                onClick={() => setCurrentPage((p) => p - 1)}
              >
                Previous
              </button>
              <span className="page-info">
                Page {currentPage} of {totalPages}
              </span>
              <button
                className="btn btn-sm"
                disabled={currentPage === totalPages}
                onClick={() => setCurrentPage((p) => p + 1)}
              >
                Next
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default SurveysPage;
