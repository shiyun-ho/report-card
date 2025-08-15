'use client'

import { useState, useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { apiClient } from '@/lib/api'

interface AchievementSelectionProps {
  studentId: number
  termId: number
  onSelectionChange: (achievements: SelectedAchievement[]) => void
}

interface SelectedAchievement {
  id?: number // undefined for custom achievements
  title: string
  description: string
  isCustom: boolean
}

interface AchievementSuggestionResponse {
  title: string
  description: string
  category_name: string
  relevance_score: number
  explanation: string
  supporting_data: Record<string, unknown>
}

interface StudentAchievementSuggestionsResponse {
  student_id: number
  term_id: number
  student_name: string
  term_name: string
  suggestions: AchievementSuggestionResponse[]
  total_suggestions: number
  average_relevance: number
}

export function AchievementSelection({ 
  studentId, 
  termId, 
  onSelectionChange 
}: AchievementSelectionProps) {
  const { data: suggestions, isLoading, error } = useQuery<StudentAchievementSuggestionsResponse>({
    queryKey: ['achievements', 'suggest', studentId, termId],
    queryFn: () => apiClient.get(`/achievements/suggest/${studentId}/${termId}`)
  })

  const [selectedTitles, setSelectedTitles] = useState<string[]>([])

  const handleSuggestionToggle = (suggestionTitle: string) => {
    setSelectedTitles(prev => 
      prev.includes(suggestionTitle) 
        ? prev.filter(title => title !== suggestionTitle)
        : [...prev, suggestionTitle]
    )
  }

  // Update parent component when selection changes
  useEffect(() => {
    const selectedSuggestions: SelectedAchievement[] = suggestions?.suggestions
      .filter(s => selectedTitles.includes(s.title))
      .map(s => ({
        title: s.title,
        description: s.description,
        isCustom: false
      })) || []

    onSelectionChange(selectedSuggestions)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedTitles, suggestions]) // onSelectionChange intentionally excluded to prevent infinite loop

  if (isLoading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Achievement Selection</CardTitle>
          <CardDescription>Loading achievement suggestions...</CardDescription>
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

  if (error || !suggestions) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="text-red-600">Error Loading Achievements</CardTitle>
          <CardDescription>
            Unable to load achievement suggestions. You may not have permission to access this data.
          </CardDescription>
        </CardHeader>
      </Card>
    )
  }

  const getRelevanceColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50 border-green-200'
    if (score >= 0.6) return 'text-blue-600 bg-blue-50 border-blue-200'
    if (score >= 0.4) return 'text-yellow-600 bg-yellow-50 border-yellow-200'
    return 'text-gray-600 bg-gray-50 border-gray-200'
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Achievement Selection (Optional)</CardTitle>
        <CardDescription>
          Select achievements based on {suggestions.student_name}&apos;s performance. 
          {selectedTitles.length}/8 selected (achievements are optional)
        </CardDescription>
      </CardHeader>
      <CardContent>
        {/* Auto-suggested Achievements */}
        <div className="mb-6">
          <h3 className="font-semibold mb-3">Suggested Achievements</h3>
          {suggestions.suggestions.length === 0 ? (
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <p className="text-blue-800 text-sm font-medium mb-2">
                No academic achievements detected
              </p>
              <p className="text-blue-700 text-sm">
                This student shows consistent performance with no significant improvements that would trigger achievement suggestions. 
                You can still generate a report using behavioral comments only.
              </p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {suggestions.suggestions.map((suggestion, index) => {
                const isSelected = selectedTitles.includes(suggestion.title)
                const isDisabled = !isSelected && selectedTitles.length >= 8

                return (
                  <div 
                    key={index} 
                    className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                      isSelected 
                        ? 'border-blue-500 bg-blue-50' 
                        : isDisabled 
                          ? 'border-gray-200 bg-gray-50 opacity-50' 
                          : 'border-gray-200 hover:border-gray-300'
                    }`} 
                    onClick={isDisabled ? undefined : () => handleSuggestionToggle(suggestion.title)}
                  >
                    <div className="flex items-start space-x-3">
                      <Checkbox
                        checked={isSelected}
                        disabled={isDisabled}
                        className="mt-1"
                        onChange={() => handleSuggestionToggle(suggestion.title)}
                      />
                      <div className="flex-1 min-w-0">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium text-sm">{suggestion.title}</h4>
                          <div className={`px-2 py-1 rounded text-xs border ${getRelevanceColor(suggestion.relevance_score)}`}>
                            {Math.round(suggestion.relevance_score * 100)}% match
                          </div>
                        </div>
                        <p className="text-sm text-gray-600 mb-2">{suggestion.description}</p>
                        <p className="text-xs text-gray-500">{suggestion.explanation}</p>
                        <div className="mt-2">
                          <Badge variant="outline" className="text-xs">
                            {suggestion.category_name}
                          </Badge>
                        </div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}