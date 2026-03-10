import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAppDispatch, useAppSelector } from '../store';
import { fetchSurveyDetail, publishSurvey, updateSurvey } from '../store/surveysSlice';
import surveysApi, { Question, SurveyPage as SurveyPageType } from '../api/surveys';

type QuestionTypeOption = {
  value: string;
  label: string;
  icon: string;
};

const QUESTION_TYPES: QuestionTypeOption[] = [
  { value: 'multiple_choice', label: 'Multiple Choice', icon: 'O' },
  { value: 'checkbox', label: 'Checkbox', icon: '#' },
  { value: 'rating', label: 'Rating Scale', icon: '*' },
  { value: 'nps', label: 'Net Promoter Score', icon: '!' },
  { value: 'open_ended', label: 'Open-Ended Text', icon: 'T' },
  { value: 'dropdown', label: 'Dropdown', icon: 'v' },
  { value: 'matrix', label: 'Matrix / Grid', icon: 'M' },
  { value: 'date', label: 'Date', icon: 'D' },
  { value: 'ranking', label: 'Ranking', icon: '=' },
  { value: 'file_upload', label: 'File Upload', icon: 'F' },
];

const SurveyBuilderPage: React.FC = () => {
  const { surveyId } = useParams<{ surveyId: string }>();
  const dispatch = useAppDispatch();
  const navigate = useNavigate();
  const { currentSurvey, isDetailLoading } = useAppSelector((state) => state.surveys);

  const [activePageIndex, setActivePageIndex] = useState(0);
  const [editingQuestion, setEditingQuestion] = useState<string | null>(null);
  const [showAddQuestion, setShowAddQuestion] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveMessage, setSaveMessage] = useState('');

  useEffect(() => {
    if (surveyId) {
      dispatch(fetchSurveyDetail(surveyId));
    }
  }, [dispatch, surveyId]);

  const pages = currentSurvey?.pages || [];
  const currentPage = pages[activePageIndex] || null;

  const handleAddPage = async () => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.createPage(surveyId, {
        title: `Page ${pages.length + 1}`,
        description: '',
      });
      dispatch(fetchSurveyDetail(surveyId));
      setActivePageIndex(pages.length);
      setSaveMessage('Page added.');
    } catch {
      setSaveMessage('Failed to add page.');
    }
    setIsSaving(false);
  };

  const handleDeletePage = async (pageId: string) => {
    if (!surveyId || pages.length <= 1) return;
    setIsSaving(true);
    try {
      await surveysApi.deletePage(surveyId, pageId);
      dispatch(fetchSurveyDetail(surveyId));
      if (activePageIndex >= pages.length - 1) {
        setActivePageIndex(Math.max(0, pages.length - 2));
      }
      setSaveMessage('Page deleted.');
    } catch {
      setSaveMessage('Failed to delete page.');
    }
    setIsSaving(false);
  };

  const handleAddQuestion = async (questionType: string) => {
    if (!surveyId || !currentPage) return;
    setIsSaving(true);
    setShowAddQuestion(false);
    try {
      await surveysApi.createQuestion(surveyId, currentPage.id, {
        question_type: questionType,
        text: 'New question',
        is_required: false,
        options: ['multiple_choice', 'checkbox', 'dropdown'].includes(questionType)
          ? [
              { text: 'Option 1', value: 'opt1', order: 0 } as any,
              { text: 'Option 2', value: 'opt2', order: 1 } as any,
            ]
          : undefined,
      } as any);
      dispatch(fetchSurveyDetail(surveyId));
      setSaveMessage('Question added.');
    } catch {
      setSaveMessage('Failed to add question.');
    }
    setIsSaving(false);
  };

  const handleUpdateQuestion = async (pageId: string, questionId: string, data: Partial<Question>) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.updateQuestion(surveyId, pageId, questionId, data);
      dispatch(fetchSurveyDetail(surveyId));
      setEditingQuestion(null);
      setSaveMessage('Question updated.');
    } catch {
      setSaveMessage('Failed to update question.');
    }
    setIsSaving(false);
  };

  const handleDeleteQuestion = async (pageId: string, questionId: string) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.deleteQuestion(surveyId, pageId, questionId);
      dispatch(fetchSurveyDetail(surveyId));
      setSaveMessage('Question deleted.');
    } catch {
      setSaveMessage('Failed to delete question.');
    }
    setIsSaving(false);
  };

  const handlePublish = async () => {
    if (!surveyId) return;
    const result = await dispatch(publishSurvey(surveyId));
    if (publishSurvey.fulfilled.match(result)) {
      setSaveMessage('Survey published successfully!');
    }
  };

  const handleSurveyTitleUpdate = async (title: string) => {
    if (!surveyId) return;
    await dispatch(updateSurvey({ id: surveyId, data: { title } }));
  };

  if (isDetailLoading || !currentSurvey) {
    return <div className="loading-spinner">Loading survey builder...</div>;
  }

  return (
    <div className="survey-builder-page">
      <div className="builder-toolbar">
        <button className="btn btn-text" onClick={() => navigate('/surveys')}>
          Back to Surveys
        </button>
        <div className="builder-title">
          <input
            type="text"
            className="title-input"
            defaultValue={currentSurvey.title}
            onBlur={(e) => handleSurveyTitleUpdate(e.target.value)}
          />
          <span className={`status-badge status-${currentSurvey.status}`}>
            {currentSurvey.status}
          </span>
        </div>
        <div className="builder-actions">
          {saveMessage && <span className="save-message">{saveMessage}</span>}
          {isSaving && <span className="saving-indicator">Saving...</span>}
          <button
            className="btn btn-secondary"
            onClick={() => navigate(`/surveys/${surveyId}/preview`)}
          >
            Preview
          </button>
          {currentSurvey.status === 'draft' && (
            <button className="btn btn-primary" onClick={handlePublish}>
              Publish
            </button>
          )}
        </div>
      </div>

      <div className="builder-layout">
        <aside className="builder-sidebar">
          <h3>Pages</h3>
          <ul className="page-list">
            {pages.map((page, index) => (
              <li
                key={page.id}
                className={`page-item ${index === activePageIndex ? 'active' : ''}`}
                onClick={() => setActivePageIndex(index)}
              >
                <span>{page.title || `Page ${index + 1}`}</span>
                <span className="question-count">
                  {page.questions?.length || 0} Q
                </span>
                {pages.length > 1 && (
                  <button
                    className="btn-icon btn-delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeletePage(page.id);
                    }}
                    title="Delete page"
                  >
                    x
                  </button>
                )}
              </li>
            ))}
          </ul>
          <button className="btn btn-outline btn-block" onClick={handleAddPage}>
            + Add Page
          </button>
        </aside>

        <main className="builder-canvas">
          {currentPage ? (
            <>
              <div className="page-header-edit">
                <input
                  type="text"
                  className="page-title-input"
                  defaultValue={currentPage.title}
                  placeholder="Page title"
                  onBlur={(e) => {
                    if (surveyId) {
                      surveysApi.updatePage(surveyId, currentPage.id, {
                        title: e.target.value,
                      });
                    }
                  }}
                />
              </div>

              <div className="questions-list">
                {(currentPage.questions || []).map((question, qIndex) => (
                  <div key={question.id} className="question-card">
                    <div className="question-card-header">
                      <span className="question-number">Q{qIndex + 1}</span>
                      <span className="question-type-label">
                        {QUESTION_TYPES.find((t) => t.value === question.question_type)?.label || question.question_type}
                      </span>
                      {question.is_required && (
                        <span className="required-badge">Required</span>
                      )}
                      <div className="question-actions">
                        <button
                          className="btn-icon"
                          onClick={() => setEditingQuestion(
                            editingQuestion === question.id ? null : question.id
                          )}
                        >
                          Edit
                        </button>
                        <button
                          className="btn-icon btn-delete"
                          onClick={() => handleDeleteQuestion(currentPage.id, question.id)}
                        >
                          Delete
                        </button>
                      </div>
                    </div>

                    {editingQuestion === question.id ? (
                      <QuestionEditor
                        question={question}
                        onSave={(data) => handleUpdateQuestion(currentPage.id, question.id, data)}
                        onCancel={() => setEditingQuestion(null)}
                      />
                    ) : (
                      <div className="question-preview">
                        <p className="question-text">{question.text}</p>
                        {question.description && (
                          <p className="question-description">{question.description}</p>
                        )}
                        {question.options && question.options.length > 0 && (
                          <ul className="options-preview">
                            {question.options.map((opt) => (
                              <li key={opt.id}>{opt.text}</li>
                            ))}
                          </ul>
                        )}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              <div className="add-question-section">
                {showAddQuestion ? (
                  <div className="question-type-picker">
                    <h4>Select Question Type</h4>
                    <div className="type-grid">
                      {QUESTION_TYPES.map((type) => (
                        <button
                          key={type.value}
                          className="type-option"
                          onClick={() => handleAddQuestion(type.value)}
                        >
                          <span className="type-icon">{type.icon}</span>
                          <span>{type.label}</span>
                        </button>
                      ))}
                    </div>
                    <button
                      className="btn btn-text"
                      onClick={() => setShowAddQuestion(false)}
                    >
                      Cancel
                    </button>
                  </div>
                ) : (
                  <button
                    className="btn btn-outline btn-block"
                    onClick={() => setShowAddQuestion(true)}
                  >
                    + Add Question
                  </button>
                )}
              </div>
            </>
          ) : (
            <div className="empty-state">
              <p>No pages yet. Add a page to start building your survey.</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

interface QuestionEditorProps {
  question: Question;
  onSave: (data: Partial<Question>) => void;
  onCancel: () => void;
}

const QuestionEditor: React.FC<QuestionEditorProps> = ({ question, onSave, onCancel }) => {
  const [text, setText] = useState(question.text);
  const [description, setDescription] = useState(question.description);
  const [isRequired, setIsRequired] = useState(question.is_required);
  const [ratingMin, setRatingMin] = useState(question.rating_min);
  const [ratingMax, setRatingMax] = useState(question.rating_max);

  const handleSubmit = () => {
    onSave({
      text,
      description,
      is_required: isRequired,
      rating_min: ratingMin,
      rating_max: ratingMax,
    });
  };

  return (
    <div className="question-editor">
      <div className="form-group">
        <label>Question Text</label>
        <textarea
          className="form-control"
          value={text}
          onChange={(e) => setText(e.target.value)}
          rows={2}
        />
      </div>
      <div className="form-group">
        <label>Description (optional)</label>
        <input
          type="text"
          className="form-control"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />
      </div>
      <div className="form-group form-check">
        <label>
          <input
            type="checkbox"
            checked={isRequired}
            onChange={(e) => setIsRequired(e.target.checked)}
          />
          Required
        </label>
      </div>
      {(question.question_type === 'rating' || question.question_type === 'nps') && (
        <div className="form-row">
          <div className="form-group">
            <label>Min</label>
            <input
              type="number"
              className="form-control"
              value={ratingMin}
              onChange={(e) => setRatingMin(Number(e.target.value))}
            />
          </div>
          <div className="form-group">
            <label>Max</label>
            <input
              type="number"
              className="form-control"
              value={ratingMax}
              onChange={(e) => setRatingMax(Number(e.target.value))}
            />
          </div>
        </div>
      )}
      <div className="editor-actions">
        <button className="btn btn-primary btn-sm" onClick={handleSubmit}>
          Save
        </button>
        <button className="btn btn-sm" onClick={onCancel}>
          Cancel
        </button>
      </div>
    </div>
  );
};

export default SurveyBuilderPage;
