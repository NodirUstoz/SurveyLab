import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Survey } from '../../api/surveys';
import StatusBadge from '../common/StatusBadge';
import { formatDate } from '../../utils/formatters';

interface SurveyCardProps {
  survey: Survey;
  onDuplicate?: (id: string) => void;
  onDelete?: (id: string) => void;
}

const SurveyCard: React.FC<SurveyCardProps> = ({ survey, onDuplicate, onDelete }) => {
  const navigate = useNavigate();

  return (
    <div
      style={{
        backgroundColor: '#fff',
        border: '1px solid #e5e7eb',
        borderRadius: 12,
        padding: 20,
        transition: 'box-shadow 0.2s',
        cursor: 'default',
      }}
    >
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 12 }}>
        <h3
          style={{
            margin: 0,
            fontSize: 16,
            fontWeight: 600,
            color: '#1f2937',
            cursor: 'pointer',
          }}
          onClick={() => navigate(`/surveys/${survey.id}`)}
        >
          {survey.title}
        </h3>
        <StatusBadge status={survey.status} />
      </div>

      <p style={{ color: '#6b7280', fontSize: 13, margin: '0 0 16px', lineHeight: 1.5 }}>
        {survey.description ? survey.description.slice(0, 120) : 'No description'}
      </p>

      <div style={{ display: 'flex', gap: 16, fontSize: 13, color: '#9ca3af', marginBottom: 12 }}>
        <span>{survey.question_count} questions</span>
        <span>{survey.response_count} responses</span>
        {survey.category && <span>{survey.category}</span>}
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <span style={{ fontSize: 12, color: '#9ca3af' }}>
          Created {formatDate(survey.created_at)}
        </span>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            style={actionButtonStyle}
            onClick={() => navigate(`/surveys/${survey.id}/builder`)}
          >
            Edit
          </button>
          <button
            style={actionButtonStyle}
            onClick={() => navigate(`/surveys/${survey.id}/responses`)}
          >
            Responses
          </button>
          {onDuplicate && (
            <button style={actionButtonStyle} onClick={() => onDuplicate(survey.id)}>
              Duplicate
            </button>
          )}
          {onDelete && (
            <button
              style={{ ...actionButtonStyle, color: '#ef4444' }}
              onClick={() => onDelete(survey.id)}
            >
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

const actionButtonStyle: React.CSSProperties = {
  padding: '4px 10px',
  fontSize: 12,
  border: '1px solid #e5e7eb',
  borderRadius: 6,
  backgroundColor: '#fff',
  color: '#374151',
  cursor: 'pointer',
};

export default SurveyCard;
