'use client';

/**
 * Dashboard Page - Teacher Report Card Assistant
 * 
 * Main interface showing all students with role-based overview.
 * Provides comprehensive student management for Form Teachers and Year Heads.
 */

import { useAuth } from '@/contexts/AuthContext';
import { useStudentSummary, useStudentStats } from '@/hooks/useStudents';
import { DashboardHeader } from '@/components/dashboard/DashboardHeader';
import { DashboardStats } from '@/components/dashboard/DashboardStats';
import { StudentTable } from '@/components/dashboard/StudentTable';
import { Card, CardContent } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

/**
 * Dashboard Loading Skeleton
 * Displayed while authentication and student data are loading
 */
function DashboardSkeleton() {
  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Header skeleton */}
      <div className="flex justify-between items-center">
        <div className="space-y-2">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-4 w-64" />
        </div>
        <div className="space-y-2">
          <Skeleton className="h-4 w-24" />
          <Skeleton className="h-6 w-32" />
          <Skeleton className="h-6 w-20" />
        </div>
      </div>

      {/* Stats skeleton */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-4 w-24 mb-2" />
              <Skeleton className="h-8 w-16" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Table skeleton */}
      <Card>
        <CardContent className="p-6">
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <Skeleton className="h-6 w-32" />
              <div className="flex gap-2">
                <Skeleton className="h-10 w-64" />
                <Skeleton className="h-10 w-32" />
              </div>
            </div>
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="flex justify-between items-center p-3 border rounded">
                  <div className="space-y-2">
                    <Skeleton className="h-4 w-32" />
                    <Skeleton className="h-3 w-24" />
                  </div>
                  <div className="flex items-center gap-2">
                    <Skeleton className="h-6 w-20" />
                    <Skeleton className="h-4 w-12" />
                  </div>
                </div>
              ))}
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Error State Component
 * Displayed when there's an authentication or data loading error
 */
interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <div className="container mx-auto px-4 py-6">
      <Card>
        <CardContent className="p-6 text-center space-y-4">
          <div className="text-red-600">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 9v3.75m9-.75a9 9 0 11-18 0 9 9 0 0118 0zm-9 3.75h.008v.008H12v-.008z" />
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-gray-900">Unable to Load Dashboard</h2>
            <p className="text-gray-600 mt-2">{message}</p>
          </div>
          {onRetry && (
            <button 
              onClick={onRetry}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * Main Dashboard Page Component
 * 
 * Provides role-based student overview with:
 * - User header with role information
 * - Summary statistics
 * - Searchable/sortable student table
 * - Performance indicators
 */
export default function DashboardPage() {
  const { user, isLoading: authLoading, isAuthenticated } = useAuth();
  const { 
    data: students, 
    isLoading: studentsLoading, 
    error: studentsError,
    refetch: refetchStudents 
  } = useStudentSummary();
  
  const { 
    data: stats, 
    isLoading: statsLoading 
  } = useStudentStats();

  // Show loading state while authenticating or initial data load
  const isLoading = authLoading || (studentsLoading && !students);

  // Handle authentication redirect
  if (!authLoading && !isAuthenticated) {
    // This should be handled by route protection, but just in case
    if (typeof window !== 'undefined') {
      window.location.href = '/login';
    }
    return null;
  }

  // Handle errors
  if (studentsError) {
    const errorMessage = studentsError instanceof Error 
      ? studentsError.message 
      : 'Failed to load student data';

    return (
      <ErrorState 
        message={errorMessage}
        onRetry={() => refetchStudents()}
      />
    );
  }

  // Show loading skeleton
  if (isLoading || !user || !students) {
    return <DashboardSkeleton />;
  }

  // Render dashboard with data
  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      <DashboardHeader 
        user={user} 
        studentCount={students.length} 
      />
      
      {stats && !statsLoading && (
        <DashboardStats 
          stats={stats} 
        />
      )}
      
      <StudentTable />
    </div>
  );
}