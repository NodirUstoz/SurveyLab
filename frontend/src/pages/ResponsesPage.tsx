import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import responsesApi, { SurveyResponseListItem, SurveyResponse, ExportRequest } from '../api/responses';
import { useAppDispatch } from '../store';
import { fetchSurveyDetail } from '../store/surveysSlice';
import { useAppSelector } from '../store';
import { formatDate, formatDuration } from '../utils/formatters';

const ResponsesPage: React.FC = () => {
  const { surveyId } = useParams<{ surveyId: string }>();
  const navigate = useNavigate();
  const dispatch = useAppDispatch();
  const { currentSurvey } = useAppSelector((state) => state.surveys);

  const [responses, setResponses] = useState<SurveyResponseListItem[]>([]);
  const [selectedResponse, setSelectedResponse] = useState<SurveyResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDetailLoading, setIsDetailLoading] = useState(false);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [statusFilter, setStatusFilter] = useState('');
  const [isExporting, setIsExporting] = useState(false);
  const [showExportDialog, setShowExportDialog] = useState(false);

  useEffect(() => {
    if (surveyId) {
      dispatch(fetchSurveyDetail(surveyId));
    }
  }, [dispatch, surveyId]);

  const loadResponses = useCallback(async () => {
    if (!surveyId) return;
    setIsLoading(true);
    try {
      const params: Record<string, string> = {
        page: String(currentPage),
        page_size: '20',
      };
      if (statusFilter) params.status = statusFilter;
      const response = await responsesApi.listForSurvey(surveyId, params);
      setResponses(response.data.results);
      setTotalCount(response.data.count);
    } catch {
      // Error handled silently
    }
    setIsLoading(false);
  }, [surveyId, currentPage, statusFilter]);

  useEffect(() => {
    loadResponses();
  }, [loadResponses]);

  const handleViewResponse = async (responseId: string) => {
    setIsDetailLoading(true);
    try {
      const response = await responsesApi.get(responseId);
      setSelectedResponse(response.data);
    } catch {
      // Error handled silently
    }
    setIsDetailLoading(false);
  };

  const handleDeleteResponse = async (responseId: string) => {
    if (!confirm('Are you sure you want to delete this response?')) return;
    try {
      await responsesApi.delete(responseId);
      setSelectedResponse(null);
      loadResponses();
    } catch {
      // Error handled silently
    }
  };

  const handleExport = async (format: 'csv' | 'xlsx') => {
    if (!surveyId) return;
    setIsExporting(true);
    try {
      const exportData: ExportRequest = {
        format,
        status_filter: statusFilter || 'all',
      };
      const response = await responsesApi.export(surveyId, exportData);

      const blob = new Blob([response.data as any], {
        type: format === 'csv' ? 'text/csv' : 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${currentSurvey?.slug || 'survey'}-responses.${format}`;
      a.click();
      URL.revokeObjectURL(url);
      setShowExportDialog(false);
    } catch {
      alert('Export failed. Please try again.');
    }
    setIsExporting(false);
  };

  const totalPages = Math.ceil(totalCount / 20);

  const statusColors: Record<string, string> = {
    complete: '#10b981',
    partial: '#f59e0b',
    disqualified: '#ef4444',
  };

  return (
    <div className="responses-page">
      <div className="page-header">
        <div>
          <button className="btn btn-text" onClick={() => navigate(`/surveys/${surveyId}`)}>
            Back to Survey
          </button>
          <h1>Responses{currentSurvey ? `: ${currentSurvey.title}` : ''}</h1>
          <p className="text-muted">{totalCount} total responses</p>
        </div>
        <div className="header-actions">
          <button
            className="btn btn-secondary"
            onClick={() => setShowExportDialog(true)}
          >
            Export
          </button>
        </div>
      </div>

      <div className="filters-bar">
        <select
          className="filter-select"
          value={statusFilter}
          onChange={(e) => {
            setStatusFilter(e.target.value);
            setCurrentPage(1);
          }}
        >
          <option value="">All Statuses</option>
          <option value="complete">Complete</option>
          <option value="partial">Partial</option>
          <option value="disqualified">Disqualified</option>
        </select>
      </div>

      {showExportDialog && (
        <div className="modal-overlay">
          <div className="modal">
            <h3>Export Responses</h3>
            <p>Choose a format to export response data.</p>
            <div className="export-options">
              <button
                className="btn btn-primary"
                onClick={() => handleExport('csv')}
                disabled={isExporting}
              >
                {isExporting ? 'Exporting...' : 'Export CSV'}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => handleExport('xlsx')}
                disabled={isExporting}
              >
                {isExporting ? 'Exporting...' : 'Export Excel'}
              </button>
            </div>
            <button className="btn btn-text" onClick={() => setShowExportDialog(false)}>
              Cancel
            </button>
          </div>
        </div>
      )}

      <div className="responses-layout">
        <div className="responses-list-panel">
          {isLoading ? (
            <div className="loading-spinner">Loading responses...</div>
          ) : responses.length === 0 ? (
            <div className="empty-state">
              <p>No responses yet.</p>
            </div>
          ) : (
            <>
              <table className="responses-table">
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Status</th>
                    <th>Language</th>
                    <th>Duration</th>
                    <th>Answers</th>
                    <th>Submitted</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {responses.map((resp) => (
                    <tr
                      key={resp.id}
                      className={selectedResponse?.id === resp.id ? 'selected' : ''}
                    >
                      <td>{resp.id.slice(0, 8)}</td>
                      <td>
                        <span
                          className="status-badge-small"
                          style={{ color: statusColors[resp.status] || '#6b7280' }}
                        >
                          {resp.status}
                        </span>
                      </td>
                      <td>{resp.language.toUpperCase()}</td>
                      <td>{resp.duration_seconds ? formatDuration(resp.duration_seconds) : '-'}</td>
                      <td>{resp.answer_count}</td>
                      <td>{formatDate(resp.submitted_at)}</td>
                      <td>
                        <button
                          className="btn btn-sm"
                          onClick={() => handleViewResponse(resp.id)}
                        >
                          View
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>

              {totalPages > 1 && (
                <div className="pagination">
                  <button
                    className="btn btn-sm"
                    disabled={currentPage === 1}
                    onClick={() => setCurrentPage((p) => p - 1)}
                  >
                    Previous
                  </button>
                  <span>Page {currentPage} of {totalPages}</span>
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

        {selectedResponse && (
          <div className="response-detail-panel">
            {isDetailLoading ? (
              <div className="loading-spinner">Loading response...</div>
            ) : (
              <>
                <div className="detail-header">
                  <h3>Response Details</h3>
                  <button
                    className="btn btn-sm btn-danger"
                    onClick={() => handleDeleteResponse(selectedResponse.id)}
                  >
                    Delete
                  </button>
                </div>
                <div className="detail-meta">
                  <p><strong>Status:</strong> {selectedResponse.status}</p>
                  <p><strong>Language:</strong> {selectedResponse.language}</p>
                  <p><strong>Duration:</strong> {selectedResponse.duration_seconds ? formatDuration(selectedResponse.duration_seconds) : 'N/A'}</p>
                  <p><strong>Submitted:</strong> {formatDate(selectedResponse.submitted_at)}</p>
                </div>
                <div className="answers-list">
                  <h4>Answers ({selectedResponse.answers.length})</h4>
                  {selectedResponse.answers.map((answer) => (
                    <div key={answer.id} className="answer-card">
                      <p className="answer-question">
                        <strong>{answer.question_text}</strong>
                        <span className="answer-type">{answer.question_type}</span>
                      </p>
                      <p className="answer-value">
                        {answer.display_value || <em>No answer</em>}
                      </p>
                    </div>
                  ))}
                </div>
              </>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ResponsesPage;
