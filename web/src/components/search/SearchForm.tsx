'use strict'

import React, { useState } from 'react'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

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
    <Card className="w-full max-w-2xl mx-auto">
      <CardContent className="pt-6">
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex gap-2">
            <Input
              placeholder="Search your dream trip (e.g., 'Beach trip to Miami next summer')"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              className="flex-1"
            />
            <Button type="submit">Search</Button>
          </div>
          {/* Structured fields placeholder for future implementation */}
          <div className="text-xs text-muted-foreground italic">
            Tip: You can also use specific fields below or just type naturally!
          </div>
        </form>
      </CardContent>
    </Card>
  )
}

export default SearchForm
