'use client'

import { useState } from 'react'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'

interface BehavioralCommentsProps {
  value: string
  onChange: (value: string) => void
  maxLength?: number
}

export function BehavioralComments({ 
  value, 
  onChange, 
  maxLength = 500 
}: BehavioralCommentsProps) {
  const [showQuickPhrases, setShowQuickPhrases] = useState(false)
  
  const quickPhrases = [
    "Shows excellent participation in class discussions",
    "Demonstrates strong leadership qualities among peers",
    "Works well independently and collaboratively in groups", 
    "Shows consistent effort and determination to improve",
    "Displays positive attitude toward learning challenges",
    "Respectful and considerate toward classmates and teachers",
    "Takes initiative in completing assignments and projects",
    "Demonstrates creativity and original thinking"
  ]

  const handleQuickPhraseInsert = (phrase: string) => {
    const newValue = value ? `${value} ${phrase}` : phrase
    if (newValue.length <= maxLength) {
      onChange(newValue)
    }
    setShowQuickPhrases(false)
  }

  const getCharacterCountColor = () => {
    const percentage = value.length / maxLength
    if (percentage >= 0.9) return 'text-red-600'
    if (percentage >= 0.7) return 'text-yellow-600'
    return 'text-gray-500'
  }

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle>Behavioral Comments</CardTitle>
            <CardDescription>
              Add observations about the student&apos;s behavior, attitude, and social skills.
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowQuickPhrases(!showQuickPhrases)}
          >
            Quick Phrases
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        {showQuickPhrases && (
          <div className="mb-4 p-4 bg-gray-50 rounded-lg">
            <h4 className="font-medium mb-2">Quick Phrases</h4>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {quickPhrases.map((phrase, index) => (
                <Button
                  key={index}
                  variant="ghost"
                  size="sm"
                  className="justify-start text-left h-auto p-2 text-xs"
                  onClick={() => handleQuickPhraseInsert(phrase)}
                  disabled={value.length + phrase.length > maxLength}
                >
                  <span className="mr-2">+</span>
                  <span>{phrase}</span>
                </Button>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-2">
          <Textarea
            value={value}
            onChange={(e) => onChange(e.target.value)}
            placeholder="Enter your observations about the student&apos;s behavior, participation, and social interactions..."
            className="min-h-[120px] resize-none"
            maxLength={maxLength}
          />
          <div className="flex justify-between items-center text-sm">
            <span className="text-gray-500">
              Comments help provide a complete picture of the student&apos;s development.
            </span>
            <span className={getCharacterCountColor()}>
              {value.length}/{maxLength} characters
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  )
}