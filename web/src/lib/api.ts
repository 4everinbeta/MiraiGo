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

export type ClarificationSlot = 'destination' | 'timeline' | 'trip_length' | 'budget' | 'weather'

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

export type DestinationSuggestionKind = 'region' | 'destination'
export type DestinationSuggestionSource = 'curated' | 'trend' | 'extracted'

export interface DestinationSuggestion {
  id: string
  kind: DestinationSuggestionKind
  label: string
  parent_region?: string | null
  signals?: string[]
  popularity_score?: number
  source: DestinationSuggestionSource
}

export type DateFlexibility = 'fixed' | 'few-days' | 'week-flex' | 'fully-flexible'
export type DestinationSelectionMode = 'single' | 'compare'

export interface FlightPreferenceConstraints {
  nonstop?: boolean
  max_travel_hours?: number
}

export interface RecommendationComparison {
  travel_time_fit?: number
  budget_fit?: number
  style_fit?: number
  flexibility_fit?: number
}

export interface RecommendationPackage {
  bundle_id: string
  destination: string
  score: number
  rationale: string[]
  rationale_text?: string | null
  reason_tags?: string[]
  estimated_total_cost?: number
  hard_constraint_status?: Record<string, boolean>
  fallback_level?: 'high-fit' | 'partial-fit' | 'fallback'
  duplicate_signature?: string | null
  comparison?: RecommendationComparison
}

export interface FlightOptionsGroup {
  primary?: FlightSearchResult[]
  nearby_date_alternatives?: FlightSearchResult[]
  partial_availability?: boolean
  warnings?: string[]
}

export interface LodgingOptionsGroup {
  hotels?: StaySearchResult[]
  bed_and_breakfasts?: StaySearchResult[]
  vacation_rentals?: StaySearchResult[]
  partial_availability?: boolean
  warnings?: string[]
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
  weather?: ClarificationSlotState | null
  destination_suggestions?: DestinationSuggestion[]
  supports_multi_destination_compare?: boolean
  destination_selection_mode?: DestinationSelectionMode
  resolved_destination_candidates?: string[]
  next_question?: ClarificationQuestion | null
  recap: ClarificationRecap
  all_critical_slots_resolved: boolean
  resolved_origin?: string | null
  resolved_date_range?: SearchDateRange | null
  flight_requirements_pending: string[]
  continue_block_reason?: string | null
  loop_guard_counter?: number
  repeated_question_slot?: ClarificationSlot | null
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
  origin?: string
  destination?: string
  destination_candidates?: string[]
  destination_selection_mode?: DestinationSelectionMode
  date_range?: SearchDateRange
  trip_length_days?: number
  budget_range?: ClarificationBudgetRange
  date_flexibility?: DateFlexibility
  flight_preferences?: FlightPreferenceConstraints
  trip_style_tags?: string[]
  weather_preference?: WeatherPreference
  explicit_unknown_slots?: ClarificationSlot[]
}

export interface SearchRequest {
  query?: string
  inventory: InventoryType[]
  destination?: string
  origin?: string
  date_range?: SearchDateRange
  trip_length_days?: number
  budget_range?: ClarificationBudgetRange
  date_flexibility?: DateFlexibility
  flight_preferences?: FlightPreferenceConstraints
  trip_style_tags?: string[]
  destination_candidates?: string[]
  destination_selection_mode?: DestinationSelectionMode
  weather_preference?: WeatherPreference
  travelers: TravelerCounts
  stay_filters: StayFilters
  flight_filters: FlightFilters
  currency_code: string
  limit_per_provider: number
  clarification_answer?: ClarificationAnswer
  recap_edit?: ClarificationRecapEdit
  constraint_updates?: ConstraintUpdates
  clarification_state?: ClarificationState | null
}

export interface ProviderStatus {
  provider: string
  label: string
  configured: boolean
  healthy: boolean
  inventory_types: InventoryType[]
  reason?: string | null
}

export interface DegradedProvider {
  provider: string
  label: string
  reason: string
  inventory_types: InventoryType[]
}

export interface DegradedState {
  active: boolean
  inventory_types: InventoryType[]
  degraded_providers: DegradedProvider[]
}

export type NoFlightGuidanceCode =
  | 'missing_prerequisites'
  | 'provider_unavailable'
  | 'no_offers'
  | 'general_no_results'

export interface NoFlightGuidance {
  code: NoFlightGuidanceCode
  explanation: string
  actions: string[]
  provenance_unavailable: boolean
  freshness_unavailable: boolean
  fallback_attempts?: string[]
  follow_up_prompt?: string | null
}

export type ConversionStatus = 'native' | 'converted' | 'unavailable'
export type FreshnessSource = 'provider_quote' | 'provider_fetch' | 'cache_write'

