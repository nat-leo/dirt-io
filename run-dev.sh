#!/bin/bash

# This script sets up the development environment if necessary and starts both the React frontend and FastAPI backend concurrently.
# It creates a Python virtual environment for the backend (if not already present) and installs the required Node.js packages for the frontend.

set -e

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Load nvm if available but not already on PATH
if ! command_exists nvm; then
  export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
  if [ -s "$NVM_DIR/nvm.sh" ]; then
    . "$NVM_DIR/nvm.sh"
  fi
fi

# Prefer latest Node.js 22.x via nvm; install if missing.
if command_exists nvm; then
  LATEST_22=$(nvm ls 22 --no-colors 2>/dev/null | grep -oE 'v22[0-9.]+' | sort -V | tail -n1)
  if [ -z "$LATEST_22" ]; then
    echo "Node.js 22 not installed in nvm; installing latest 22.x..."
    nvm install 22 >/dev/null 2>&1
    LATEST_22=$(nvm ls 22 --no-colors 2>/dev/null | grep -oE 'v22[0-9.]+' | sort -V | tail -n1)
  fi
  if [ -n "$LATEST_22" ]; then
    echo "Using Node.js $LATEST_22 via nvm..."
    nvm use "$LATEST_22" >/dev/null 2>&1
  else
    echo "Could not install Node.js 22; using current node $(node -v)"
  fi
else
  echo "nvm not found; using system node $(node -v)"
fi

# Setup backend environment
echo
echo "Setting up backend environment..."

if [ ! -d "backend/venv" ]; then
  echo "Creating Python virtual environment in backend/venv ..."
  cd backend
  if ! command_exists python3; then
    echo "python3 is not installed. Please install Python 3."
    exit 1
  fi
  python3 -m venv venv
  echo "Activating virtual environment and installing requirements..."
  source venv/bin/activate
  if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
  else
    echo "No requirements.txt found in backend. Skipping dependency installation."
  fi
  deactivate
  cd ..
else
  echo "Backend virtual environment already exists."
fi

# Setup frontend environment
echo
echo "Setting up web environment..."

if [ ! -d "web/node_modules" ] || [ ! -f "web/node_modules/.bin/react-scripts" ]; then
  echo "Installing Node.js packages for web..."
  cd web
  if ! command_exists npm; then
    echo "npm is not installed. Please install Node.js and npm."
    exit 1
  fi
  npm install
  cd ..
else
  echo "Web dependencies already installed."
fi

# Function to clean up background processes upon exit
function cleanup() {
  echo
  echo "Shutting down development environment..."
  if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
  fi
  if [ -n "$FRONTEND_PID" ]; then
    kill $FRONTEND_PID 2>/dev/null || true
  fi
  exit 0
}

trap cleanup SIGINT SIGTERM

# Start the backend server
echo
echo "Starting FastAPI backend..."
export FASTAPI_BASE_URL=http://localhost:8000
cd backend
source venv/bin/activate
uvicorn soil:app --reload &
BACKEND_PID=$!
cd ..

# Start the frontend server
echo
echo "Starting React frontend..."
export NEXT_PUBLIC_API_BASE_URL=$FASTAPI_BASE_URL
cd web
NEXT_DISABLE_TURBOPACK=1 npm run dev &
FRONTEND_PID=$!
cd ..

# Start the Storybook server
# STORYBOOK SERVER NEEDS NODE VERSION 20 OR 22! (November 17, 2025)
echo
echo "Starting Storybook..."
cd web
rm -rf node_modules/.cache/storybook
npm run storybook &
FRONTEND_PID=$!
cd ..

# Let the child processes run until interrupted
echo
echo "Development environment is running. Press Ctrl+C to stop."
wait

cleanup
