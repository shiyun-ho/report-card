'use client'

import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { apiClient } from '@/lib/api'

interface GradeReviewProps {
  studentId: number
  termId: number
}

interface GradeResponse {
  id: number
  score: string
  subject: {
    id: number
    name: string
    code: string
  }
  term: {
    id: number
    name: string
    term_number: number
    academic_year: number
  }
}

interface StudentTermGradesResponse {
  student_id: number
  term_id: number
  grades: GradeResponse[]
  average_score: number
  performance_band: string
  total_subjects: number
}

export function GradeReview({ studentId, termId }: GradeReviewProps) {
  const { data: currentGrades, isLoading: currentLoading, error: currentError } = useQuery<StudentTermGradesResponse>({
    queryKey: ['grades', studentId, termId],
    queryFn: () => apiClient.get(`/grades/students/${studentId}/terms/${termId}`)
  })

  const { data: previousGrades, isLoading: previousLoading } = useQuery<StudentTermGradesResponse>({
    queryKey: ['grades', studentId, termId - 1],
    queryFn: () => apiClient.get(`/grades/students/${studentId}/terms/${termId - 1}`),
    enabled: termId > 1 // Only fetch if there's a previous term
  })
  
  const getPerformanceBand = (average: number) => {
    if (average >= 85) return { label: "Outstanding", color: "bg-green-100 text-green-800" }
    if (average >= 70) return { label: "Good", color: "bg-blue-100 text-blue-800" }
    if (average >= 55) return { label: "Satisfactory", color: "bg-yellow-100 text-yellow-800" }
    return { label: "Needs Improvement", color: "bg-red-100 text-red-800" }
  }

  if (currentLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Grade Review</CardTitle>
          <CardDescription>Loading grades...</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardContent>
      </Card>
    )
  }

  if (currentError || !currentGrades) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-red-600">Error Loading Grades</CardTitle>
          <CardDescription>
            Unable to load grades for this student and term. You may not have permission to access this data.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const currentAverage = currentGrades.average_score
  const previousAverage = previousGrades?.average_score || 0
  const performanceBand = getPerformanceBand(currentAverage)

  return (
    <Card>
      <CardHeader>
        <CardTitle>Grade Review</CardTitle>
        <CardDescription>
          Review recorded grades for Term {termId}. Grades are already recorded in the system.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Current Term Grades (Read-Only Display) */}
          <div>
            <h3 className="font-semibold mb-4">Current Term Grades</h3>
            <div className="space-y-3">
              {currentGrades.grades?.map((grade) => {
                const prevGrade = previousGrades?.grades?.find(g => g.subject.id === grade.subject.id)
                const improvement = prevGrade ? 
                  parseFloat(grade.score) - parseFloat(prevGrade.score) : null

                return (
                  <div key={grade.id} className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                      <span className="font-medium">{grade.subject.name}</span>
                      <div className="text-sm text-gray-500">{grade.subject.code}</div>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold">
                        {parseFloat(grade.score).toFixed(1)}
                        <span className="text-sm text-gray-500 ml-1">/ 100</span>
                      </div>
                      {improvement !== null && (
                        <div className={`text-xs flex items-center justify-end mt-1 ${
                          improvement > 0 ? 'text-green-600' : 
                          improvement < 0 ? 'text-red-600' : 'text-gray-500'
                        }`}>
                          {improvement > 0 && '↗ +'}
                          {improvement < 0 && '↘ '}
                          {improvement === 0 && '→ '}
                          {Math.abs(improvement).toFixed(1)} from last term
                        </div>
                      )}
                    </div>
                  </div>
                )
              })}
            </div>

            {/* Current Performance Summary */}
            <div className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex justify-between items-center mb-2">
                <span className="font-medium">Term Average:</span>
                <span className="text-xl font-bold text-blue-700">
                  {currentAverage.toFixed(1)}%
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span>Performance Band:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${performanceBand.color}`}>
                  {performanceBand.label}
                </span>
              </div>
              {previousAverage > 0 && (
                <div className="mt-2 pt-2 border-t border-blue-200">
                  <div className={`text-sm ${
                    currentAverage > previousAverage ? 'text-green-600' : 
                    currentAverage < previousAverage ? 'text-red-600' : 'text-gray-600'
                  }`}>
                    {currentAverage > previousAverage ? '↗' : currentAverage < previousAverage ? '↘' : '→'} 
                    {currentAverage > previousAverage ? '+' : ''}
                    {(currentAverage - previousAverage).toFixed(1)} from previous term
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Previous Term Comparison */}
          <div>
            <h3 className="font-semibold mb-4">Previous Term (Reference)</h3>
            {previousGrades?.grades?.length ? (
              <div className="space-y-3">
                {previousGrades.grades.map((grade) => (
                  <div key={grade.id} className="flex justify-between items-center p-3 bg-gray-100 rounded-lg">
                    <span className="font-medium">{grade.subject.name}</span>
                    <div className="text-right">
                      <span className="text-lg font-semibold text-gray-700">
                        {parseFloat(grade.score).toFixed(1)}
                      </span>
                      <span className="text-sm text-gray-500 ml-1">/ 100</span>
                    </div>
                  </div>
                ))}
                <div className="mt-4 p-3 bg-gray-200 rounded-lg">
                  <div className="flex justify-between items-center">
                    <span className="text-sm font-medium text-gray-700">Previous Average:</span>
                    <span className="text-lg font-bold text-gray-700">
                      {previousAverage.toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-8 text-gray-500">
                <div className="text-sm">No previous term data available</div>
                <div className="text-xs mt-1">This might be the student&apos;s first term</div>
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}