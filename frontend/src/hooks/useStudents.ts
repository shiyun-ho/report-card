/**
 * Student Data Hooks with React Query
 * 
 * Custom hooks for fetching and managing student data with caching,
 * automatic background updates, and error handling.
 */

import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'
import { 
  StudentSummary, 
  DashboardStats, 
  validateStudentSummaryList, 
  validateDashboardStats 
} from '@/lib/schemas'
import { calculateDashboardStats } from '@/utils/studentFilters'

/**
 * Hook to fetch student summary data for dashboard
 * Includes role-based filtering (Form Teachers vs Year Heads)
 */
export function useStudentSummary() {
  return useQuery({
    queryKey: ['students', 'summary'],
    queryFn: async (): Promise<StudentSummary[]> => {
      const data = await apiClient.get<unknown[]>('/students/summary/overview')
      
      // Validate API response with Zod
      const validation = validateStudentSummaryList(data)
      if (!validation.success) {
        console.error('Student summary validation failed:', validation.error)
        throw new Error('Invalid student data received from server')
      }
      
      return validation.data
    },
    staleTime: 5 * 60 * 1000, // 5 minutes cache
    gcTime: 10 * 60 * 1000, // 10 minutes garbage collection
    retry: (failureCount, error) => {
      // Don't retry on authentication errors
      if (error instanceof Error && error.message.includes('Authentication required')) {
        return false
      }
      return failureCount < 3
    },
    retryDelay: (attemptIndex) => Math.min(1000 * 2 ** attemptIndex, 30000),
  })
}

/**
 * Hook to fetch detailed student list
 * Alternative to summary for when more detail is needed
 */
export function useStudentList() {
  return useQuery({
    queryKey: ['students', 'list'],
    queryFn: async (): Promise<StudentSummary[]> => {
      const data = await apiClient.get<unknown[]>('/students')
      
      // Transform and validate the data
      const validation = validateStudentSummaryList(data)
      if (!validation.success) {
        console.error('Student list validation failed:', validation.error)
        throw new Error('Invalid student data received from server')
      }
      
      return validation.data
    },
    staleTime: 3 * 60 * 1000, // 3 minutes cache (more detailed data, shorter cache)
    gcTime: 8 * 60 * 1000, // 8 minutes garbage collection
  })
}

/**
 * Hook to calculate and cache dashboard statistics
 * Depends on student summary data
 */
export function useStudentStats() {
  const { data: students, isLoading: studentsLoading, error: studentsError } = useStudentSummary()

  return useQuery({
    queryKey: ['dashboard', 'stats', students?.length],
    queryFn: (): DashboardStats => {
      if (!students || students.length === 0) {
        return {
          totalStudents: 0,
          performanceBands: {
            outstanding: 0,
            good: 0,
            satisfactory: 0,
            needsImprovement: 0,
          },
          gradeCompletion: 0,
          recentActivity: 0,
        }
      }

      const stats = calculateDashboardStats(students)
      
      // Validate calculated stats
      const validation = validateDashboardStats(stats)
      if (!validation.success) {
        console.error('Dashboard stats validation failed:', validation.error)
        throw new Error('Failed to calculate dashboard statistics')
      }
      
      return validation.data
    },
    enabled: !!students && !studentsLoading, // Only run when students data is available
    staleTime: 5 * 60 * 1000, // 5 minutes cache
    gcTime: 10 * 60 * 1000, // 10 minutes garbage collection
  })
}

/**
 * Hook to fetch individual student details
 */
export function useStudent(studentId: number | null) {
  return useQuery({
    queryKey: ['students', 'detail', studentId],
    queryFn: async (): Promise<StudentSummary> => {
      if (!studentId) {
        throw new Error('Student ID is required')
      }
      
      const data = await apiClient.get<unknown>(`/students/${studentId}`)
      
      // Validate single student data
      const validation = validateStudentSummaryList([data])
      if (!validation.success || validation.data.length === 0) {
        console.error('Student detail validation failed:', validation.error)
        throw new Error('Invalid student data received from server')
      }
      
      return validation.data[0]
    },
    enabled: !!studentId, // Only run when studentId is provided
    staleTime: 2 * 60 * 1000, // 2 minutes cache
    gcTime: 5 * 60 * 1000, // 5 minutes garbage collection
  })
}

/**
 * Hook to prefetch student data for better performance
 * Useful when we know user might navigate to student details
 */
export function usePrefetchStudent() {
  const queryClient = useQueryClient()
  
  return (studentId: number) => {
    queryClient.prefetchQuery({
      queryKey: ['students', 'detail', studentId],
      queryFn: async (): Promise<StudentSummary> => {
        const data = await apiClient.get<unknown>(`/students/${studentId}`)
        const validation = validateStudentSummaryList([data])
        if (!validation.success || validation.data.length === 0) {
          throw new Error('Invalid student data received from server')
        }
        return validation.data[0]
      },
      staleTime: 2 * 60 * 1000,
    })
  }
}

// Add missing import
import { useQueryClient } from '@tanstack/react-query'

/**
 * Hook for invalidating student-related queries
 * Useful after mutations that affect student data
 */
export function useInvalidateStudentQueries() {
  const queryClient = useQueryClient()
  
  return {
    invalidateAll: () => {
      queryClient.invalidateQueries({ queryKey: ['students'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard'] })
    },
    invalidateSummary: () => {
      queryClient.invalidateQueries({ queryKey: ['students', 'summary'] })
      queryClient.invalidateQueries({ queryKey: ['dashboard', 'stats'] })
    },
    invalidateStudent: (studentId: number) => {
      queryClient.invalidateQueries({ queryKey: ['students', 'detail', studentId] })
    },
  }
}