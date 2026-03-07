'use client'

import React, { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Search, Calendar as CalendarIcon, Tag, X } from 'lucide-react'
import { Calendar } from '@/components/ui/calendar'
import { Popover, PopoverContent, PopoverTrigger } from '@/components/ui/popover'
import { cn } from '@/lib/utils'
import { format } from 'date-fns'
import { DateRange } from 'react-day-picker'

interface SearchFormProps {
  onSearch: (params: { q: string; dateRange?: DateRange; qualities?: string[] }) => void
}

const AVAILABLE_QUALITIES = ["Beach", "Mountains", "Luxury", "Budget", "Family", "Romantic", "Quiet", "Hiking", "Skiing"]

const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('')
  const [showDates, setShowDates] = useState(false)
  const [showQualities, setShowQualities] = useState(false)
  const [dateRange, setDateRange] = useState<DateRange | undefined>(undefined)
  const [selectedQualities, setSelectedQualities] = useState<string[]>([])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch({ 
      q: query,
      dateRange: dateRange,
      qualities: selectedQualities
    })
  }

  const toggleQuality = (quality: string) => {
    setSelectedQualities(prev => 
      prev.includes(quality) 
        ? prev.filter(q => q !== quality) 
        : [...prev, quality]
    )
  }

  return (
    <Card className="w-full max-w-2xl mx-auto rounded-none border-none shadow-2xl overflow-hidden group">
      <CardContent className="p-0">
        <form onSubmit={handleSubmit} className="flex flex-col">
          <div className="flex items-center bg-white p-2">
            <div className="pl-4 pr-2 text-muted-foreground group-focus-within:text-primary transition-colors">
              <Search size={20} strokeWidth={1.5} />
            </div>
            <Input
              placeholder="Where do you want to go? Type naturally..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1 border-none shadow-none focus-visible:ring-1 focus-visible:ring-primary/20 text-lg py-8 placeholder:text-muted-foreground/50 placeholder:font-light font-light"
            />
            <Button 
              type="submit" 
              className="rounded-none px-10 py-8 h-auto bg-primary hover:bg-indigo-jp transition-all text-sm uppercase tracking-widest font-bold"
            >
              Search
            </Button>
          </div>

          {(showDates || showQualities) && (
            <div className="bg-white border-t border-border p-6 space-y-6 animate-in fade-in slide-in-from-top-2">
              {showDates && (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <label className="text-[10px] uppercase tracking-widest font-bold text-primary/60">Date Range</label>
                    {dateRange && (
                      <button type="button" onClick={() => setDateRange(undefined)} className="text-[10px] text-muted-foreground hover:text-destructive flex items-center gap-1">
                        <X size={10} /> Clear
                      </button>
                    )}
                  </div>
                  <Popover>
                    <PopoverTrigger asChild>
                      <Button
                        id="date"
                        variant={"outline"}
                        className={cn(
                          "w-full justify-start text-left font-normal rounded-none border-border hover:bg-sakura/5",
                          !dateRange && "text-muted-foreground"
                        )}
                      >
                        <CalendarIcon className="mr-2 h-4 w-4" />
                        {dateRange?.from ? (
                          dateRange.to ? (
                            <>
                              {format(dateRange.from, "LLL dd, y")} -{" "}
                              {format(dateRange.to, "LLL dd, y")}
                            </>
                          ) : (
                            format(dateRange.from, "LLL dd, y")
                          )
                        ) : (
                          <span>Pick a date range</span>
                        )}
                      </Button>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0 rounded-none border-border" align="start">
                      <Calendar
                        initialFocus
                        mode="range"
                        defaultMonth={dateRange?.from}
                        selected={dateRange}
                        onSelect={setDateRange}
                        numberOfMonths={2}
                      />
                    </PopoverContent>
                  </Popover>
                </div>
              )}
              
              {showQualities && (
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <label className="text-[10px] uppercase tracking-widest font-bold text-primary/60">Desired Qualities</label>
                    {selectedQualities.length > 0 && (
                      <button type="button" onClick={() => setSelectedQualities([])} className="text-[10px] text-muted-foreground hover:text-destructive flex items-center gap-1">
                        <X size={10} /> Clear All
                      </button>
                    )}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {AVAILABLE_QUALITIES.map(q => (
                      <button
                        key={q}
                        type="button"
                        onClick={() => toggleQuality(q)}
                        className={cn(
                          "px-4 py-1.5 text-[10px] uppercase tracking-tighter rounded-full border transition-all",
                          selectedQualities.includes(q)
                            ? "bg-primary text-primary-foreground border-primary shadow-md"
                            : "bg-muted text-muted-foreground border-border hover:bg-sakura/20 hover:border-sakura/40"
                        )}
                      >
                        {q}
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          <div className="bg-sakura/10 px-6 py-2 flex justify-between items-center border-t border-sakura/20">
            <span className="text-[10px] text-primary uppercase tracking-wider font-medium">
              Flexible Search Enabled
            </span>
            <div className="flex gap-4">
               <button 
                type="button" 
                onClick={() => setShowDates(!showDates)}
                className={cn("text-[10px] uppercase tracking-wider transition-colors", showDates ? "text-primary font-bold" : "text-muted-foreground hover:text-primary")}
               >
                {dateRange?.from ? (
                  dateRange.to ? `${format(dateRange.from, "MMM dd")} - ${format(dateRange.to, "MMM dd")}` : format(dateRange.from, "MMM dd")
                ) : "Add Dates"}
               </button>
               <button 
                type="button" 
                onClick={() => setShowQualities(!showQualities)}
                className={cn("text-[10px] uppercase tracking-wider transition-colors", showQualities ? "text-primary font-bold" : "text-muted-foreground hover:text-primary")}
               >
                {selectedQualities.length > 0 ? `${selectedQualities.length} Qualities` : "Qualities"}
               </button>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

export default SearchForm
