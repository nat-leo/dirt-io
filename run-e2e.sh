#!/bin/bash

# Run Playwright end-to-end tests against the Next.js app.
# Starts the dev server (webpack, not Turbopack), waits for it to be ready,
# then runs Playwright tests under web/e2e.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WEB_DIR="$ROOT_DIR/web"
HOST="${HOST:-$(ipconfig getifaddr en0 || hostname -I | awk '{print $1}')}"
PORT="${PORT:-3000}"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

if ! command_exists npm; then
  echo "npm is required to run e2e tests." >&2
  exit 1
fi

cd "$WEB_DIR"

if [ ! -d node_modules ]; then
  echo "Installing web dependencies..."
  npm install
fi

if [ ! -d playwright ]; then
  echo "Installing Playwright browsers..."
  npx playwright install
fi

echo "Starting Next.js dev server on http://${HOST}:${PORT} ..."
NEXT_DISABLE_TURBOPACK=1 npm run dev -- --hostname "$HOST" --port "$PORT" >/tmp/next-dev.log 2>&1 &
DEV_PID=$!

cleanup() {
  echo "Stopping dev server..."
  if ps -p $DEV_PID >/dev/null 2>&1; then
    kill $DEV_PID
  fi
}
trap cleanup EXIT

# Wait for server to respond
for i in {1..30}; do
  if curl -sSf "http://${HOST}:${PORT}" >/dev/null 2>&1; then
    READY=1
    break
  fi
  sleep 1
done

if [ -z "${READY:-}" ]; then
  echo "Dev server did not start. Check /tmp/next-dev.log" >&2
  exit 1
fi

echo "Running Playwright tests..."
PLAYWRIGHT_BASE_URL="http://${HOST}:${PORT}" npx playwright test "$@"

echo "E2E tests completed."
