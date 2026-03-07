import React, { useState, useMemo } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { CheckCircle2, Loader2, ExternalLink, Filter, DollarSign, Wifi, Waves, Dumbbell, Coffee } from 'lucide-react'
import { cn } from '@/lib/utils'
import { Separator } from '@/components/ui/separator'
import { Slider } from '@/components/ui/slider'
import { Checkbox } from '@/components/ui/checkbox'

interface TravelResult {
  provider: string
  text: string
  score: number
  price?: number
  amenities?: string[]
  link?: string
}

interface ResultsDashboardProps {
  results: TravelResult[]
  isLoading: boolean
}

const PROVIDERS = [
  { id: 'Expedia', name: 'Expedia' },
  { id: 'Booking.com', name: 'Booking.com' },
  { id: 'Airbnb', name: 'Airbnb' },
  { id: 'Amadeus', name: 'Amadeus' },
  { id: 'LocalNiche', name: 'LocalNiche' }
]

const AMENITY_OPTIONS = [
  { id: 'wifi', label: 'WiFi', icon: <Wifi size={12} /> },
  { id: 'pool', label: 'Pool', icon: <Waves size={12} /> },
  { id: 'gym', label: 'Gym', icon: <Dumbbell size={12} /> },
  { id: 'breakfast', label: 'Breakfast', icon: <Coffee size={12} /> }
]

