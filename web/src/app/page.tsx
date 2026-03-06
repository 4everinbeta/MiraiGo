'use client'

import React, { useState } from 'react'
import useSWR from 'swr'
import { fetcher } from '@/lib/api'
import SearchForm from '@/components/search/SearchForm'
import ResultsDashboard from '@/components/search/ResultsDashboard'

export default function Home() {
  const [searchParams, setSearchParams] = useState<{ q: string } | null>(null)

  const { data, error, isLoading } = useSWR(
    searchParams ? `/search?q=${encodeURIComponent(searchParams.q)}` : null,
    fetcher
  )

  const handleSearch = (params: { q: string }) => {
    setSearchParams(params)
  }

  return (
    <main className="min-h-screen bg-background text-foreground font-sans">
      <div className="max-w-5xl mx-auto px-6 py-16 space-y-16">
        <header className="text-center space-y-6">
          <div className="inline-block px-3 py-1 border-y border-primary/20 text-xs tracking-[0.2em] uppercase text-primary mb-2">
            Mirai 未来
          </div>
          <h1 className="text-5xl font-light tracking-tight lg:text-6xl text-sumi">
            Mirai<span className="text-primary font-bold">Go</span>
          </h1>
          <p className="text-lg text-muted-foreground max-w-lg mx-auto font-light leading-relaxed">
            Discover your next journey with the clarity of the future.
          </p>
        </header>

        <section className="relative">
          <div className="absolute inset-0 bg-sakura/5 -skew-y-1 transform scale-110 pointer-events-none -z-10 rounded-3xl" />
          <SearchForm onSearch={handleSearch} />
        </section>

        {error && (
          <div className="w-full max-w-2xl mx-auto mt-8 p-6 bg-destructive/5 text-destructive rounded-none border-l-4 border-destructive text-sm">
            We encountered a connection issue. Please refine your search and try again.
          </div>
        )}

        <section className="pb-20">
          <ResultsDashboard 
            results={data?.results || []} 
            isLoading={isLoading} 
          />
        </section>
        
        <footer className="text-center text-[10px] text-muted-foreground/40 uppercase tracking-[0.3em] pt-10 border-t border-border/50">
          Built for the future of travel.
        </footer>
      </div>
    </main>
  )
}
