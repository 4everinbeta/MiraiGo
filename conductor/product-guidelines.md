# Product Guidelines: MiraiGo Travel Discovery

This document outlines the brand voice, user experience (UX) principles, and visual styling rules that govern MiraiGo Travel Discovery.

## 1. Brand Voice & Tone
* **Empathetic & Professional**: The travel assistant is helpful, encouraging, and clear. Responses must remain highly structured and focused on travel recommendations, avoiding unnecessary conversational fluff.
* **Informative & Transparent**: Always state data freshness, availability limits, or missing API credentials explicitly so the user knows exactly why certain routes (e.g. Duffel Flights) might be unavailable.

## 2. User Experience (UX) Principles
* **Graceful Degradation**:
  * Input is natural-language first. If APIs or live credentials (e.g. Duffel access tokens) are absent or down, the application must automatically degrade gracefully by serving beautiful, high-fidelity mock stays and flight recommendations accompanied by elegant, non-intrusive warning banners.
  * Never show blank pages or block the user from proceeding.
* **Interactive State Continuity**:
  * Interactive recap chips are displayed as soon as slots are extracted.
  * Users can edit slots (destination, origin, budget) directly at any point in the conversational flow, instantly triggering updated recommendations.
* **Accessibility First**:
  * Form inputs must be correctly labeled with explicit `htmlFor` and `id` tags.
  * Text contrast ratios on all elements (e.g., stay/flight status badges) must comply strictly with WCAG 2 AA guidelines (minimum contrast ratio of 4.5:1).

## 3. Visual Styling Rules & Aesthetics
* **Premium & Hybrid Theme**:
  * Combine modern **Glassmorphism** (backdrop-blur overlays, semi-transparent white/sakura headers, and soft border highlights) with organic background elements (radial gradients and sumi/sakura color palettes).
  * Use **Micro-animations** (smooth hover scaling on stay/flight cards, loading states, and elegant transition effects) to make the application feel responsive and premium.
  * Maintain clean, readable density using **Flat & Dense Minimalist** layouts for results to maximize information scannability without cluttering the screen.
