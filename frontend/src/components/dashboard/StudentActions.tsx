/**
 * Student Actions Component
 * 
 * Quick action buttons for each student row in the dashboard table.
 * Provides navigation to report generation and student detail views.
 */

'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { StudentSummary } from '@/lib/schemas';
import { Button } from '@/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { 
  FileText, 
  Eye, 
  MoreHorizontal, 
  TrendingUp, 
  Calendar,
  User,
  ExternalLink
} from 'lucide-react';

interface StudentActionsProps {
  student: StudentSummary;
  variant?: 'buttons' | 'dropdown' | 'compact';
}

/**
 * Button Actions Variant - Shows individual action buttons
 */
function ButtonActions({ student }: { student: StudentSummary }) {
  const router = useRouter();
  const [isNavigating, setIsNavigating] = useState(false);

  const handleGenerateReport = async () => {
    setIsNavigating(true);
    try {
      // Navigate to report generation page
      router.push(`/reports/generate/${student.id}`);
    } catch (error) {
      console.error('Navigation failed:', error);
      setIsNavigating(false);
    }
  };

  const handleViewDetails = async () => {
    setIsNavigating(true);
    try {
      // Navigate to student details page
      router.push(`/students/${student.id}`);
    } catch (error) {
      console.error('Navigation failed:', error);
      setIsNavigating(false);
    }
  };

  return (
    <div className="flex gap-2">
      <Button 
        size="sm" 
        onClick={handleGenerateReport}
        disabled={isNavigating}
        className="flex items-center gap-1"
      >
        <FileText className="h-3 w-3" />
        Generate Report
      </Button>
      <Button 
        size="sm" 
        variant="outline" 
        onClick={handleViewDetails}
        disabled={isNavigating}
        className="flex items-center gap-1"
      >
        <Eye className="h-3 w-3" />
        View Details
      </Button>
    </div>
  );
}

/**
 * Dropdown Actions Variant - More compact with dropdown menu
 */
function DropdownActions({ student }: { student: StudentSummary }) {
  const router = useRouter();
  const [isNavigating, setIsNavigating] = useState(false);

  const handleAction = async (action: string) => {
    setIsNavigating(true);
    try {
      switch (action) {
        case 'generate-report':
          router.push(`/reports/generate/${student.id}`);
          break;
        case 'view-details':
          router.push(`/students/${student.id}`);
          break;
        case 'view-grades':
          router.push(`/students/${student.id}/grades`);
          break;
        case 'view-progress':
          router.push(`/students/${student.id}/progress`);
          break;
        default:
          console.warn('Unknown action:', action);
          setIsNavigating(false);
      }
    } catch (error) {
      console.error('Navigation failed:', error);
      setIsNavigating(false);
    }
  };

  const hasCompleteGrades = student.total_grades >= 12;
  const canGenerateReport = hasCompleteGrades;

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button 
          variant="ghost" 
          className="h-8 w-8 p-0"
          disabled={isNavigating}
        >
          <span className="sr-only">Open menu</span>
          <MoreHorizontal className="h-4 w-4" />
        </Button>
      </DropdownMenuTrigger>
      
      <DropdownMenuContent align="end" className="w-48">
        <DropdownMenuLabel className="font-normal">
          <div className="flex flex-col space-y-1">
            <p className="text-sm font-medium leading-none">
              {student.full_name}
            </p>
            <p className="text-xs leading-none text-muted-foreground">
              {student.student_id}
            </p>
          </div>
        </DropdownMenuLabel>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem 
          onClick={() => handleAction('generate-report')}
          disabled={!canGenerateReport}
          className="flex items-center gap-2"
        >
          <FileText className="h-4 w-4" />
          Generate Report
          {!canGenerateReport && (
            <span className="text-xs text-gray-500">(Incomplete grades)</span>
          )}
        </DropdownMenuItem>
        
        <DropdownMenuItem 
          onClick={() => handleAction('view-details')}
          className="flex items-center gap-2"
        >
          <User className="h-4 w-4" />
          Student Profile
        </DropdownMenuItem>
        
        <DropdownMenuItem 
          onClick={() => handleAction('view-grades')}
          className="flex items-center gap-2"
        >
          <Calendar className="h-4 w-4" />
          Grade History
        </DropdownMenuItem>
        
        <DropdownMenuItem 
          onClick={() => handleAction('view-progress')}
          className="flex items-center gap-2"
        >
          <TrendingUp className="h-4 w-4" />
          Progress Tracking
        </DropdownMenuItem>
        
        <DropdownMenuSeparator />
        
        <DropdownMenuItem 
          onClick={() => handleAction('view-details')}
          className="flex items-center gap-2 text-blue-600"
        >
          <ExternalLink className="h-4 w-4" />
          Open Full View
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  );
}

/**
 * Compact Actions Variant - Minimal space usage with centered icon only
 */
function CompactActions({ student }: { student: StudentSummary }) {
  const router = useRouter();
  const [isNavigating, setIsNavigating] = useState(false);

  const handleGenerateReport = async () => {
    setIsNavigating(true);
    try {
      router.push(`/reports/generate/${student.id}`);
    } catch (error) {
      console.error('Navigation failed:', error);
      setIsNavigating(false);
    }
  };

  const hasCompleteGrades = student.total_grades >= 12;

  return (
    <div className="flex justify-center">
      <Button 
        size="sm" 
        onClick={handleGenerateReport}
        disabled={!hasCompleteGrades || isNavigating}
        className="h-8 w-8 p-0"
        title={hasCompleteGrades ? 'Generate Report' : 'Complete all grades first'}
      >
        <FileText className="h-4 w-4" />
      </Button>
    </div>
  );
}

/**
 * Main Student Actions Component
 * 
 * Renders different action variants based on the specified variant prop.
 * Handles navigation to report generation and student detail pages.
 */
export function StudentActions({ student, variant = 'compact' }: StudentActionsProps) {
  switch (variant) {
    case 'buttons':
      return <ButtonActions student={student} />;
    case 'dropdown':
      return <DropdownActions student={student} />;
    case 'compact':
    default:
      return <CompactActions student={student} />;
  }
}

export default StudentActions;