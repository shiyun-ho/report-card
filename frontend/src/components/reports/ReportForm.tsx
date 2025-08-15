'use client'

import { useState, useEffect, useCallback } from 'react'
import { useRouter } from 'next/navigation'
import { useQuery } from '@tanstack/react-query'
import { StudentHeader } from './StudentHeader'
import { GradeReview } from './GradeReview'
import { AchievementSelection } from './AchievementSelection'
import { BehavioralComments } from './BehavioralComments'
import { Button } from '@/components/ui/button'
import { apiClient, api } from '@/lib/api'
import { reportFormSchema } from '@/lib/schemas'
import { z } from 'zod'

interface ReportFormProps {
  studentId: number
  initialTermId?: number
}

interface ReportFormData {
  selectedAchievements: SelectedAchievement[]
  behavioralComments: string
}

interface SelectedAchievement {
  id?: number // undefined for custom achievements
  title: string
  description: string
  isCustom: boolean
}

interface Term {
  id: number
  name: string
  term_number: number
  academic_year: number
}

interface Student {
  id: number
  student_id: string
  first_name: string
  last_name: string
  full_name: string
  class_obj: {
    name: string
  }
  school: {
    name: string
  }
}

export function ReportForm({ studentId, initialTermId }: ReportFormProps) {
  const router = useRouter()
  
  // Fetch student details
  const { data: student, isLoading: studentLoading } = useQuery<Student>({
    queryKey: ['student', studentId],
    queryFn: () => apiClient.get(`/students/${studentId}`)
  })
  
  // Fetch terms for this student's school
  const { data: terms, isLoading: termsLoading } = useQuery<Term[]>({
    queryKey: ['terms'],
    queryFn: () => apiClient.get('/terms')
  })

  // Set initial term (use latest term if none specified)
  const [selectedTermId, setSelectedTermId] = useState<number | undefined>(
    initialTermId || undefined
  )

  // Set selectedTermId to latest term when terms load
  useEffect(() => {
    if (!selectedTermId && terms?.length) {
      const latestTerm = terms.reduce((latest, term) => 
        term.term_number > latest.term_number ? term : latest
      )
      setSelectedTermId(latestTerm.id)
    }
  }, [terms, selectedTermId])
  
  // Simple React state for form data (no React Hook Form complexity)
  const [formData, setFormData] = useState<ReportFormData>({
    selectedAchievements: [],
    behavioralComments: ''
  })
  const [validationErrors, setValidationErrors] = useState<Record<string, string>>({})

  // Validate form data using Zod (keeping established pattern)
  const validateForm = (data: ReportFormData) => {
    const result = reportFormSchema.safeParse(data)
    if (!result.success) {
      const errors: Record<string, string> = {}
      result.error.issues.forEach(issue => {
        errors[issue.path.join('.')] = issue.message
      })
      setValidationErrors(errors)
      return false
    }
    setValidationErrors({})
    return true
  }

  const handleAchievementsChange = useCallback((achievements: SelectedAchievement[]) => {
    // Store all selected achievements (both suggestions and custom)
    const updatedData = { ...formData, selectedAchievements: achievements }
    setFormData(updatedData)
    
    // Clear achievement validation errors - achievements are now optional
    setValidationErrors(prev => ({ ...prev, selectedAchievements: '' }))
  }, [formData])

  const handleCommentsChange = useCallback((comments: string) => {
    const updatedData = { ...formData, behavioralComments: comments }
    setFormData(updatedData)
    
    // Real-time validation for comments
    const result = reportFormSchema.shape.behavioralComments.safeParse(comments)
    if (!result.success) {
      setValidationErrors(prev => ({ 
        ...prev, 
        behavioralComments: result.error.issues[0].message 
      }))
    } else {
      setValidationErrors(prev => ({ ...prev, behavioralComments: '' }))
    }
  }, [formData])

  const handleGenerateReport = async () => {
    if (!validateForm(formData)) {
      // Show error toast or notification
      console.error('Form validation failed')
      return
    }

    try {
      // Generate PDF report using the API client
      const { blob, filename } = await api.downloadBlob(`/reports/generate/${studentId}/${selectedTermId}`, {
        selected_achievements: formData.selectedAchievements.map(achievement => ({
          title: achievement.title,
          description: achievement.description,
          category_name: achievement.isCustom ? 'Custom' : 'Academic'
        })),
        behavioral_comments: formData.behavioralComments
      })
      
      // Generate proper filename: StudentName_Class_TermNumber_Year.pdf
      let defaultFilename = `Student_${studentId}_Term_${selectedTermId}_Report.pdf`
      
      if (student && terms) {
        const selectedTerm = terms.find(term => term.id === selectedTermId)
        if (selectedTerm) {
          // Clean student name (remove spaces, special characters)
          const cleanStudentName = student.full_name.replace(/[^a-zA-Z0-9]/g, '_')
          const cleanClassName = student.class_obj.name.replace(/[^a-zA-Z0-9]/g, '_')
          
          defaultFilename = `${cleanStudentName}_${cleanClassName}_Term${selectedTerm.term_number}_${selectedTerm.academic_year}.pdf`
        }
      }
      
      // Create download link
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = filename || defaultFilename
      
      document.body.appendChild(link)
      link.click()
      
      // Cleanup
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
      
      alert('PDF report generated successfully!')
      
    } catch (error) {
      console.error('Error generating PDF:', error)
      alert('Failed to generate PDF report. Please try again.')
    }
  }

  if (studentLoading || termsLoading || !selectedTermId) {
    return (
      <div className="space-y-6">
        <div className="animate-pulse">
          <div className="h-32 bg-gray-200 rounded mb-6"></div>
          <div className="h-48 bg-gray-200 rounded mb-6"></div>
          <div className="h-64 bg-gray-200 rounded mb-6"></div>
          <div className="h-32 bg-gray-200 rounded"></div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Student Header */}
      <StudentHeader 
        studentId={studentId}
        selectedTermId={selectedTermId}
        onTermChange={setSelectedTermId}
      />

      {/* Grade Review (Read-Only) */}
      <GradeReview
        studentId={studentId}
        termId={selectedTermId}
      />

      {/* Achievement Selection */}
      <AchievementSelection
        studentId={studentId}
        termId={selectedTermId}
        onSelectionChange={handleAchievementsChange}
      />
      {validationErrors.selectedAchievements && (
        <p className="text-sm text-red-600 -mt-4 ml-4">
          {validationErrors.selectedAchievements}
        </p>
      )}

      {/* Behavioral Comments */}
      <BehavioralComments
        value={formData.behavioralComments}
        onChange={handleCommentsChange}
        maxLength={500}
      />
      {validationErrors.behavioralComments && (
        <p className="text-sm text-red-600 -mt-4 ml-4">
          {validationErrors.behavioralComments}
        </p>
      )}

      {/* Action Buttons */}
      <div className="flex justify-end pt-6 border-t">
        <div className="flex space-x-3">
          <Button 
            variant="outline"
            onClick={() => router.push('/dashboard')}
          >
            Cancel
          </Button>
          <Button 
            onClick={handleGenerateReport}
            className="bg-blue-600 hover:bg-blue-700 text-white"
            disabled={Object.values(validationErrors).some(error => !!error)}
          >
            Generate Report
          </Button>
        </div>
      </div>
    </div>
  )
}