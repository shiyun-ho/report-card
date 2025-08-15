/**
 * Zod Validation Schemas for Report Card Assistant
 * 
 * TypeScript-first validation schemas that provide runtime type safety
 * and automatic type inference for the dashboard and student data.
 */

import { z } from 'zod'

// Dashboard-specific validation schemas
export const StudentSearchSchema = z.object({
  query: z.string().max(100, 'Search query too long').optional(),
  sortBy: z.enum(['name', 'performance', 'score']).default('name'),
  page: z.number().int().min(1).default(1),
  limit: z.number().int().min(5).max(200).default(20),
})

export const PerformanceBandSchema = z.enum([
  'Outstanding', 
  'Good', 
  'Satisfactory', 
  'Needs Improvement'
])

export const StudentSummarySchema = z.object({
  id: z.number(),
  student_id: z.string(),
  full_name: z.string().min(1).max(100),
  class_name: z.string(),
  performance_band: PerformanceBandSchema,
  average_score: z.number().min(0).max(100),
  total_grades: z.number().int().min(0),
  latest_term: z.string(),
})

// User schema for authentication context
export const UserSchema = z.object({
  id: z.number(),
  email: z.string().email(),
  username: z.string(),
  full_name: z.string(),
  role: z.enum(['form_teacher', 'year_head', 'admin']),
  school_id: z.number(),
  school_name: z.string(),
  created_at: z.string(),
  updated_at: z.string(),
  is_active: z.boolean(),
})

// Dashboard statistics schema
export const DashboardStatsSchema = z.object({
  totalStudents: z.number().int().min(0),
  performanceBands: z.object({
    outstanding: z.number().int().min(0),
    good: z.number().int().min(0),
    satisfactory: z.number().int().min(0),
    needsImprovement: z.number().int().min(0),
  }),
  gradeCompletion: z.number().min(0).max(100),
  recentActivity: z.number().int().min(0),
})

// API Response schemas
export const StudentSummaryListSchema = z.array(StudentSummarySchema)

export const LoginRequestSchema = z.object({
  email: z.string().email('Please enter a valid email address'),
  password: z.string().min(6, 'Password must be at least 6 characters'),
})

export const ApiErrorSchema = z.object({
  detail: z.string(),
  type: z.string().optional(),
  code: z.string().optional(),
})

// Validation functions
export const validateStudentSearch = (data: unknown) => {
  return StudentSearchSchema.safeParse(data)
}

export const validateStudentSummary = (data: unknown) => {
  return StudentSummarySchema.safeParse(data)
}

export const validateStudentSummaryList = (data: unknown) => {
  return StudentSummaryListSchema.safeParse(data)
}

export const validateUser = (data: unknown) => {
  return UserSchema.safeParse(data)
}

export const validateDashboardStats = (data: unknown) => {
  return DashboardStatsSchema.safeParse(data)
}

export const validateLoginRequest = (data: unknown) => {
  return LoginRequestSchema.safeParse(data)
}

// Type inference from schemas - this gives us TypeScript types automatically
export type StudentSearchParams = z.infer<typeof StudentSearchSchema>
export type PerformanceBand = z.infer<typeof PerformanceBandSchema>
export type StudentSummary = z.infer<typeof StudentSummarySchema>
export type User = z.infer<typeof UserSchema>
export type DashboardStats = z.infer<typeof DashboardStatsSchema>
export type LoginRequest = z.infer<typeof LoginRequestSchema>
export type ApiError = z.infer<typeof ApiErrorSchema>

// Helper function to get performance band color
export const getPerformanceBandColor = (band: PerformanceBand): string => {
  switch (band) {
    case 'Outstanding':
      return 'text-green-600 bg-green-50 border-green-200'
    case 'Good':
      return 'text-blue-600 bg-blue-50 border-blue-200'
    case 'Satisfactory':
      return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    case 'Needs Improvement':
      return 'text-red-600 bg-red-50 border-red-200'
    default:
      return 'text-gray-600 bg-gray-50 border-gray-200'
  }
}

// Report form validation schema (keeping established pattern)
export const reportFormSchema = z.object({
  selectedAchievements: z.array(z.object({
    id: z.number().optional(),
    title: z.string(),
    description: z.string(),
    isCustom: z.boolean(),
  })).min(0, ""), // Allow empty achievements array
  behavioralComments: z.string()
    .min(1, "Behavioral comments are required")
    .max(500, "Comments must be under 500 characters"),
})

// Type inference for report form
export type ReportFormData = z.infer<typeof reportFormSchema>

// Helper function to get performance band variant for shadcn/ui Badge
export const getPerformanceBadgeVariant = (band: PerformanceBand): 'default' | 'secondary' | 'destructive' | 'outline' => {
  switch (band) {
    case 'Outstanding':
      return 'default' // green
    case 'Good':
      return 'secondary' // blue
    case 'Satisfactory':
      return 'outline' // yellow
    case 'Needs Improvement':
      return 'destructive' // red
    default:
      return 'outline'
  }
}