export interface AirfareProvenance {
  source_provider: string | null
  provider_offer_id: string | null
  source_quote_at: string | null
  source_payload_ref: string | null
}

export interface AirfareFreshness {
  freshness_source: FreshnessSource | null
  freshness_at: string | null
  fetched_at: string | null
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
  duration: string | null
  price_minor: number | null
  currency_code: string | null
  duration_minutes: number | null
  stops_count: number | null
  normalized_offer_id: string | null
  provider_offer_id: string | null
  missing_fields: string[]
  conversion_status: ConversionStatus | null
  airfare_provenance: AirfareProvenance
  airfare_freshness: AirfareFreshness
}

export type SearchResult = StaySearchResult | FlightSearchResult

export interface SearchResponse {
  search_id: string
  query: string
  requested_inventory: InventoryType[]
  applied_filters: {
    destination?: string | null
    destination_candidates?: string[]
    destination_selection_mode?: DestinationSelectionMode | null
    origin?: string | null
    date_range?: SearchDateRange | null
    trip_length_days?: number | null
    budget_range?: ClarificationBudgetRange | null
    date_flexibility?: DateFlexibility | null
    flight_preferences?: FlightPreferenceConstraints | null
    trip_style_tags?: string[]
    weather_preference?: WeatherPreference | null
    travelers: TravelerCounts
    stay_filters: StayFilters
    flight_filters: FlightFilters
  }
  provider_status: ProviderStatus[]
  degraded_state?: DegradedState
  warnings: string[]
  results: SearchResult[]
  clarification_state?: ClarificationState | null
  no_flight_guidance?: NoFlightGuidance | null
  recommendation_packages?: RecommendationPackage[]
  flight_options?: FlightOptionsGroup | null
  lodging_options?: LodgingOptionsGroup | null
}

export interface OrchestratorTurnRequest {
  session_id: string
  message: string
  /** Optional typed search payload. When included, the backend executes the
   *  search path and returns typed search reliability metadata in search_response. */
  search_payload?: SearchRequest | null
}

export type OrchestratorResponseType = 'questions' | 'ideas' | 'packages' | 'itineraries'

export interface OrchestratorTurnResponse {
  session_id: string
  response_type: OrchestratorResponseType | string
  markdown: string
  open_questions: string[]
  candidate_destinations: Array<Record<string, unknown>>
  packages: Array<Record<string, unknown>>
  itineraries: Array<Record<string, unknown>>
  disclaimers: string[]
  executed_agents: string[]
  /** Typed search result including degraded_state and clarification_state.
   *  Only present when search_payload was included in the request. */
  search_response?: SearchResponse | null
}

export type ItineraryEstimateConfidence = 'low' | 'medium' | 'high'

export interface ItineraryCostEstimate {
  total_estimated: number
  flight_estimated: number
  stay_estimated: number
  car_estimated: number
  currency_code: string
  confidence: ItineraryEstimateConfidence
}

export interface ItineraryProposal {
  proposal_id: string
  destination: string
  destination_region_key: string
  travel_window: SearchDateRange
  duration_nights: number
  travelers: TravelerCounts
  needs_car: boolean
  cost_estimate: ItineraryCostEstimate
  rationale: string
  within_budget: boolean
  over_budget_note?: string | null
}

export interface ItineraryProposeRequest {
  query: string
  travelers?: TravelerCounts
  budget_range?: ClarificationBudgetRange
  candidate_destinations?: string[]
  travel_window?: SearchDateRange
  include_car?: boolean
  clarification_answer?: Record<string, unknown>
  currency_code?: string
}

export interface ItineraryProposeResponse {
  session_id: string
  proposals: ItineraryProposal[]
  clarification_state?: ClarificationState | null
  applied_inputs: Record<string, unknown>
  warnings: string[]
}

export interface ItineraryPriceRequest {
  proposal_id: string
  proposal_snapshot: ItineraryProposal
  travelers: TravelerCounts
  currency_code?: string
}

export interface ItineraryPriceResponse {
  search_id: string
  proposal_id: string
  flight_results: FlightSearchResult[]
  stay_results: StaySearchResult[]
  car_redirect_url?: string | null
  car_redirect_label?: string | null
  provider_status: ProviderStatus[]
  warnings: string[]
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

export async function proposeItinerary(
  payload: ItineraryProposeRequest
): Promise<ItineraryProposeResponse> {
  return request<ItineraryProposeResponse>('/itinerary/propose', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function priceItinerary(payload: ItineraryPriceRequest): Promise<ItineraryPriceResponse> {
  return request<ItineraryPriceResponse>('/itinerary/price', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export async function orchestratorTurn(
  payload: OrchestratorTurnRequest
): Promise<OrchestratorTurnResponse> {
  return request<OrchestratorTurnResponse>('/orchestrator/turn', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
