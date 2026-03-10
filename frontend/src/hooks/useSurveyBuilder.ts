import { useState, useCallback, useEffect } from 'react';
import surveysApi, { Survey, SurveyPage, Question } from '../api/surveys';

interface UseSurveyBuilderReturn {
  survey: Survey | null;
  pages: SurveyPage[];
  activePageIndex: number;
  setActivePageIndex: (index: number) => void;
  isLoading: boolean;
  isSaving: boolean;
  error: string | null;
  reload: () => Promise<void>;
  addPage: (title?: string) => Promise<void>;
  deletePage: (pageId: string) => Promise<void>;
  updatePage: (pageId: string, data: Partial<SurveyPage>) => Promise<void>;
  addQuestion: (pageId: string, questionType: string) => Promise<void>;
  updateQuestion: (pageId: string, questionId: string, data: Partial<Question>) => Promise<void>;
  deleteQuestion: (pageId: string, questionId: string) => Promise<void>;
  reorderPages: (pageOrder: string[]) => Promise<void>;
}

export function useSurveyBuilder(surveyId: string | undefined): UseSurveyBuilderReturn {
  const [survey, setSurvey] = useState<Survey | null>(null);
  const [activePageIndex, setActivePageIndex] = useState(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    if (!surveyId) return;
    setIsLoading(true);
    try {
      const response = await surveysApi.get(surveyId);
      setSurvey(response.data);
      setError(null);
    } catch {
      setError('Failed to load survey.');
    }
    setIsLoading(false);
  }, [surveyId]);

  useEffect(() => {
    reload();
  }, [reload]);

  const pages = survey?.pages || [];

  const addPage = useCallback(async (title?: string) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.createPage(surveyId, {
        title: title || `Page ${pages.length + 1}`,
      });
      await reload();
      setActivePageIndex(pages.length);
    } catch {
      setError('Failed to add page.');
    }
    setIsSaving(false);
  }, [surveyId, pages.length, reload]);

  const deletePage = useCallback(async (pageId: string) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.deletePage(surveyId, pageId);
      await reload();
      if (activePageIndex >= pages.length - 1) {
        setActivePageIndex(Math.max(0, pages.length - 2));
      }
    } catch {
      setError('Failed to delete page.');
    }
    setIsSaving(false);
  }, [surveyId, pages.length, activePageIndex, reload]);

  const updatePage = useCallback(async (pageId: string, data: Partial<SurveyPage>) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.updatePage(surveyId, pageId, data);
      await reload();
    } catch {
      setError('Failed to update page.');
    }
    setIsSaving(false);
  }, [surveyId, reload]);

  const addQuestion = useCallback(async (pageId: string, questionType: string) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.createQuestion(surveyId, pageId, {
        question_type: questionType,
        text: 'New question',
        is_required: false,
      } as any);
      await reload();
    } catch {
      setError('Failed to add question.');
    }
    setIsSaving(false);
  }, [surveyId, reload]);

  const updateQuestion = useCallback(async (
    pageId: string, questionId: string, data: Partial<Question>
  ) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.updateQuestion(surveyId, pageId, questionId, data);
      await reload();
    } catch {
      setError('Failed to update question.');
    }
    setIsSaving(false);
  }, [surveyId, reload]);

  const deleteQuestion = useCallback(async (pageId: string, questionId: string) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.deleteQuestion(surveyId, pageId, questionId);
      await reload();
    } catch {
      setError('Failed to delete question.');
    }
    setIsSaving(false);
  }, [surveyId, reload]);

  const reorderPages = useCallback(async (pageOrder: string[]) => {
    if (!surveyId) return;
    setIsSaving(true);
    try {
      await surveysApi.reorderPages(surveyId, pageOrder);
      await reload();
    } catch {
      setError('Failed to reorder pages.');
    }
    setIsSaving(false);
  }, [surveyId, reload]);

  return {
    survey,
    pages,
    activePageIndex,
    setActivePageIndex,
    isLoading,
    isSaving,
    error,
    reload,
    addPage,
    deletePage,
    updatePage,
    addQuestion,
    updateQuestion,
    deleteQuestion,
    reorderPages,
  };
}
