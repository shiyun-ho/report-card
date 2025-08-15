/**
 * Student Filtering and Sorting Utilities with Zod Validation
 * 
 * Provides type-safe filtering and sorting functionality for student data
 * with runtime validation using Zod schemas.
 */

import { StudentSearchParams, StudentSummary, PerformanceBand, StudentSearchSchema } from '@/lib/schemas'

/**
 * Filter and sort students based on validated search parameters
 */
export function filterAndSortStudents(
  students: StudentSummary[],
  params: StudentSearchParams
): StudentSummary[] {
  // Validate search parameters with Zod
  const validatedParams = StudentSearchSchema.parse(params)
  const { query = '', sortBy } = validatedParams

  // Filter students based on search query
  const filtered = students.filter(student =>
    query === '' || 
    student.full_name.toLowerCase().includes(query.toLowerCase()) ||
    student.student_id.toLowerCase().includes(query.toLowerCase())
  )

  // Sort students based on sort criteria
  return filtered.sort((a, b) => {
    switch (sortBy) {
      case 'name':
        return a.full_name.localeCompare(b.full_name)
      case 'performance':
        return getPerformanceOrder(a.performance_band) - getPerformanceOrder(b.performance_band)
      case 'score':
        return b.average_score - a.average_score
      default:
        return 0
    }
  })
}

/**
 * Get numerical order for performance bands (for sorting)
 */
export function getPerformanceOrder(band: PerformanceBand): number {
  const order = {
    'Outstanding': 1,
    'Good': 2, 
    'Satisfactory': 3,
    'Needs Improvement': 4
  }
  return order[band] || 5
}

/**
 * Calculate dashboard statistics from student list
 */
export function calculateDashboardStats(students: StudentSummary[]) {
  const totalStudents = students.length
  
  // Count students in each performance band
  const performanceBands = students.reduce(
    (acc, student) => {
      const band = student.performance_band
      switch (band) {
        case 'Outstanding':
          acc.outstanding += 1
          break
        case 'Good':
          acc.good += 1
          break
        case 'Satisfactory':
          acc.satisfactory += 1
          break
        case 'Needs Improvement':
          acc.needsImprovement += 1
          break
      }
      return acc
    },
    {
      outstanding: 0,
      good: 0,
      satisfactory: 0,
      needsImprovement: 0,
    }
  )

  // Calculate grade completion percentage
  const totalPossibleGrades = totalStudents * 12 // 4 subjects × 3 terms
  const totalActualGrades = students.reduce((sum, student) => sum + student.total_grades, 0)
  const gradeCompletion = totalPossibleGrades > 0 ? Math.round((totalActualGrades / totalPossibleGrades) * 100) : 100

  // Mock recent activity (this would come from API in real implementation)
  const recentActivity = Math.floor(Math.random() * 5) + 1

  return {
    totalStudents,
    performanceBands,
    gradeCompletion,
    recentActivity,
  }
}

/**
 * Format performance band for display
 */
export function formatPerformanceBand(band: PerformanceBand): string {
  return band
}

/**
 * Format average score for display
 */
export function formatAverageScore(score: number): string {
  return score.toFixed(1) + '%'
}

/**
 * Get grade completion status text
 */
export function getGradeCompletionStatus(totalGrades: number, maxGrades: number = 12): string {
  if (totalGrades >= maxGrades) {
    return `${totalGrades}/${maxGrades} grades recorded`
  } else if (totalGrades > 0) {
    return `${totalGrades}/${maxGrades} grades recorded`
  } else {
    return 'No grades recorded'
  }
}

/**
 * Check if student has complete grades
 */
export function hasCompleteGrades(student: StudentSummary): boolean {
  const maxGrades = 12 // 4 subjects × 3 terms
  return student.total_grades >= maxGrades
}

/**
 * Get students by performance band
 */
export function getStudentsByPerformanceBand(
  students: StudentSummary[], 
  band: PerformanceBand
): StudentSummary[] {
  return students.filter(student => student.performance_band === band)
}

/**
 * Search students by query (name or student ID)
 */
export function searchStudents(students: StudentSummary[], query: string): StudentSummary[] {
  if (!query.trim()) {
    return students
  }
  
  const normalizedQuery = query.toLowerCase().trim()
  return students.filter(student =>
    student.full_name.toLowerCase().includes(normalizedQuery) ||
    student.student_id.toLowerCase().includes(normalizedQuery) ||
    student.class_name.toLowerCase().includes(normalizedQuery)
  )
}

/**
 * Paginate student list
 */
export function paginateStudents(
  students: StudentSummary[], 
  page: number, 
  limit: number
): {
  students: StudentSummary[]
  totalPages: number
  currentPage: number
  totalStudents: number
} {
  const totalStudents = students.length
  const totalPages = Math.ceil(totalStudents / limit)
  const currentPage = Math.max(1, Math.min(page, totalPages))
  const startIndex = (currentPage - 1) * limit
  const endIndex = startIndex + limit
  
  return {
    students: students.slice(startIndex, endIndex),
    totalPages,
    currentPage,
    totalStudents,
  }
}