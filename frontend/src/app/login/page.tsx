'use client';

/**
 * Login Page - Teacher Report Card Assistant
 * 
 * Dedicated login page for users to authenticate.
 * Redirects to dashboard on successful authentication.
 */

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { LoginForm } from '@/components/forms/LoginForm';

export default function LoginPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading } = useAuth();

  // Redirect authenticated users to dashboard
  useEffect(() => {
    if (!isLoading && isAuthenticated) {
      router.push('/dashboard');
    }
  }, [isAuthenticated, isLoading, router]);

  // Show loading state during authentication check or redirect
  if (isLoading || isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">
            {isAuthenticated ? 'Redirecting to dashboard...' : 'Loading...'}
          </p>
        </div>
      </div>
    );
  }

  // Show login form for unauthenticated users
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Teacher Report Card Assistant
          </h1>
          <p className="text-gray-600">
            Please sign in to access your dashboard
          </p>
        </div>
        <LoginForm onSuccess={() => router.push('/dashboard')} />
      </div>
    </div>
  );
}