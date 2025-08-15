/**
 * Dashboard Header Component
 * 
 * Professional header displaying user information, role, and context-aware messaging.
 * Shows different content for Form Teachers vs Year Heads.
 */

import { User } from '@/lib/schemas';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/contexts/AuthContext';
import { LogOut, User as UserIcon, School } from 'lucide-react';

interface DashboardHeaderProps {
  user: User;
  studentCount: number;
}

export function DashboardHeader({ user, studentCount }: DashboardHeaderProps) {
  const { logout } = useAuth();

  const handleLogout = async () => {
    try {
      await logout();
      // Redirect will be handled by AuthContext
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const getRoleDisplayName = (role: string) => {
    switch (role) {
      case 'year_head':
        return 'Year Head';
      case 'form_teacher':
        return 'Form Teacher';
      case 'admin':
        return 'Administrator';
      default:
        return role;
    }
  };

  const getRoleBadgeVariant = (role: string): 'default' | 'secondary' | 'outline' | 'destructive' => {
    switch (role) {
      case 'year_head':
        return 'default'; // More prominent for year heads
      case 'form_teacher':
        return 'secondary';
      case 'admin':
        return 'destructive';
      default:
        return 'outline';
    }
  };

  const getContextMessage = (role: string, schoolName: string, studentCount: number) => {
    if (role === 'form_teacher') {
      return `Your assigned students (${studentCount})`;
    } else if (role === 'year_head') {
      return `All students in ${schoolName} (${studentCount})`;
    } else {
      return `Students in ${schoolName} (${studentCount})`;
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
      <div className="flex justify-between items-start">
        {/* Left side - Page title and context */}
        <div className="space-y-2">
          <div className="flex items-center gap-2">
            <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
            <School className="h-6 w-6 text-gray-500" />
          </div>
          <p className="text-gray-600 text-lg">
            {getContextMessage(user.role, user.school_name, studentCount)}
          </p>
          <div className="flex items-center gap-2 text-sm text-gray-500">
            <School className="h-4 w-4" />
            <span>{user.school_name}</span>
          </div>
        </div>

        {/* Right side - User info and actions */}
        <div className="text-right space-y-3">
          {/* Welcome message */}
          <div>
            <p className="text-sm text-gray-500">Welcome back,</p>
            <div className="flex items-center justify-end gap-2 mt-1">
              <UserIcon className="h-4 w-4 text-gray-400" />
              <p className="font-semibold text-gray-900 text-lg">{user.full_name}</p>
            </div>
          </div>

          {/* Role badge */}
          <div className="flex justify-end">
            <Badge variant={getRoleBadgeVariant(user.role)}>
              {getRoleDisplayName(user.role)}
            </Badge>
          </div>

          {/* User actions */}
          <div className="flex justify-end gap-2 pt-2">
            <Button
              variant="outline"
              size="sm"
              onClick={handleLogout}
              className="flex items-center gap-2"
            >
              <LogOut className="h-4 w-4" />
              Logout
            </Button>
          </div>
        </div>
      </div>

      {/* Additional context bar for role-specific information */}
      <div className="mt-4 pt-4 border-t border-gray-100">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-4 text-gray-600">
            <span>
              <strong>Role:</strong> {getRoleDisplayName(user.role)}
            </span>
            <span>
              <strong>School:</strong> {user.school_name}
            </span>
            <span>
              <strong>Students:</strong> {studentCount}
            </span>
          </div>
          
          {/* Role-specific help text */}
          <div className="text-gray-500 italic">
            {user.role === 'form_teacher' && (
              <span>You can view and manage grades for your assigned class</span>
            )}
            {user.role === 'year_head' && (
              <span>You have access to all students in your school</span>
            )}
            {user.role === 'admin' && (
              <span>You have administrative access to all school data</span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}