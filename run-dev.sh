#!/bin/bash

# This script sets up the development environment if necessary and starts both the React frontend and FastAPI backend concurrently.
# It creates a Python virtual environment for the backend (if not already present) and installs the required Node.js packages for the frontend.

set -e

# Function to check if a command exists
command_exists() {
  command -v "$1" >/dev/null 2>&1
}

# Setup backend environment
echo "\nSetting up backend environment..."

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
echo "\nSetting up frontend environment..."

if [ ! -d "frontend/node_modules" ] || [ ! -f "frontend/node_modules/.bin/react-scripts" ]; then
  echo "Installing Node.js packages for frontend..."
  cd frontend
  if ! command_exists npm; then
    echo "npm is not installed. Please install Node.js and npm."
    exit 1
  fi
  npm install
  cd ..
else
  echo "Frontend dependencies already installed."
fi

# Create .env file for React app if it doesn't exist.
if [ ! -f "frontend/.env" ]; then
  echo "REACT_APP_GOOGLE_MAPS_API_KEY=" > frontend/.env
  echo "Created .env file in frontend with empty REACT_APP_GOOGLE_MAPS_API_KEY."
fi

# Function to clean up background processes upon exit
function cleanup() {
  echo "\nShutting down development environment..."
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
echo "\nStarting FastAPI backend..."
cd backend
source venv/bin/activate
uvicorn soil:app --reload &
BACKEND_PID=$!
cd ..

# Start the frontend server
echo "\nStarting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Let the child processes run until interrupted
echo "\nDevelopment environment is running. Press Ctrl+C to stop."
wait

cleanup
