import { ReportForm } from '@/components/reports/ReportForm'

interface ReportGeneratePageProps {
  params: Promise<{ studentId: string }>
  searchParams: Promise<{ termId?: string }>
}

export default async function ReportGeneratePage({ 
  params, 
  searchParams 
}: ReportGeneratePageProps) {
  const resolvedParams = await params
  const resolvedSearchParams = await searchParams
  
  const studentId = parseInt(resolvedParams.studentId)
  const termId = resolvedSearchParams.termId ? parseInt(resolvedSearchParams.termId) : undefined

  // Validate studentId is a valid number
  if (isNaN(studentId)) {
    return (
      <div className="container mx-auto px-4 py-6">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Invalid Student ID</h1>
          <p className="text-gray-600">The student ID provided is not valid.</p>
        </div>
      </div>
    )
  }

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      <ReportForm studentId={studentId} initialTermId={termId} />
    </div>
  )
}