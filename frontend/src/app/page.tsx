'use client';

/**
 * Home Page - Entry point for Report Card Assistant
 * 
 * Redirects authenticated users to dashboard, shows login for unauthenticated users.
 * This ensures users always see the new Phase 4.2 dashboard after login.
 */

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';
import { LoginForm } from '@/components/forms/LoginForm';

export default function Home() {
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
          <p className="text-gray-600 mb-4">
            Digital report card management for Singapore primary schools
          </p>
          <p className="text-sm text-gray-500">
            Already have an account? You can also{' '}
            <button 
              onClick={() => router.push('/login')} 
              className="text-blue-600 hover:text-blue-800 font-medium"
            >
              sign in here
            </button>
          </p>
        </div>
        <LoginForm onSuccess={() => router.push('/dashboard')} />
      </div>
    </div>
  );
}

/**
 * Logout Button Component
 * Handles user logout with loading state
 */
function LogoutButton() {
  const { logout } = useAuth();
  const [isLoggingOut, setIsLoggingOut] = React.useState(false);

  const handleLogout = async () => {
    setIsLoggingOut(true);
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoggingOut(false);
    }
  };

  return (
    <button
      onClick={handleLogout}
      disabled={isLoggingOut}
      className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
    >
      {isLoggingOut ? (
        <>
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
          Signing out...
        </>
      ) : (
        'Sign out'
      )}
    </button>
  );
}
