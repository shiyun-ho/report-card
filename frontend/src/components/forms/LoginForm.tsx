'use client';

/**
 * Login Form Component for Report Card Assistant
 * 
 * Handles user authentication with client-side validation and error handling.
 * Integrates with AuthContext for session management and Docker-based backend communication.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { validateLoginForm, normalizeEmail, formatErrorMessage } from '@/lib/validation';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

// Component props interface
interface LoginFormProps {
  onSuccess?: () => void;
  className?: string;
}

/**
 * Login Form Component
 * 
 * Provides email/password authentication form with validation and error handling.
 * Uses shadcn/ui components for consistent styling.
 */
export function LoginForm({ onSuccess, className }: LoginFormProps) {
  // Authentication context
  const { login, isLoading, error: authError, clearError } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    email: '',
    password: '',
  });

  // Validation state
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({});
  const [hasSubmitted, setHasSubmitted] = useState(false);

  // Loading state for form submission
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Clear auth error when component mounts or form data changes
  useEffect(() => {
    if (authError) {
      clearError();
    }
  }, [formData, authError, clearError]);

  /**
   * Handle form input changes
   */
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    
    // Update form data
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));

    // Clear validation error for this field if it exists
    if (validationErrors[name]) {
      setValidationErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  /**
   * Validate form and show errors
   */
  const validateForm = (): boolean => {
    const validation = validateLoginForm({
      email: normalizeEmail(formData.email),
      password: formData.password,
    });

    setValidationErrors(validation.errors);
    return validation.isValid;
  };

  /**
   * Handle form submission
   */
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setHasSubmitted(true);
    setIsSubmitting(true);

    // Clear any previous auth errors
    if (authError) {
      clearError();
    }

    // Validate form
    const isValid = validateForm();
    
    if (!isValid) {
      setIsSubmitting(false);
      return;
    }

    try {
      // Attempt login via AuthContext (which uses Docker network backend)
      await login(normalizeEmail(formData.email), formData.password);
      
      // Call success callback if provided
      onSuccess?.();
      
      // Reset form on successful login
      setFormData({
        email: '',
        password: '',
      });
      setHasSubmitted(false);
      
    } catch (error) {
      // Error is handled by AuthContext and displayed via authError
      console.error('Login form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  /**
   * Get field error message
   */
  const getFieldError = (fieldName: string): string | undefined => {
    return validationErrors[fieldName];
  };

  /**
   * Check if field has error
   */
  const hasFieldError = (fieldName: string): boolean => {
    return hasSubmitted && !!getFieldError(fieldName);
  };

  return (
    <Card className={className}>
      <CardHeader className="text-center">
        <CardTitle>Welcome Back</CardTitle>
        <CardDescription>
          Sign in to access the Report Card Assistant
        </CardDescription>
      </CardHeader>

      <form onSubmit={handleSubmit}>
        <CardContent className="space-y-4">
          {/* Global error display */}
          {authError && (
            <div className="rounded-md bg-red-50 p-4 border border-red-200">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <p className="text-sm font-medium text-red-800">
                    {formatErrorMessage(authError)}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Email field */}
          <div className="space-y-2">
            <Label htmlFor="email">Email Address</Label>
            <Input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
              onChange={handleInputChange}
              placeholder="Enter your email address"
              aria-invalid={hasFieldError('email')}
              className={hasFieldError('email') ? 'border-red-500' : ''}
              disabled={isSubmitting || isLoading}
            />
            {hasFieldError('email') && (
              <p className="text-sm text-red-600" role="alert">
                {getFieldError('email')}
              </p>
            )}
          </div>

          {/* Password field */}
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              value={formData.password}
              onChange={handleInputChange}
              placeholder="Enter your password"
              aria-invalid={hasFieldError('password')}
              className={hasFieldError('password') ? 'border-red-500' : ''}
              disabled={isSubmitting || isLoading}
            />
            {hasFieldError('password') && (
              <p className="text-sm text-red-600" role="alert">
                {getFieldError('password')}
              </p>
            )}
          </div>
        </CardContent>

        <CardFooter>
          <Button
            type="submit"
            className="w-full"
            disabled={isSubmitting || isLoading}
          >
            {isSubmitting || isLoading ? (
              <div className="flex items-center space-x-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                <span>Signing in...</span>
              </div>
            ) : (
              'Sign In'
            )}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}

export default LoginForm;