---
name: ui-ux-dashboard
description: Frontend specialist for the Next.js dashboard. Use for pages, components, layout, dark theme tokens, shadcn/ui usage, Recharts visualisations, data fetching with TanStack Query, generated OpenAPI types, loading/empty/error/pagination states, responsiveness and accessibility.
when_to_use: Triggers on "page", "component", "dashboard", "chart", "UI", "frontend", "Tailwind", "shadcn", "Recharts", "responsive", "dark mode".
paths: "frontend/**"
---

# UI/UX Dashboard

Source of truth: `docs/SYSTEM_ARCHITECTURE.md § Frontend` (page list → endpoints) and `docs/API_SPECIFICATION.md`.

## Design direction
- Dark-first: background `#0B0D0C`, surface `#151917`, border `#232A26`, text `#E6EBE8` / muted `#8A948F`, one accent green (`#3DDC84`, hover `#2FBF6F`). Status colours only for status (rising = green, declining = muted red, warn = amber).
- Typography: Geist/Inter; numbers in `tabular-nums`. Dense but calm cards; clear hierarchy (one primary metric per card).
- Avoid the generic "AI dashboard" look: no gradient blobs, no glassmorphism, no emoji headers, no rainbow charts.
- Charts (Recharts): one accent series plus neutral greys, labelled axes, tooltips with exact values, no 3D or pie charts with more than 5 slices.

## Execution
1. Confirm the endpoint exists (`/api/v1/openapi.json`) and regenerate types (`pnpm gen:api`). **Never build UI for an endpoint that doesn't exist.**
2. Use shadcn/ui primitives (Card, Table, Tabs, Badge, Dialog, Skeleton, Toast) before writing custom ones.
3. Every data view ships with: skeleton loading, empty state (what to do next), error state (retry), pagination (cursor), and filters in URL search params.
4. Show a red "MOCK DATA" banner whenever any item has `source === "mock"`.
5. Show score explanations with a "Why is this trending?" popover rendering `score_breakdown`.
6. Test with Vitest + Testing Library; add/extend the Playwright smoke for new pages.

## Constraints
- **No non-functional buttons.** If the backend action doesn't exist yet, don't render the control.
- No new UI libraries beyond Next.js, Tailwind, shadcn/ui, Recharts, TanStack Query, lucide-react without an ADR.
- No hand-written API types. No API keys in the browser.
- Render Reddit text as text or sanitised markdown, never `dangerouslySetInnerHTML`.
- Accessibility: keyboard reachable, visible focus ring (accent), contrast ≥ 4.5:1, `aria-label` on icon buttons. Lighthouse a11y ≥ 90.
- Responsive from 360 px; tables collapse to cards on mobile.

## Examples
- *"Build the Trend Explorer."* → `app/trends/page.tsx` server component loads the first page; client `TrendTable` uses TanStack Query with `region`, `category`, `status` and `sort` search params; Indian/Global nav items link to `?region=IN|GLOBAL` (ADR-012).
- *"Add a category distribution chart."* → horizontal bar chart (not a pie), top 8 categories plus "other", accent for the selected category.
