/**
 * Validation Utilities for Report Card Assistant Frontend
 * 
 * Client-side validation functions for forms, user input, and data integrity.
 * Works in conjunction with backend validation for comprehensive security.
 */

// Email validation regex pattern
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

// Validation result type
export interface ValidationResult {
  isValid: boolean;
  error?: string;
}

// Form field validation results
export interface FormValidationResult {
  isValid: boolean;
  errors: Record<string, string>;
}

/**
 * Validate email address format
 * 
 * @param email - Email address to validate
 * @returns ValidationResult with validity and error message
 */
export function validateEmail(email: string): ValidationResult {
  // Check for empty email
  if (!email || email.trim() === '') {
    return {
      isValid: false,
      error: 'Email address is required',
    };
  }

  // Check email format
  if (!EMAIL_REGEX.test(email.trim())) {
    return {
      isValid: false,
      error: 'Please enter a valid email address',
    };
  }

  // Check for reasonable length
  if (email.trim().length > 254) {
    return {
      isValid: false,
      error: 'Email address is too long',
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Validate password requirements
 * 
 * @param password - Password to validate
 * @returns ValidationResult with validity and error message
 */
export function validatePassword(password: string): ValidationResult {
  // Check for empty password
  if (!password || password === '') {
    return {
      isValid: false,
      error: 'Password is required',
    };
  }

  // Check minimum length (basic requirement)
  if (password.length < 6) {
    return {
      isValid: false,
      error: 'Password must be at least 6 characters long',
    };
  }

  // Check maximum length (prevent DoS attacks)
  if (password.length > 128) {
    return {
      isValid: false,
      error: 'Password is too long',
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Validate required field (non-empty string)
 * 
 * @param value - Value to validate
 * @param fieldName - Name of the field for error message
 * @returns ValidationResult with validity and error message
 */
export function validateRequired(value: string, fieldName: string): ValidationResult {
  if (!value || value.trim() === '') {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Validate login form data
 * 
 * @param formData - Login form data
 * @returns FormValidationResult with overall validity and field errors
 */
export function validateLoginForm(formData: {
  email: string;
  password: string;
}): FormValidationResult {
  const errors: Record<string, string> = {};

  // Validate email
  const emailValidation = validateEmail(formData.email);
  if (!emailValidation.isValid && emailValidation.error) {
    errors.email = emailValidation.error;
  }

  // Validate password
  const passwordValidation = validatePassword(formData.password);
  if (!passwordValidation.isValid && passwordValidation.error) {
    errors.password = passwordValidation.error;
  }

  return {
    isValid: Object.keys(errors).length === 0,
    errors,
  };
}

/**
 * Clean and normalize email address
 * 
 * @param email - Raw email input
 * @returns Cleaned email address
 */
export function normalizeEmail(email: string): string {
  return email.trim().toLowerCase();
}

/**
 * Sanitize user input to prevent XSS attacks
 * Basic sanitization for display purposes
 * 
 * @param input - User input string
 * @returns Sanitized string
 */
export function sanitizeInput(input: string): string {
  return input
    .replace(/[<>]/g, '') // Remove angle brackets
    .replace(/javascript:/gi, '') // Remove javascript: protocol
    .replace(/on\w+=/gi, '') // Remove event handlers
    .trim();
}

/**
 * Validate grade score (0-100 range)
 * 
 * @param score - Grade score to validate
 * @returns ValidationResult with validity and error message
 */
export function validateGradeScore(score: number | string): ValidationResult {
  // Convert to number if string
  const numericScore = typeof score === 'string' ? parseFloat(score) : score;

  // Check if it's a valid number
  if (isNaN(numericScore)) {
    return {
      isValid: false,
      error: 'Grade must be a valid number',
    };
  }

  // Check range (0-100)
  if (numericScore < 0 || numericScore > 100) {
    return {
      isValid: false,
      error: 'Grade must be between 0 and 100',
    };
  }

  // Check for reasonable decimal places (max 2)
  if (numericScore.toString().includes('.')) {
    const decimalPlaces = numericScore.toString().split('.')[1].length;
    if (decimalPlaces > 2) {
      return {
        isValid: false,
        error: 'Grade can have at most 2 decimal places',
      };
    }
  }

  return {
    isValid: true,
  };
}

/**
 * Check if a string contains only letters, numbers, spaces, and common punctuation
 * Useful for validating names, titles, etc.
 * 
 * @param input - String to validate
 * @param fieldName - Name of field for error message
 * @returns ValidationResult with validity and error message
 */
export function validateTextContent(input: string, fieldName: string): ValidationResult {
  if (!input || input.trim() === '') {
    return {
      isValid: false,
      error: `${fieldName} is required`,
    };
  }

  // Allow letters, numbers, spaces, and common punctuation
  const allowedPattern = /^[a-zA-Z0-9\s.,!?'-]*$/;
  
  if (!allowedPattern.test(input)) {
    return {
      isValid: false,
      error: `${fieldName} contains invalid characters`,
    };
  }

  // Check reasonable length
  if (input.length > 500) {
    return {
      isValid: false,
      error: `${fieldName} is too long (maximum 500 characters)`,
    };
  }

  return {
    isValid: true,
  };
}

/**
 * Debounce function for validation
 * Useful for real-time validation without excessive API calls
 * 
 * @param func - Function to debounce
 * @param wait - Wait time in milliseconds
 * @returns Debounced function
 */
export function debounce<T extends (...args: unknown[]) => unknown>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

/**
 * Format error message for display
 * Standardizes error message formatting across the application
 * 
 * @param error - Error message or Error object
 * @returns Formatted error message
 */
export function formatErrorMessage(error: string | Error | unknown): string {
  if (typeof error === 'string') {
    return error;
  }
  
  if (error instanceof Error) {
    return error.message;
  }
  
  return 'An unexpected error occurred';
}

// Common validation patterns for reuse
export const VALIDATION_PATTERNS = {
  email: EMAIL_REGEX,
  phoneNumber: /^\+?[\d\s\-\(\)]+$/,
  studentId: /^[A-Z]{2,3}[0-9]{3,4}$/i, // Format like "RPS001"
  classCode: /^[A-Z\d\s]+$/i, // Format like "Primary 4A"
} as const;

// Common field length limits
export const FIELD_LIMITS = {
  email: 254,
  password: 128,
  name: 100,
  description: 500,
  title: 200,
} as const;