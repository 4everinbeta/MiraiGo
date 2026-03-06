'use client'

import React, { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Search } from 'lucide-react'

interface SearchFormProps {
  onSearch: (params: { q: string }) => void
}

const SearchForm: React.FC<SearchFormProps> = ({ onSearch }) => {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch({ q: query })
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
          <div className="bg-sakura/10 px-6 py-2 flex justify-between items-center border-t border-sakura/20">
            <span className="text-[10px] text-primary/60 uppercase tracking-wider font-medium">
              Flexible Search Enabled
            </span>
            <div className="flex gap-4">
               {/* Placeholders for future fields */}
               <button type="button" className="text-[10px] text-muted-foreground hover:text-primary transition-colors uppercase tracking-wider">Add Dates</button>
               <button type="button" className="text-[10px] text-muted-foreground hover:text-primary transition-colors uppercase tracking-wider">Qualities</button>
            </div>
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

export default SearchForm
