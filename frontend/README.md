# dirt-io

`dirt-io` is a React-based mapping project with interactive overlays and custom polygon markers. This README helps developers get started quickly.

---

## Table of Contents

* [Getting Started](#getting-started)
* [Frontend Components](#frontend-components)
* [Environment Variables](#environment-variables)
* [Generating Documentation](#generating-documentation)
* [Tips for Developers](#tips-for-developers)
* [Quick Commands](#quick-commands)
* [Live App](#live-app)

---

## Getting Started

### 1. Clone the Repo

```bash
git clone <your-repo-url>
cd dirt-io
```

### 2. Frontend Setup (React App)

The frontend lives in `frontend`:

```bash
cd frontend
npm install        # install dependencies
npm start          # run development server
```

* App runs on `http://localhost:3000` by default.
* Live reloads automatically when files change.

---

## Frontend Components

| Component      | Location                      | Description                                                                     |
| -------------- | ----------------------------- | ------------------------------------------------------------------------------- |
| `MapControl`   | `src/components/MapControl`   | Central component for Google Maps integration; handles overlays and UI buttons. |
| `PolygonLayer` | `src/components/PolygonLayer` | Adds custom polygons to the map; can fetch polygon data via API.                |

> Use `MapControl` as the **single parent** for all overlays to centralize state.

---

## Environment Variables

Create a `.env` file in `frontend`:

```
REACT_APP_GOOGLE_MAPS_API_KEY=your_api_key_here
```

* Access in code: `process.env.REACT_APP_GOOGLE_MAPS_API_KEY`.
* **Important:** Do not commit `.env` files containing secrets.

---

## Generating Documentation

### JSDoc (vanilla JS / JSX)

```bash
cd frontend
npx jsdoc -c jsdoc.json
```

* HTML docs generated in `docs/`.
* Open `docs/index.html` in a browser to view component API.

### TypeDoc (for TypeScript / TSX)

```bash
npx typedoc --out docs src
```

* Fully supports TypeScript types and JSX components.
* Docs also generated in `docs/`.

> Links in README (if docs exist):

* [Frontend API Documentation](frontend/docs/index.html)

---

## Tips for Developers

* Keep **one `MapControl`** per map; all overlays should be children.
* Use `PolygonLayer` for custom polygon markers; future API calls can dynamically decide polygon shapes.
* Keep API keys in `.env`; never commit them.
* Build production frontend:

```bash
npm run build
```

* Deploy `build/` folder using static hosting or backend integration.

---

## Quick Commands

| Command                           | Description               |
| --------------------------------- | ------------------------- |
| `cd frontend && npm start` | Run frontend locally      |
| `npm run build`                   | Build production frontend |
| `npx jsdoc -c jsdoc.json`         | Generate HTML docs        |
| `npx typedoc --out docs src`      | Generate TypeScript docs  |

---

## Live App

If deployed (optional), add link here:

[View Live App](#)

> You can deploy with **Vercel**, **Netlify**, or **GitHub Pages**.
