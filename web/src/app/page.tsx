'use client'

import React, { useState } from 'react'
import useSWR from 'swr'
import { fetcher } from '@/lib/api'
import SearchForm from '@/components/search/SearchForm'
import ResultsDashboard from '@/components/search/ResultsDashboard'

export default function Home() {
  const [searchParams, setSearchParams] = useState<{ q: string } | null>(null)

  // Only fetch when searchParams is set
  const { data, error, isLoading } = useSWR(
    searchParams ? `/search?q=${encodeURIComponent(searchParams.q)}` : null,
    fetcher
  )

  const handleSearch = (params: { q: string }) => {
    setSearchParams(params)
  }

  return (
    <main className="min-h-screen p-8 bg-background">
      <div className="max-w-4xl mx-auto space-y-12">
        <header className="text-center space-y-4">
          <h1 className="text-4xl font-extrabold tracking-tight lg:text-5xl">
            MiraiGo
          </h1>
          <p className="text-xl text-muted-foreground">
            The future of travel discovery.
          </p>
        </header>

        <section>
          <SearchForm onSearch={handleSearch} />
        </section>

        {error && (
          <div className="w-full max-w-2xl mx-auto mt-8 p-4 bg-destructive/10 text-destructive rounded-md border border-destructive/20 text-center">
            Something went wrong while searching. Please try again.
          </div>
        )}

        <section>
          <ResultsDashboard 
            results={data?.results || []} 
            isLoading={isLoading} 
          />
        </section>
      </div>
    </main>
  )
}
