import React from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, Loader2, ExternalLink } from 'lucide-react'

interface TravelResult {
  provider: string
  text: string
  score: number
  link?: string
}

interface ResultsDashboardProps {
  results: TravelResult[]
  isLoading: boolean
}

const PROVIDERS = [
  { id: 'expedia', name: 'Expedia' },
  { id: 'booking', name: 'Booking.com' },
  { id: 'airbnb', name: 'Airbnb' }
]

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ results, isLoading }) => {
  if (isLoading) {
    return (
      <div className="w-full max-w-2xl mx-auto space-y-12">
        <div className="flex flex-col items-center justify-center py-10 space-y-4">
          <div className="w-12 h-[1px] bg-primary animate-pulse" />
          <span className="text-[10px] uppercase tracking-[0.4em] text-primary/60 font-light italic">Seeking the future...</span>
        </div>

        <div className="grid grid-cols-3 gap-4">
          {PROVIDERS.map(p => (
            <div key={p.id} className="flex flex-col items-center gap-2 p-4 bg-sakura/5 border border-primary/5">
              <Loader2 className="h-4 w-4 animate-spin text-primary/40" />
              <span className="text-[9px] uppercase tracking-widest font-bold text-primary/60">{p.name}</span>
            </div>
          ))}
        </div>

        <div className="space-y-6">
          {[1, 2, 3].map(i => (
            <div key={i} data-testid="loading-skeleton" className="h-24 w-full bg-muted/20 animate-pulse rounded-none border-l-2 border-primary/5" />
          ))}
        </div>
      </div>
    )
  }

  if (results.length === 0) {
    return null
  }

  const CardWrapper = ({ result, children }: { result: TravelResult, children: React.ReactNode }) => {
    if (result.link) {
      return (
        <a href={result.link} target="_blank" rel="noopener noreferrer" className="block group">
          {children}
        </a>
      )
    }
    return <div className="group">{children}</div>
  }

  return (
    <div className="w-full max-w-2xl mx-auto mt-12 flex flex-col gap-8">
      <div className="flex items-center gap-4 px-2">
        <h2 className="text-xs uppercase tracking-[0.3em] font-bold text-sumi">Refined Options</h2>
        <div className="flex-1 h-[1px] bg-border/50" />
      </div>
      
      <div className="flex flex-col gap-6">
        {results.map((result, index) => (
          <CardWrapper key={index} result={result}>
            <Card className="rounded-none border-none border-l border-primary/10 bg-transparent hover:bg-sakura/5 transition-all duration-300 relative">
              <div className="flex items-stretch">
                <div className="w-[1px] bg-transparent group-hover:bg-primary transition-all duration-500" />
                <div className="flex-1 py-4">
                  <CardHeader className="pb-2 pt-0 px-6">
                    <div className="flex justify-between items-end">
                      <CardTitle className="text-[10px] font-bold text-primary uppercase tracking-[0.2em] flex items-center gap-2">
                        {result.provider}
                        {result.link && <ExternalLink size={10} className="text-primary/40 group-hover:text-primary transition-colors" />}
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
          </CardWrapper>
        ))}
      </div>
    </div>
  )
}

export default ResultsDashboard
