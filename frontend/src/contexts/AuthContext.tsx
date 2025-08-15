'use client';

/**
 * Authentication Context Provider for Report Card Assistant
 * 
 * Manages user authentication state, session persistence, and role-based access
 * for the Teacher Report Card Assistant application.
 */

import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { User, auth, ApiError, AuthError, NetworkError } from '@/lib/api';

// Authentication context interface
interface AuthContextType {
  // State
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  checkAuth: () => Promise<void>;
  clearError: () => void;

  // Role-based helpers
  isFormTeacher: boolean;
  isYearHead: boolean;
  isAdmin: boolean;
  schoolId: number | null;
}

// Create the context
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Provider component props
interface AuthProviderProps {
  children: ReactNode;
}

/**
 * Authentication Context Provider
 * 
 * Provides authentication state and functions to all child components.
 * Handles session persistence, automatic authentication checking, and role-based access.
 */
export function AuthProvider({ children }: AuthProviderProps) {
  // Authentication state
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Derived state
  const isAuthenticated = !!user;
  const isFormTeacher = user?.role === 'form_teacher';
  const isYearHead = user?.role === 'year_head';
  const isAdmin = user?.role === 'admin';
  const schoolId = user?.school_id || null;

  /**
   * Login function
   * Authenticates user with email and password via Docker network backend
   */
  const login = async (email: string, password: string): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Call backend login endpoint via Docker network
      const response = await auth.login({ email, password });
      
      // Set user from login response
      setUser(response.user);
      
      console.log('✅ Login successful:', {
        user: response.user.full_name,
        role: response.user.role,
        school_id: response.user.school_id,
      });
      
    } catch (err) {
      // Handle different types of errors
      let errorMessage = 'Login failed';
      
      if (err instanceof AuthError) {
        errorMessage = err.message;
      } else if (err instanceof ApiError) {
        if (err.status === 422) {
          errorMessage = 'Invalid email or password format';
        } else {
          errorMessage = err.message;
        }
      } else if (err instanceof NetworkError) {
        errorMessage = 'Unable to connect to server. Please check your connection.';
      } else if (err instanceof Error) {
        errorMessage = err.message;
      }
      
      console.error('❌ Login failed:', errorMessage);
      setError(errorMessage);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Logout function
   * Ends session via Docker network backend and clears local state
   */
  const logout = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Call backend logout endpoint via Docker network
      await auth.logout();
      
      // Clear local state
      setUser(null);
      
      console.log('✅ Logout successful');
      
      // Redirect to login page after successful logout
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      
    } catch (err) {
      // Even if logout fails on server side, clear local state
      console.error('⚠️ Logout error (clearing local state anyway):', err);
      setUser(null);
      
      // Still redirect to login page even on error
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Check authentication status
   * Verifies current session with backend via Docker network
   */
  const checkAuth = async (): Promise<void> => {
    setIsLoading(true);
    setError(null);

    try {
      // Check current user session via Docker network
      const currentUser = await auth.getCurrentUser();
      
      setUser(currentUser);
      
      console.log('✅ Auth check successful:', {
        user: currentUser.full_name,
        role: currentUser.role,
      });
      
    } catch (err) {
      // Handle authentication check errors
      if (err instanceof AuthError) {
        // User not authenticated - this is normal, not an error to display
        setUser(null);
      } else if (err instanceof NetworkError) {
        console.error('❌ Network error during auth check:', err.message);
        setError('Unable to verify authentication. Please check your connection.');
      } else {
        console.error('❌ Auth check failed:', err);
        setUser(null);
      }
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Clear error state
   */
  const clearError = (): void => {
    setError(null);
  };

  // Check authentication on provider mount
  useEffect(() => {
    let isMounted = true;

    const initializeAuth = async () => {
      try {
        await checkAuth();
      } catch {
        // Error already handled in checkAuth
      } finally {
        if (isMounted) {
          setIsLoading(false);
        }
      }
    };

    initializeAuth();

    return () => {
      isMounted = false;
    };
  }, []);

  // Provide context value
  const contextValue: AuthContextType = {
    // State
    user,
    isLoading,
    isAuthenticated,
    error,

    // Actions
    login,
    logout,
    checkAuth,
    clearError,

    // Role-based helpers
    isFormTeacher,
    isYearHead,
    isAdmin,
    schoolId,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
}

/**
 * Custom hook to access authentication context
 * 
 * @returns AuthContextType - Authentication context with user state and functions
 * @throws Error if used outside AuthProvider
 */
export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
}

/**
 * Higher-order component for protecting routes
 * Redirects to login if user is not authenticated
 */
export interface RequireAuthProps {
  children: ReactNode;
  fallback?: ReactNode;
}

export function RequireAuth({ children, fallback = null }: RequireAuthProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-2 text-sm text-gray-600">Checking authentication...</p>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
}

/**
 * Component for role-based rendering
 * Only renders children if user has the specified role(s)
 */
export interface RoleGuardProps {
  children: ReactNode;
  roles: Array<'form_teacher' | 'year_head' | 'admin'>;
  fallback?: ReactNode;
}

export function RoleGuard({ children, roles, fallback = null }: RoleGuardProps) {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return null;
  }

  if (!user || !roles.includes(user.role)) {
    return fallback ? <>{fallback}</> : null;
  }

  return <>{children}</>;
}

export default AuthContext;