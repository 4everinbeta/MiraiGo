import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'

interface TravelResult {
  provider: string
  text: string
  score: number
}

interface ResultsDashboardProps {
  results: TravelResult[]
  isLoading: boolean
}

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mr-2"></div>
        <span>Searching for the best options...</span>
      </div>
    )
  }

  if (results.length === 0) {
    return (
      <Card className="w-full max-w-2xl mx-auto mt-8">
        <CardContent className="py-12 text-center text-muted-foreground">
          No results found. Try a different search!
        </CardContent>
      </Card>
    )
  }

  return (
    <div className="w-full max-w-2xl mx-auto mt-8 flex flex-col gap-4">
      <h2 className="text-xl font-bold px-2">Top Results</h2>
      {results.map((result, index) => (
        <Card key={index} className="overflow-hidden">
          <div className="flex items-stretch">
            <div className="w-2 bg-primary"></div>
            <div className="flex-1">
              <CardHeader className="pb-2">
                <div className="flex justify-between items-start">
                  <CardTitle className="text-sm font-medium text-muted-foreground uppercase tracking-wider">
                    {result.provider}
                  </CardTitle>
                  <div className="bg-primary/10 text-primary text-xs font-bold px-2 py-1 rounded">
                    Match: {result.score}
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-sm leading-relaxed">{result.text}</p>
              </CardContent>
            </div>
          </div>
        </Card>
      ))}
    </div>
  )
}

export default ResultsDashboard
