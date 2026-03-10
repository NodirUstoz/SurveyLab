import React, { useState } from 'react';
import { Question, QuestionOption } from '../../api/surveys';

interface QuestionRendererProps {
  question: Question;
  value: QuestionValue;
  onChange: (value: QuestionValue) => void;
  showNumber?: boolean;
  questionNumber?: number;
  error?: string | null;
}

export interface QuestionValue {
  text_value?: string;
  numeric_value?: number | null;
  selected_option_ids?: string[];
  matrix_values?: Record<string, string>;
  ranking_values?: string[];
}

const QuestionRenderer: React.FC<QuestionRendererProps> = ({
  question,
  value,
  onChange,
  showNumber = true,
  questionNumber,
  error,
}) => {
  const renderInput = () => {
    switch (question.question_type) {
      case 'multiple_choice':
        return (
          <div className="options-list">
            {question.options.map((opt) => (
              <label key={opt.id} className="option-label radio">
                <input
                  type="radio"
                  name={`q-${question.id}`}
                  checked={value.selected_option_ids?.includes(opt.id) || false}
                  onChange={() => onChange({ ...value, selected_option_ids: [opt.id] })}
                />
                <span>{opt.text}</span>
              </label>
            ))}
          </div>
        );

      case 'checkbox':
        return (
          <div className="options-list">
            {question.options.map((opt) => {
              const selected = value.selected_option_ids || [];
              const isChecked = selected.includes(opt.id);
              return (
                <label key={opt.id} className="option-label checkbox">
                  <input
                    type="checkbox"
                    checked={isChecked}
                    onChange={() => {
                      const updated = isChecked
                        ? selected.filter((id) => id !== opt.id)
                        : [...selected, opt.id];
                      onChange({ ...value, selected_option_ids: updated });
                    }}
                  />
                  <span>{opt.text}</span>
                </label>
              );
            })}
          </div>
        );

      case 'dropdown':
        return (
          <select
            className="form-control"
            value={value.selected_option_ids?.[0] || ''}
            onChange={(e) => onChange({ ...value, selected_option_ids: e.target.value ? [e.target.value] : [] })}
          >
            <option value="">Select an option...</option>
            {question.options.map((opt) => (
              <option key={opt.id} value={opt.id}>{opt.text}</option>
            ))}
          </select>
        );

      case 'open_ended':
        return (
          <textarea
            className="form-control"
            placeholder="Type your answer here..."
            value={value.text_value || ''}
            onChange={(e) => onChange({ ...value, text_value: e.target.value })}
            rows={4}
            maxLength={question.max_length || undefined}
          />
        );

      case 'rating':
        return (
          <div className="rating-scale">
            {question.rating_min_label && (
              <span className="scale-label">{question.rating_min_label}</span>
            )}
            <div className="rating-buttons">
              {Array.from(
                { length: question.rating_max - question.rating_min + 1 },
                (_, i) => question.rating_min + i
              ).map((num) => (
                <button
                  key={num}
                  className={`rating-button ${value.numeric_value === num ? 'selected' : ''}`}
                  onClick={() => onChange({ ...value, numeric_value: num })}
                  type="button"
                >
                  {num}
                </button>
              ))}
            </div>
            {question.rating_max_label && (
              <span className="scale-label">{question.rating_max_label}</span>
            )}
          </div>
        );

      case 'nps':
        return (
          <div className="nps-scale">
            <span className="scale-label">Not at all likely</span>
            <div className="nps-buttons">
              {Array.from({ length: 11 }, (_, i) => i).map((num) => (
                <button
                  key={num}
                  className={`nps-button ${value.numeric_value === num ? 'selected' : ''}`}
                  onClick={() => onChange({ ...value, numeric_value: num })}
                  type="button"
                >
                  {num}
                </button>
              ))}
            </div>
            <span className="scale-label">Extremely likely</span>
          </div>
        );

      case 'matrix':
        return (
          <div className="matrix-grid">
            <table>
              <thead>
                <tr>
                  <th></th>
                  {question.matrix_columns.map((col, i) => (
                    <th key={i}>{col}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {question.matrix_rows.map((row, rowIdx) => (
                  <tr key={rowIdx}>
                    <td className="row-label">{row}</td>
                    {question.matrix_columns.map((col, colIdx) => (
                      <td key={colIdx}>
                        <input
                          type="radio"
                          name={`matrix-${question.id}-${rowIdx}`}
                          checked={value.matrix_values?.[row] === col}
                          onChange={() =>
                            onChange({
                              ...value,
                              matrix_values: { ...(value.matrix_values || {}), [row]: col },
                            })
                          }
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );

      case 'date':
        return (
          <input
            type="date"
            className="form-control"
            value={value.text_value || ''}
            onChange={(e) => onChange({ ...value, text_value: e.target.value })}
          />
        );

      case 'file_upload':
        return (
          <div className="file-upload">
            <input
              type="file"
              className="form-control"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) {
                  onChange({ ...value, text_value: file.name });
                }
              }}
            />
          </div>
        );

      case 'ranking':
        return (
          <div className="ranking-list">
            <p className="ranking-instruction">Drag to reorder or click to rank</p>
            {question.options.map((opt, index) => {
              const rankPosition = (value.ranking_values || []).indexOf(opt.id);
              return (
                <div key={opt.id} className="ranking-item">
                  <span className="rank-number">
                    {rankPosition >= 0 ? rankPosition + 1 : '-'}
                  </span>
                  <span className="rank-text">{opt.text}</span>
                  <button
                    type="button"
                    className="rank-button"
                    onClick={() => {
                      const current = value.ranking_values || [];
                      const updated = current.includes(opt.id)
                        ? current.filter((id) => id !== opt.id)
                        : [...current, opt.id];
                      onChange({ ...value, ranking_values: updated });
                    }}
                  >
                    {(value.ranking_values || []).includes(opt.id) ? 'Remove' : 'Add'}
                  </button>
                </div>
              );
            })}
          </div>
        );

      default:
        return <p>Unsupported question type: {question.question_type}</p>;
    }
  };

  return (
    <div className={`question-renderer ${error ? 'has-error' : ''}`}>
      <div className="question-header">
        {showNumber && questionNumber && (
          <span className="question-number">Q{questionNumber}</span>
        )}
        <span className="question-text">
          {question.text}
          {question.is_required && <span className="required-marker"> *</span>}
        </span>
      </div>
      {question.description && (
        <p className="question-description">{question.description}</p>
      )}
      <div className="question-input">{renderInput()}</div>
      {error && <p className="question-error">{error}</p>}
    </div>
  );
};

export default QuestionRenderer;
