export type InventoryType = 'stay' | 'flight'

export interface SearchDateRange {
  start: string
  end?: string
}

export interface TravelerCounts {
  adults: number
  children: number
  infants: number
}

export interface StayFilters {
  max_price?: number
  amenities: string[]
}

export interface FlightFilters {
  max_price?: number
  nonstop: boolean
}

export type ClarificationSlot = 'destination' | 'timeline' | 'trip_length' | 'budget'

export interface ClarificationBudgetRange {
  minimum?: number | null
  maximum?: number | null
  currency_code: string
}

export interface WeatherPreference {
  temperature?: 'warm' | 'cool' | 'pleasant' | null
  precipitation?: 'avoid_rain' | 'rain_ok' | null
  source_text?: string | null
}

export interface ClarificationSlotState {
  slot: ClarificationSlot
  value_label?: string | null
  confidence: number
  ambiguous: boolean
  explicit_unknown: boolean
  source: 'user' | 'extracted' | 'system'
}

export interface ClarificationQuestion {
  slot: ClarificationSlot
  prompt: string
  helper_text?: string | null
}

export interface ClarificationRecapChip {
  slot: ClarificationSlot
  label: string
  value_label: string
  editable: boolean
  explicit_unknown: boolean
}

export interface ClarificationRecap {
  chips: ClarificationRecapChip[]
  continue_label: string
}

export interface ClarificationState {
  destination: ClarificationSlotState
  timeline: ClarificationSlotState
  trip_length: ClarificationSlotState
  budget: ClarificationSlotState
  next_question?: ClarificationQuestion | null
  recap: ClarificationRecap
  all_critical_slots_resolved: boolean
}

export interface ClarificationAnswer {
  slot: ClarificationSlot
  answer_text?: string
  explicit_unknown: boolean
}

export interface ClarificationRecapEdit {
  slot: ClarificationSlot
  edited_value?: string
  explicit_unknown: boolean
}

export interface ConstraintUpdates {
  destination?: string
  date_range?: SearchDateRange
  trip_length_days?: number
  budget_range?: ClarificationBudgetRange
  weather_preference?: WeatherPreference
  explicit_unknown_slots: ClarificationSlot[]
}

export interface SearchRequest {
  query?: string
  inventory: InventoryType[]
  destination?: string
  origin?: string
  date_range?: SearchDateRange
  trip_length_days?: number
  budget_range?: ClarificationBudgetRange
  weather_preference?: WeatherPreference
  travelers: TravelerCounts
  stay_filters: StayFilters
  flight_filters: FlightFilters
  currency_code: string
  limit_per_provider: number
  clarification_answer?: ClarificationAnswer
  recap_edit?: ClarificationRecapEdit
  constraint_updates?: ConstraintUpdates
}

export interface ProviderStatus {
  provider: string
  label: string
  configured: boolean
  healthy: boolean
  inventory_types: InventoryType[]
  reason?: string | null
}

interface BaseResult {
  inventory_type: InventoryType
  provider: string
  provider_label: string
  title: string
  description: string
  total_price: number
  currency: string
  redirect_url?: string | null
  deep_link_label?: string | null
  score: number
  price_known: boolean
  price_label?: string | null
}

export interface StaySearchResult extends BaseResult {
  inventory_type: 'stay'
  location_label?: string | null
  rating?: string | null
  amenities: string[]
  nightly_price?: number | null
  check_in?: string | null
  check_out?: string | null
}

export interface FlightSearchResult extends BaseResult {
  inventory_type: 'flight'
  origin_code: string
  destination_code: string
  departure_at: string
  arrival_at: string
  carrier_codes: string[]
  stops: number
  duration?: string | null
}

export type SearchResult = StaySearchResult | FlightSearchResult

export interface SearchResponse {
  search_id: string
  query: string
  requested_inventory: InventoryType[]
  applied_filters: {
    destination?: string | null
    origin?: string | null
    date_range?: SearchDateRange | null
    trip_length_days?: number | null
    budget_range?: ClarificationBudgetRange | null
    weather_preference?: WeatherPreference | null
    travelers: TravelerCounts
    stay_filters: StayFilters
    flight_filters: FlightFilters
  }
  provider_status: ProviderStatus[]
  warnings: string[]
  results: SearchResult[]
  clarification_state?: ClarificationState | null
}

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1'

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...(init?.headers ?? {}),
    },
    cache: 'no-store',
  })

  if (!response.ok) {
    const message = await response.text()
    throw new Error(message || `Request failed with ${response.status}`)
  }

  return response.json() as Promise<T>
}

export async function fetchProviderStatuses(): Promise<ProviderStatus[]> {
  const response = await request<{ providers: ProviderStatus[] }>('/providers/status')
  return response.providers
}

export async function searchTrips(payload: SearchRequest): Promise<SearchResponse> {
  return request<SearchResponse>('/search', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
