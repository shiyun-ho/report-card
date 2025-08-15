/**
 * Student Table Component
 * 
 * Interactive table displaying student data with search, sort, and filter functionality.
 * Includes performance indicators and quick actions for each student.
 */

'use client';

import { useState, useMemo } from 'react';
import { useStudentSummary } from '@/hooks/useStudents';
import { StudentSummary, StudentSearchParams } from '@/lib/schemas';
import { filterAndSortStudents, getGradeCompletionStatus } from '@/utils/studentFilters';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Skeleton } from '@/components/ui/skeleton';
import { PerformanceBadge } from './PerformanceBadge';
import { StudentActions } from './StudentActions';
import { 
  Search, 
  SortAsc, 
  SortDesc, 
  Users, 
  AlertCircle,
  FileText,
  Calendar
} from 'lucide-react';

/**
 * Table Loading Skeleton
 */
function StudentTableSkeleton() {
  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <Skeleton className="h-6 w-48" />
          <div className="flex gap-2">
            <Skeleton className="h-10 w-64" />
            <Skeleton className="h-10 w-32" />
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {Array.from({ length: 5 }).map((_, i) => (
            <div key={i} className="flex justify-between items-center p-4 border rounded-lg">
              <div className="space-y-2">
                <Skeleton className="h-4 w-32" />
                <Skeleton className="h-3 w-24" />
                <Skeleton className="h-3 w-20" />
              </div>
              <div className="flex items-center gap-4">
                <Skeleton className="h-6 w-24" />
                <Skeleton className="h-4 w-16" />
                <div className="flex gap-2">
                  <Skeleton className="h-8 w-20" />
                  <Skeleton className="h-8 w-20" />
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Empty State Component
 */
interface EmptyStateProps {
  message: string;
  icon?: React.ReactNode;
}

function EmptyState({ message, icon }: EmptyStateProps) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-12 text-center">
        <div className="mb-4 text-gray-400">
          {icon || <Users className="h-12 w-12" />}
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Students Found</h3>
        <p className="text-gray-600 max-w-sm">{message}</p>
      </CardContent>
    </Card>
  );
}

/**
 * Error State Component
 */
interface ErrorStateProps {
  message: string;
  onRetry?: () => void;
}

function ErrorState({ message, onRetry }: ErrorStateProps) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-12 text-center">
        <AlertCircle className="h-12 w-12 text-red-500 mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to Load Students</h3>
        <p className="text-gray-600 mb-4 max-w-sm">{message}</p>
        {onRetry && (
          <Button onClick={onRetry} variant="outline">
            Try Again
          </Button>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Sort Select Component
 */
interface SortSelectProps {
  value: StudentSearchParams['sortBy'];
  onChange: (value: StudentSearchParams['sortBy']) => void;
}

function SortSelect({ value, onChange }: SortSelectProps) {
  return (
    <Select value={value} onValueChange={onChange}>
      <SelectTrigger className="w-48">
        <div className="flex items-center gap-2">
          {value === 'name' && <SortAsc className="h-4 w-4" />}
          {value === 'performance' && <SortDesc className="h-4 w-4" />}
          {value === 'score' && <SortDesc className="h-4 w-4" />}
          <SelectValue placeholder="Sort by..." />
        </div>
      </SelectTrigger>
      <SelectContent>
        <SelectItem value="name">Name (A-Z)</SelectItem>
        <SelectItem value="performance">Performance Band</SelectItem>
        <SelectItem value="score">Average Score</SelectItem>
      </SelectContent>
    </Select>
  );
}

/**
 * Student Table Row Component
 */
interface StudentRowProps {
  student: StudentSummary;
  index: number;
}

function StudentRow({ student, index }: StudentRowProps) {
  const completionStatus = getGradeCompletionStatus(student.total_grades);
  const isComplete = student.total_grades >= 12;

  return (
    <TableRow className="hover:bg-gray-50 transition-colors">
      <TableCell className="font-medium">
        <div className="space-y-1">
          <div className="font-semibold text-gray-900">{student.full_name}</div>
          <div className="text-sm text-gray-600">{student.student_id}</div>
          <div className="text-sm text-gray-500">{student.class_name}</div>
        </div>
      </TableCell>

      <TableCell>
        <PerformanceBadge 
          band={student.performance_band}
          score={student.average_score}
          showIcon={true}
          showScore={true}
        />
      </TableCell>

      <TableCell>
        <div className="space-y-1">
          <div className="flex items-center gap-2">
            <Badge variant={isComplete ? 'default' : 'secondary'}>
              {completionStatus}
            </Badge>
          </div>
          <div className="text-sm text-gray-500 flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {student.latest_term}
          </div>
        </div>
      </TableCell>

      <TableCell>
        <div className="text-right">
          <div className="font-bold text-lg">{student.average_score.toFixed(1)}%</div>
          <div className="text-sm text-gray-500">{student.total_grades} grades</div>
        </div>
      </TableCell>

      <TableCell>
        <StudentActions student={student} />
      </TableCell>
    </TableRow>
  );
}

/**
 * Main Student Table Component
 */
export function StudentTable() {
  const { 
    data: students, 
    isLoading, 
    error, 
    refetch 
  } = useStudentSummary();

  // Search and sort state
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<StudentSearchParams['sortBy']>('name');

  // Filter and sort students based on current parameters
  const filteredAndSortedStudents = useMemo(() => {
    if (!students) return [];

    const searchParams: StudentSearchParams = {
      query: searchQuery,
      sortBy,
      page: 1,
      limit: 100, // Show all for now, pagination can be added later
    };

    return filterAndSortStudents(students, searchParams);
  }, [students, searchQuery, sortBy]);

  // Handle loading state
  if (isLoading) {
    return <StudentTableSkeleton />;
  }

  // Handle error state
  if (error) {
    const errorMessage = error instanceof Error 
      ? error.message 
      : 'Failed to load student data';

    return <ErrorState message={errorMessage} onRetry={() => refetch()} />;
  }

  // Handle empty state
  if (!students || students.length === 0) {
    return (
      <EmptyState 
        message="No students have been assigned to you. Contact your administrator if this seems incorrect."
        icon={<Users className="h-12 w-12" />}
      />
    );
  }

  // Handle no search results
  if (searchQuery && filteredAndSortedStudents.length === 0) {
    return (
      <EmptyState 
        message={`No students found matching "${searchQuery}". Try adjusting your search terms.`}
        icon={<Search className="h-12 w-12" />}
      />
    );
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            Students Overview
            <Badge variant="secondary">
              {filteredAndSortedStudents.length} of {students.length}
            </Badge>
          </CardTitle>
          
          <div className="flex flex-col sm:flex-row gap-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
              <Input 
                placeholder="Search students or ID..." 
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-10 w-full sm:w-64"
              />
            </div>
            <SortSelect value={sortBy} onChange={setSortBy} />
          </div>
        </div>
      </CardHeader>

      <CardContent>
        <div className="rounded-md border">
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="font-semibold">Student</TableHead>
                <TableHead className="font-semibold">Performance</TableHead>
                <TableHead className="font-semibold">Grade Status</TableHead>
                <TableHead className="font-semibold text-right">Average</TableHead>
                <TableHead className="font-semibold text-center">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredAndSortedStudents.map((student, index) => (
                <StudentRow 
                  key={student.id} 
                  student={student} 
                  index={index}
                />
              ))}
            </TableBody>
          </Table>
        </div>

        {/* Summary footer */}
        <div className="mt-4 flex items-center justify-between text-sm text-gray-600 border-t pt-4">
          <div className="flex items-center gap-4">
            <span>Showing {filteredAndSortedStudents.length} students</span>
            {searchQuery && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => setSearchQuery('')}
                className="text-blue-600 hover:text-blue-800"
              >
                Clear search
              </Button>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            <span>Last updated: {new Date().toLocaleTimeString()}</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}

export default StudentTable;