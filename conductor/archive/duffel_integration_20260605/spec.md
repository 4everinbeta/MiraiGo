# Specification: Duffel Flight Provider Integration

## 1. Overview
The goal of this track is to refine and fully integrate the Duffel flight provider. Currently, the search workflow uses basic configurations and can trigger fallback warnings due to missing or unmapped fields. This work will complete the data mapping, introduce robust error and timeout handling, and enable persistence and configuration checks.

## 2. Functional Requirements
* **Complete Data Mapping**: 
  - Ensure `price_minor`, `currency_code`, `duration_minutes`, and `stops_count` are correctly parsed and mapped from Duffel API responses to prevent automatic legacy fallbacks.
* **Error Handling & Fallbacks**:
  - Implement retry logic with backoff for Duffel request timeouts.
  - Gracefully handle missing Duffel API tokens by surfacing the `degraded_state` and structured `no_flight_guidance` to the frontend orchestrator.
* **Credentials & Configuration**:
  - Wire Duffel configuration checks through environment variables and ensure the health status is accurately reported by the provider status endpoints.
  
## 3. Acceptance Criteria
* **No Warning Regression**: Duffel searches do not default to using legacy airfare fields when healthy.
* **Graceful Degradation**: If Duffel credentials are missing or the API is down, mock flights are served and a clear degraded warning is returned.
* **Test Verification**: Pytest unit/integration tests cover Duffel provider configurations, data mapping, and failure states.

## 4. Out of Scope (v1)
* Stays provider changes or UI dashboard redesigns.
