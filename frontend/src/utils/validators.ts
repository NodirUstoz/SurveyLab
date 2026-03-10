/**
 * Validation utilities for forms and data input.
 */

export interface ValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

/**
 * Validate an email address format.
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return emailRegex.test(email.trim());
}

/**
 * Validate a password meets minimum requirements.
 */
export function validatePassword(password: string): string[] {
  const errors: string[] = [];

  if (password.length < 8) {
    errors.push('Password must be at least 8 characters long.');
  }
  if (!/[A-Z]/.test(password)) {
    errors.push('Password must contain at least one uppercase letter.');
  }
  if (!/[a-z]/.test(password)) {
    errors.push('Password must contain at least one lowercase letter.');
  }
  if (!/[0-9]/.test(password)) {
    errors.push('Password must contain at least one digit.');
  }

  return errors;
}

/**
 * Validate a survey title.
 */
export function validateSurveyTitle(title: string): string | null {
  const trimmed = title.trim();
  if (!trimmed) return 'Survey title is required.';
  if (trimmed.length < 3) return 'Title must be at least 3 characters.';
  if (trimmed.length > 500) return 'Title must not exceed 500 characters.';
  return null;
}

/**
 * Validate a question.
 */
export function validateQuestion(question: {
  text: string;
  question_type: string;
  options?: Array<{ text: string }>;
  matrix_rows?: string[];
  matrix_columns?: string[];
}): string[] {
  const errors: string[] = [];

  if (!question.text.trim()) {
    errors.push('Question text is required.');
  }

  const choiceTypes = ['multiple_choice', 'checkbox', 'dropdown', 'ranking'];
  if (choiceTypes.includes(question.question_type)) {
    const validOptions = (question.options || []).filter((o) => o.text.trim());
    if (validOptions.length < 2) {
      errors.push('At least 2 options are required for this question type.');
    }
  }

  if (question.question_type === 'matrix') {
    if (!question.matrix_rows || question.matrix_rows.length === 0) {
      errors.push('Matrix questions need at least one row.');
    }
    if (!question.matrix_columns || question.matrix_columns.length === 0) {
      errors.push('Matrix questions need at least one column.');
    }
  }

  return errors;
}

/**
 * Validate a survey response answer against question requirements.
 */
export function validateAnswer(
  answer: {
    text_value?: string;
    numeric_value?: number | null;
    selected_option_ids?: string[];
    matrix_values?: Record<string, string>;
    ranking_values?: string[];
  },
  question: {
    question_type: string;
    is_required: boolean;
    min_length?: number | null;
    max_length?: number | null;
    matrix_rows?: string[];
    options?: Array<{ id: string }>;
  }
): string | null {
  if (!question.is_required) return null;

  switch (question.question_type) {
    case 'open_ended':
      if (!answer.text_value?.trim()) return 'This question requires an answer.';
      if (question.min_length && answer.text_value.length < question.min_length) {
        return `Answer must be at least ${question.min_length} characters.`;
      }
      if (question.max_length && answer.text_value.length > question.max_length) {
        return `Answer must not exceed ${question.max_length} characters.`;
      }
      break;

    case 'multiple_choice':
    case 'dropdown':
      if (!answer.selected_option_ids || answer.selected_option_ids.length === 0) {
        return 'Please select an option.';
      }
      break;

    case 'checkbox':
      if (!answer.selected_option_ids || answer.selected_option_ids.length === 0) {
        return 'Please select at least one option.';
      }
      break;

    case 'rating':
    case 'nps':
      if (answer.numeric_value === null || answer.numeric_value === undefined) {
        return 'Please provide a rating.';
      }
      break;

    case 'matrix':
      if (!answer.matrix_values || Object.keys(answer.matrix_values).length === 0) {
        return 'Please complete the matrix.';
      }
      if (question.matrix_rows) {
        const answeredRows = Object.keys(answer.matrix_values);
        const missingRows = question.matrix_rows.filter((r) => !answeredRows.includes(r));
        if (missingRows.length > 0) {
          return `Please answer all rows in the matrix.`;
        }
      }
      break;

    case 'ranking':
      if (!answer.ranking_values || answer.ranking_values.length === 0) {
        return 'Please rank all options.';
      }
      if (question.options && answer.ranking_values.length < question.options.length) {
        return 'Please rank all options.';
      }
      break;

    case 'date':
      if (!answer.text_value?.trim()) return 'Please select a date.';
      break;
  }

  return null;
}

/**
 * Validate a list of email addresses.
 */
export function validateEmailList(emails: string[]): { valid: string[]; invalid: string[] } {
  const valid: string[] = [];
  const invalid: string[] = [];

  for (const email of emails) {
    const trimmed = email.trim();
    if (trimmed) {
      if (isValidEmail(trimmed)) {
        valid.push(trimmed);
      } else {
        invalid.push(trimmed);
      }
    }
  }

  return { valid, invalid };
}
