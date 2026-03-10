import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import reportsApi, { Report, CreateReportPayload } from '../api/reports';
import { useAppSelector } from '../store';
import { formatDate, formatFileSize } from '../utils/formatters';

const REPORT_TYPES = [
  { value: 'summary', label: 'Summary Report' },
  { value: 'detailed', label: 'Detailed Report' },
  { value: 'executive', label: 'Executive Summary' },
  { value: 'cross_tab', label: 'Cross-Tabulation Report' },
  { value: 'trend', label: 'Trend Analysis' },
];

const OUTPUT_FORMATS = [
  { value: 'pdf', label: 'PDF' },
  { value: 'html', label: 'HTML' },
  { value: 'docx', label: 'Word Document' },
];

const ReportsPage: React.FC = () => {
  const { surveyId } = useParams<{ surveyId: string }>();
  const navigate = useNavigate();
  const { currentSurvey } = useAppSelector((state) => state.surveys);

  const [reports, setReports] = useState<Report[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [isCreating, setIsCreating] = useState(false);

  // Create form state
  const [newReport, setNewReport] = useState<CreateReportPayload>({
    survey: surveyId || '',
    title: '',
    report_type: 'summary',
    output_format: 'pdf',
    include_summary: true,
    include_charts: true,
    include_individual_responses: false,
    include_open_ended: true,
    include_cross_tabs: false,
  });

  const loadReports = useCallback(async () => {
    if (!surveyId) return;
    setIsLoading(true);
    try {
      const response = await reportsApi.listForSurvey(surveyId);
      setReports(response.data);
    } catch {
      // Handled silently
    }
    setIsLoading(false);
  }, [surveyId]);

  useEffect(() => {
    loadReports();
  }, [loadReports]);

  const handleCreate = async () => {
    setIsCreating(true);
    try {
      const response = await reportsApi.create(newReport);
      const report = response.data;

      // Auto-generate
      await reportsApi.generate(report.id);
      setShowCreateDialog(false);
      loadReports();
    } catch {
      alert('Failed to create report.');
    }
    setIsCreating(false);
  };

  const handleDownload = async (reportId: string) => {
    try {
      const response = await reportsApi.download(reportId);
      window.open(response.data.download_url, '_blank');
    } catch {
      alert('Report is not ready for download yet.');
    }
  };

  const handleShare = async (reportId: string, currentlyShared: boolean) => {
    try {
      await reportsApi.share(reportId, !currentlyShared);
      loadReports();
    } catch {
      alert('Failed to update sharing.');
    }
  };

  const handleDelete = async (reportId: string) => {
    if (!confirm('Are you sure you want to delete this report?')) return;
    try {
      await reportsApi.delete(reportId);
      loadReports();
    } catch {
      alert('Failed to delete report.');
    }
  };

  const handleRegenerate = async (reportId: string) => {
    try {
      await reportsApi.generate(reportId);
      loadReports();
    } catch {
      alert('Failed to regenerate report.');
    }
  };

  const statusColors: Record<string, string> = {
    draft: '#6b7280',
    generating: '#3b82f6',
    ready: '#10b981',
    failed: '#ef4444',
  };

  return (
    <div className="reports-page">
      <div className="page-header">
        <div>
          <button className="btn btn-text" onClick={() => navigate(`/surveys/${surveyId}`)}>
            Back to Survey
          </button>
          <h1>Reports{currentSurvey ? `: ${currentSurvey.title}` : ''}</h1>
        </div>
        <button
          className="btn btn-primary"
          onClick={() => setShowCreateDialog(true)}
        >
          + New Report
        </button>
      </div>

      {showCreateDialog && (
        <div className="modal-overlay">
          <div className="modal modal-large">
            <h3>Create New Report</h3>
            <div className="form-grid">
              <div className="form-group">
                <label>Report Title</label>
                <input
                  type="text"
                  className="form-control"
                  value={newReport.title}
                  onChange={(e) => setNewReport({ ...newReport, title: e.target.value })}
                  placeholder="e.g., Q4 2025 Customer Satisfaction Report"
                />
              </div>
              <div className="form-group">
                <label>Report Type</label>
                <select
                  className="form-control"
                  value={newReport.report_type}
                  onChange={(e) => setNewReport({ ...newReport, report_type: e.target.value })}
                >
                  {REPORT_TYPES.map((t) => (
                    <option key={t.value} value={t.value}>{t.label}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>Output Format</label>
                <select
                  className="form-control"
                  value={newReport.output_format}
                  onChange={(e) => setNewReport({ ...newReport, output_format: e.target.value })}
                >
                  {OUTPUT_FORMATS.map((f) => (
                    <option key={f.value} value={f.value}>{f.label}</option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-checkboxes">
              <label>
                <input
                  type="checkbox"
                  checked={newReport.include_summary}
                  onChange={(e) => setNewReport({ ...newReport, include_summary: e.target.checked })}
                />
                Include Summary Statistics
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={newReport.include_charts}
                  onChange={(e) => setNewReport({ ...newReport, include_charts: e.target.checked })}
                />
                Include Charts
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={newReport.include_open_ended}
                  onChange={(e) => setNewReport({ ...newReport, include_open_ended: e.target.checked })}
                />
                Include Open-Ended Responses
              </label>
              <label>
                <input
                  type="checkbox"
                  checked={newReport.include_cross_tabs}
                  onChange={(e) => setNewReport({ ...newReport, include_cross_tabs: e.target.checked })}
                />
                Include Cross-Tabulations
              </label>
            </div>
            <div className="modal-actions">
              <button
                className="btn btn-primary"
                onClick={handleCreate}
                disabled={isCreating || !newReport.title}
              >
                {isCreating ? 'Creating...' : 'Create & Generate'}
              </button>
              <button
                className="btn"
                onClick={() => setShowCreateDialog(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {isLoading ? (
        <div className="loading-spinner">Loading reports...</div>
      ) : reports.length === 0 ? (
        <div className="empty-state">
          <h3>No reports yet</h3>
          <p>Generate a report to share survey results with your team.</p>
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateDialog(true)}
          >
            Create Your First Report
          </button>
        </div>
      ) : (
        <div className="reports-list">
          {reports.map((report) => (
            <div key={report.id} className="report-card">
              <div className="report-card-header">
                <h3>{report.title}</h3>
                <span
                  className="status-badge"
                  style={{ backgroundColor: statusColors[report.status] || '#6b7280' }}
                >
                  {report.status}
                </span>
              </div>
              <div className="report-card-meta">
                <span>{REPORT_TYPES.find((t) => t.value === report.report_type)?.label}</span>
                <span>{report.output_format.toUpperCase()}</span>
                {report.file_size_bytes && (
                  <span>{formatFileSize(report.file_size_bytes)}</span>
                )}
                <span>Created {formatDate(report.created_at)}</span>
                {report.generated_at && (
                  <span>Generated {formatDate(report.generated_at)}</span>
                )}
              </div>
              <div className="report-card-actions">
                {report.status === 'ready' && (
                  <button
                    className="btn btn-primary btn-sm"
                    onClick={() => handleDownload(report.id)}
                  >
                    Download
                  </button>
                )}
                {report.status === 'failed' && (
                  <button
                    className="btn btn-secondary btn-sm"
                    onClick={() => handleRegenerate(report.id)}
                  >
                    Retry
                  </button>
                )}
                <button
                  className="btn btn-sm"
                  onClick={() => handleShare(report.id, report.is_shared)}
                >
                  {report.is_shared ? 'Unshare' : 'Share'}
                </button>
                <button
                  className="btn btn-sm btn-danger"
                  onClick={() => handleDelete(report.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ReportsPage;
