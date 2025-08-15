'use client'

import Link from 'next/link'
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api'

interface StudentHeaderProps {
  studentId: number
  selectedTermId?: number
  onTermChange: (termId: number) => void
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

interface Term {
  id: number
  name: string
  term_number: number
  academic_year: number
}

export function StudentHeader({ 
  studentId, 
  selectedTermId, 
  onTermChange 
}: StudentHeaderProps) {
  // Fetch student details
  const { data: student, isLoading: studentLoading, error: studentError } = useQuery<Student>({
    queryKey: ['student', studentId],
    queryFn: () => apiClient.get(`/students/${studentId}`)
  })

  // Fetch terms (should be filtered to user's school automatically by RBAC)
  const { data: terms, isLoading: termsLoading } = useQuery<Term[]>({
    queryKey: ['terms'],
    queryFn: () => apiClient.get('/terms')
  })

  if (studentLoading) {
    return (
      <Card>
        <CardHeader>
          <div className="animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
            <div className="h-6 bg-gray-200 rounded w-1/2 mb-2"></div>
            <div className="h-4 bg-gray-200 rounded w-2/3"></div>
          </div>
        </CardHeader>
      </Card>
    )
  }

  if (studentError || !student) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-red-600">Error Loading Student</CardTitle>
          <CardDescription>
            Unable to load student information. You may not have permission to access this student.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex items-center justify-between">
          <div>
            <nav className="mb-2">
              <Link 
                href="/dashboard" 
                className="text-sm text-blue-600 hover:text-blue-800 underline"
              >
                ← Back to Dashboard
              </Link>
            </nav>
            <CardTitle className="text-xl">
              {student.full_name} ({student.student_id})
            </CardTitle>
            <CardDescription className="text-base">
              {student.class_obj.name} • {student.school.name}
            </CardDescription>
          </div>
          <div className="text-right">
            <label htmlFor="term-select" className="text-sm font-medium text-gray-700 block mb-1">
              Select Term
            </label>
            <Select 
              value={selectedTermId?.toString()} 
              onValueChange={(value) => onTermChange(parseInt(value))}
              disabled={termsLoading}
            >
              <SelectTrigger className="w-40" id="term-select">
                <SelectValue placeholder="Select term" />
              </SelectTrigger>
              <SelectContent>
                {terms?.map((term) => (
                  <SelectItem key={term.id} value={term.id.toString()}>
                    {term.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </CardHeader>
    </Card>
  )
}