const ResultsDashboard: React.FC<ResultsDashboardProps> = ({ results, isLoading }) => {
  const [activeProviders, setActiveProviders] = useState<string[]>([])
  const [maxPrice, setMaxPrice] = useState<number>(5000)
  const [selectedAmenities, setSelectedAmenities] = useState<string[]>([])

  const toggleProvider = (id: string) => {
    setActiveProviders(prev => prev.includes(id) ? prev.filter(p => p !== id) : [...prev, id])
  }

  const toggleAmenity = (id: string) => {
    setSelectedAmenities(prev => prev.includes(id) ? prev.filter(a => a !== id) : [...prev, id])
  }

  const filteredResults = useMemo(() => {
    return results.filter(r => {
      const matchProvider = activeProviders.length === 0 || activeProviders.includes(r.provider)
      const matchPrice = !r.price || r.price <= maxPrice
      const matchAmenities = selectedAmenities.length === 0 || 
        selectedAmenities.every(sa => r.amenities?.some(ra => ra.toLowerCase().includes(sa.toLowerCase())))
      
      return matchProvider && matchPrice && matchAmenities
    })
  }, [results, activeProviders, maxPrice, selectedAmenities])

  if (isLoading) {
    return (
      <div className="w-full max-w-4xl mx-auto space-y-12">
        <div className="flex flex-col items-center justify-center py-10 space-y-4">
          <div className="w-12 h-[1px] bg-primary animate-pulse" />
          <span className="text-[10px] uppercase tracking-[0.4em] text-primary/60 font-light italic">Seeking the future...</span>
        </div>
        <div className="grid grid-cols-5 gap-2">
          {PROVIDERS.map(p => (
            <div key={p.id} className="flex flex-col items-center gap-2 p-3 bg-sakura/5 border border-primary/5">
              <Loader2 className="h-3 w-3 animate-spin text-primary/40" />
              <span className="text-[8px] uppercase tracking-widest font-bold text-primary/60">{p.name}</span>
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

  if (results.length === 0) return null

  return (
    <div className="w-full max-w-6xl mx-auto mt-12 grid grid-cols-1 md:grid-cols-[250px_1fr] gap-10">
      {/* Sidebar Filters */}
      <aside className="space-y-8 animate-in fade-in slide-in-from-left-4 duration-700">
        <div className="space-y-4">
          <h3 className="text-[10px] uppercase tracking-[0.2em] font-bold text-primary flex items-center gap-2">
            <Filter size={12} /> Filters
          </h3>
          <Separator className="bg-primary/10" />
        </div>

        {/* Provider Filter */}
        <div className="space-y-4">
          <h4 className="text-[9px] uppercase tracking-widest font-bold text-muted-foreground">Providers</h4>
          <div className="flex flex-col gap-2">
            {PROVIDERS.map(p => (
              <div key={p.id} className="flex items-center space-x-2">
                <Checkbox 
                  id={`p-${p.id}`} 
                  checked={activeProviders.includes(p.id)}
                  onCheckedChange={() => toggleProvider(p.id)}
                />
                <label htmlFor={`p-${p.id}`} className="text-[10px] uppercase tracking-tighter font-medium leading-none cursor-pointer">
                  {p.name}
                </label>
              </div>
            ))}
          </div>
        </div>

        {/* Budget Filter */}
        <div className="space-y-4">
          <div className="flex justify-between items-end">
            <h4 className="text-[9px] uppercase tracking-widest font-bold text-muted-foreground">Max Budget</h4>
            <span className="text-[10px] font-mono font-bold text-primary">${maxPrice}</span>
          </div>
          <Slider
            defaultValue={[5000]}
            max={5000}
            step={50}
            onValueChange={(vals) => setMaxPrice(vals[0])}
            className="py-4"
          />
        </div>

        {/* Amenities Filter */}
        <div className="space-y-4">
          <h4 className="text-[9px] uppercase tracking-widest font-bold text-muted-foreground">Amenities</h4>
          <div className="flex flex-wrap gap-2">
            {AMENITY_OPTIONS.map(a => (
              <button
                key={a.id}
                onClick={() => toggleAmenity(a.id)}
                className={cn(
                  "flex items-center gap-1.5 px-3 py-1.5 text-[9px] uppercase tracking-tighter border transition-all",
                  selectedAmenities.includes(a.id)
                    ? "bg-primary text-primary-foreground border-primary"
                    : "bg-transparent text-muted-foreground border-border hover:border-primary/40"
                )}
              >
                {a.icon} {a.label}
              </button>
            ))}
          </div>
        </div>
      </aside>

      {/* Main Results Area */}
      <div className="flex flex-col gap-8">
        <div className="flex items-center gap-4">
          <h2 className="text-xs uppercase tracking-[0.3em] font-bold text-sumi">
            Refined Options ({filteredResults.length})
          </h2>
          <div className="flex-1 h-[1px] bg-border/50" />
        </div>
        
        <div className="flex flex-col gap-6">
          {filteredResults.length > 0 ? (
            filteredResults.map((result, index) => (
              <a key={index} href={result.link} target="_blank" rel="noopener noreferrer" className="block group">
                <Card className="rounded-none border-none border-l border-primary/10 bg-transparent hover:bg-sakura/5 transition-all duration-300 relative">
                  <div className="flex items-stretch">
                    <div className="w-[1px] bg-transparent group-hover:bg-primary transition-all duration-500" />
                    <div className="flex-1 py-6 px-8">
                      <div className="flex justify-between items-start mb-4">
                        <div className="space-y-1">
                          <span className="text-[10px] font-bold text-primary uppercase tracking-[0.2em] flex items-center gap-2">
                            {result.provider}
                            {result.link && <ExternalLink size={10} className="text-primary/40 group-hover:text-primary transition-colors" />}
                          </span>
                          <h3 className="text-sm font-medium text-sumi group-hover:text-primary transition-colors">{result.text}</h3>
                        </div>
                        <div className="text-right">
                          <div className="text-[10px] font-light text-muted-foreground uppercase tracking-widest mb-1">Match Score</div>
                          <div className="text-xl font-light text-sumi tabular-nums">
                            {result.score}<span className="text-[10px] text-muted-foreground ml-1">// 100</span>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex justify-between items-center">
                        <div className="flex gap-3">
                          {result.amenities?.slice(0, 3).map(a => (
                            <span key={a} className="text-[9px] uppercase tracking-widest text-muted-foreground/60 px-2 py-0.5 border border-border/40">
                              {a}
                            </span>
                          ))}
                        </div>
                        {result.price && (
                          <div className="flex items-center gap-1 text-primary font-bold">
                            <span className="text-[10px] font-normal text-muted-foreground uppercase tracking-widest mr-1">From</span>
                            <DollarSign size={12} />
                            <span className="text-lg tabular-nums">{result.price}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                </Card>
              </a>
            ))
          ) : (
            <div className="py-20 text-center text-[10px] uppercase tracking-[0.4em] text-muted-foreground bg-muted/5 border border-dashed border-border font-light">
              No results match your active filters.
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default ResultsDashboard
