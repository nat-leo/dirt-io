# Web client

This Next.js 16 app renders a Deck.GL/MapLibre map that overlays NRCS USDA soil polygons retrieved from the backend. The map ships with an API client context that lets you swap between the live FastAPI service and the mock client used for Storybook, Playwright, and offline demos.

## Local setup

1. `cd web`
2. Install dependencies with `npm install`.
3. Create or adapt any `.env` values using the environment variables described below before starting the dev server.

## Environment variables

- `FASTAPI_BASE_URL` / `NEXT_PUBLIC_API_BASE_URL`: base URL for backend requests (defaults to relative URLs within the Next.js app).
- `NEXT_PUBLIC_API_MODE`: set to `mock` to force `mockApiClient`; otherwise `realApiClient` hits the configured backend service.
- `PLAYWRIGHT_BASE_URL`: point Playwright at an existing deployment instead of launching the bundled dev server (`NEXT_PUBLIC_API_MODE=mock pnpm dev`).

## Scripts (`npm run <script>`)

- `dev`: `next dev` – run the app locally with fast refresh.
- `build`: `next build` – compile the production bundle and validate routes.
- `start`: `next start` – serve the optimized build.
- `lint`: `eslint .` – lint the app and Storybook stories.
- `storybook`: launch Storybook on port 6006 for isolated component work (the `Map` story shows viewport-based polygon queries).
- `build-storybook`: prebuild Storybook for hosting or sharing.

Additional tooling:

- `npx playwright test`: run the Playwright suites under `tests/` against `NEXT_PUBLIC_API_MODE=mock pnpm dev` (or against `PLAYWRIGHT_BASE_URL` if set).

## App structure

- `app/page.tsx` composes the centered starter layout and renders `<Map />`.
- `app/components/Map.tsx` relies on `react-map-gl/maplibre` and MapLibre basemaps, throttles viewport events, caps the request area to ~10,000 km², and paints the GeoJSON via `Source`/`Layer`.
- `app/components/apiClientContext.tsx` swaps between `realApiClient` (`lib/api.ts`) and `mockApiClient` (`lib/api.mock.ts`) depending on `NEXT_PUBLIC_API_MODE`.
- Shared helpers/types live in `lib/definitions.ts`, `lib/utils.ts`, and `lib/areaSymbols.server.ts` (the latter proxies backend area symbols during server renders).

## Testing and verification

1. Run `npm run dev` (set `NEXT_PUBLIC_API_MODE=mock` for offline prototypes).
2. Execute `npm run lint`.
3. Run `npx playwright test` (traces are recorded on first retries per `playwright.config.ts`).
4. Use `npm run storybook` to preview the `Map` story with mock data.

When you have a backend ready, set `NEXT_PUBLIC_API_MODE=real` and configure `FASTAPI_BASE_URL` to surface live `/map` data in the running app.
