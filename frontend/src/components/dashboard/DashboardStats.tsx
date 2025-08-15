/**
 * Dashboard Statistics Component
 * 
 * Displays key metrics and performance indicators in an easy-to-read grid layout.
 * Shows total students, performance band distribution, and grade completion status.
 */

import { DashboardStats as DashboardStatsType } from '@/lib/schemas';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { 
  Users, 
  Trophy, 
  TrendingUp, 
  CheckCircle, 
  Activity,
  Star,
  AlertCircle,
  Target
} from 'lucide-react';

interface DashboardStatsProps {
  stats: DashboardStatsType;
}

/**
 * Individual Stat Card Component
 */
interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ReactNode;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  progress?: number;
  trend?: 'up' | 'down' | 'neutral';
}

function StatCard({ 
  title, 
  value, 
  subtitle, 
  icon, 
  color = 'blue',
  progress,
  trend 
}: StatCardProps) {
  const colorClasses = {
    blue: {
      bg: 'bg-blue-50',
      text: 'text-blue-600',
      icon: 'text-blue-500',
      border: 'border-blue-100'
    },
    green: {
      bg: 'bg-green-50',
      text: 'text-green-600',
      icon: 'text-green-500',
      border: 'border-green-100'
    },
    yellow: {
      bg: 'bg-yellow-50',
      text: 'text-yellow-600',
      icon: 'text-yellow-500',
      border: 'border-yellow-100'
    },
    red: {
      bg: 'bg-red-50',
      text: 'text-red-600',
      icon: 'text-red-500',
      border: 'border-red-100'
    },
    purple: {
      bg: 'bg-purple-50',
      text: 'text-purple-600',
      icon: 'text-purple-500',
      border: 'border-purple-100'
    }
  };

  const colors = colorClasses[color];

  const getTrendIcon = () => {
    if (trend === 'up') return <TrendingUp className="h-3 w-3 text-green-500" />;
    if (trend === 'down') return <TrendingUp className="h-3 w-3 text-red-500 rotate-180" />;
    return null;
  };

  return (
    <Card className={`${colors.border} border-2 hover:shadow-md transition-shadow`}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-gray-600">
          {title}
        </CardTitle>
        <div className={`${colors.bg} p-2 rounded-full`}>
          <div className={colors.icon}>
            {icon}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <div className={`text-2xl font-bold ${colors.text} mb-1`}>
          {value}
        </div>
        {subtitle && (
          <div className="flex items-center gap-1 text-xs text-gray-500">
            {getTrendIcon()}
            <span>{subtitle}</span>
          </div>
        )}
        {progress !== undefined && (
          <div className="mt-3">
            <Progress value={progress} className="h-2" />
            <p className="text-xs text-gray-500 mt-1">{progress}% complete</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
}

/**
 * Performance Band Distribution Component
 */
interface PerformanceBandStatsProps {
  performanceBands: DashboardStatsType['performanceBands'];
  totalStudents: number;
}

function PerformanceBandStats({ performanceBands, totalStudents }: PerformanceBandStatsProps) {
  const bands = [
    {
      name: 'Outstanding',
      count: performanceBands.outstanding,
      color: 'green' as const,
      icon: <Star className="h-4 w-4" />,
      description: '≥85% average'
    },
    {
      name: 'Good',
      count: performanceBands.good,
      color: 'blue' as const,
      icon: <Trophy className="h-4 w-4" />,
      description: '70-84% average'
    },
    {
      name: 'Satisfactory',
      count: performanceBands.satisfactory,
      color: 'yellow' as const,
      icon: <Target className="h-4 w-4" />,
      description: '55-69% average'
    },
    {
      name: 'Needs Improvement',
      count: performanceBands.needsImprovement,
      color: 'red' as const,
      icon: <AlertCircle className="h-4 w-4" />,
      description: '<55% average'
    }
  ];

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm font-medium text-gray-600">
          Performance Distribution
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {bands.map((band) => {
            const percentage = totalStudents > 0 ? Math.round((band.count / totalStudents) * 100) : 0;
            const colorClasses = {
              green: 'bg-green-100 text-green-800',
              blue: 'bg-blue-100 text-blue-800',
              yellow: 'bg-yellow-100 text-yellow-800',
              red: 'bg-red-100 text-red-800'
            };
            
            return (
              <div key={band.name} className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className={`p-1 rounded ${colorClasses[band.color]}`}>
                    {band.icon}
                  </div>
                  <div>
                    <p className="text-sm font-medium">{band.name}</p>
                    <p className="text-xs text-gray-500">{band.description}</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm font-bold">{band.count}</p>
                  <p className="text-xs text-gray-500">{percentage}%</p>
                </div>
              </div>
            );
          })}
        </div>
      </CardContent>
    </Card>
  );
}

/**
 * Main Dashboard Statistics Component
 */
export function DashboardStats({ stats }: DashboardStatsProps) {
  const {
    totalStudents,
    performanceBands,
    gradeCompletion,
    recentActivity
  } = stats;

  // Calculate trends and insights
  const outstandingPercentage = totalStudents > 0 
    ? Math.round((performanceBands.outstanding / totalStudents) * 100) 
    : 0;

  const needsImprovementPercentage = totalStudents > 0 
    ? Math.round((performanceBands.needsImprovement / totalStudents) * 100) 
    : 0;

  return (
    <div className="space-y-6">
      {/* Main Statistics Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Students"
          value={totalStudents}
          subtitle={`Across all classes`}
          icon={<Users className="h-4 w-4" />}
          color="blue"
        />

        <StatCard
          title="Outstanding Students"
          value={performanceBands.outstanding}
          subtitle={`${outstandingPercentage}% of total`}
          icon={<Star className="h-4 w-4" />}
          color="green"
          trend={outstandingPercentage > 25 ? 'up' : 'neutral'}
        />

        <StatCard
          title="Grade Completion"
          value={`${gradeCompletion}%`}
          subtitle="All subjects recorded"
          icon={<CheckCircle className="h-4 w-4" />}
          color="purple"
          progress={gradeCompletion}
        />

        <StatCard
          title="Recent Activity"
          value={recentActivity}
          subtitle="Reports generated today"
          icon={<Activity className="h-4 w-4" />}
          color="yellow"
        />
      </div>

      {/* Detailed Performance Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <PerformanceBandStats 
          performanceBands={performanceBands} 
          totalStudents={totalStudents} 
        />

        {/* Quick Insights Card */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm font-medium text-gray-600">
              Quick Insights
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-start gap-3 p-3 bg-green-50 rounded-lg">
              <Star className="h-5 w-5 text-green-500 mt-0.5 flex-shrink-0" />
              <div>
                <p className="text-sm font-medium text-green-800">
                  Excellent Performance
                </p>
                <p className="text-xs text-green-600">
                  {performanceBands.outstanding} students achieving outstanding results
                </p>
              </div>
            </div>

            {needsImprovementPercentage > 20 && (
              <div className="flex items-start gap-3 p-3 bg-red-50 rounded-lg">
                <AlertCircle className="h-5 w-5 text-red-500 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-red-800">
                    Attention Needed
                  </p>
                  <p className="text-xs text-red-600">
                    {performanceBands.needsImprovement} students need additional support
                  </p>
                </div>
              </div>
            )}

            {gradeCompletion < 90 && (
              <div className="flex items-start gap-3 p-3 bg-yellow-50 rounded-lg">
                <CheckCircle className="h-5 w-5 text-yellow-500 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-yellow-800">
                    Grade Recording
                  </p>
                  <p className="text-xs text-yellow-600">
                    {100 - gradeCompletion}% of grades still need to be recorded
                  </p>
                </div>
              </div>
            )}

            {gradeCompletion >= 90 && needsImprovementPercentage <= 20 && (
              <div className="flex items-start gap-3 p-3 bg-blue-50 rounded-lg">
                <Trophy className="h-5 w-5 text-blue-500 mt-0.5 flex-shrink-0" />
                <div>
                  <p className="text-sm font-medium text-blue-800">
                    Great Progress
                  </p>
                  <p className="text-xs text-blue-600">
                    Your students are performing well across all subjects
                  </p>
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}