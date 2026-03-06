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
      <div className="flex flex-col items-center justify-center py-20 space-y-4">
        <div className="w-12 h-[1px] bg-primary animate-pulse" />
        <span className="text-[10px] uppercase tracking-[0.4em] text-primary/60 font-light">Seeking the future...</span>
      </div>
    )
  }

  if (results.length === 0) {
    return null
  }

  return (
    <div className="w-full max-w-2xl mx-auto mt-12 flex flex-col gap-8">
      <div className="flex items-center gap-4 px-2">
        <h2 className="text-xs uppercase tracking-[0.3em] font-bold text-sumi">Refined Options</h2>
        <div className="flex-1 h-[1px] bg-border/50" />
      </div>
      
      <div className="flex flex-col gap-6">
        {results.map((result, index) => (
          <Card key={index} className="rounded-none border-none border-l border-primary/10 bg-transparent hover:bg-sakura/5 transition-colors group">
            <div className="flex items-stretch">
              <div className="w-[1px] bg-transparent group-hover:bg-primary transition-all duration-500" />
              <div className="flex-1 py-4">
                <CardHeader className="pb-2 pt-0 px-6">
                  <div className="flex justify-between items-end">
                    <CardTitle className="text-[10px] font-bold text-primary uppercase tracking-[0.2em]">
                      {result.provider}
                    </CardTitle>
                    <div className="text-[10px] font-light text-muted-foreground tabular-nums">
                      Score // <span className="text-sumi font-medium">{result.score}</span>
                    </div>
                  </div>
                </CardHeader>
                <CardContent className="px-6">
                  <p className="text-sm font-light leading-relaxed text-sumi/80 group-hover:text-sumi transition-colors">
                    {result.text}
                  </p>
                </CardContent>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

export default ResultsDashboard
