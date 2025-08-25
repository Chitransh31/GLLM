#!/bin/bash

# G-code Generator Startup Script
# This script starts both the backend API and frontend React app

echo "🚀 Starting G-code Generator Application..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null
}

# Function to start backend
start_backend() {
    echo -e "${YELLOW}Starting FastAPI backend...${NC}"
    cd backend
    
    # Check if requirements are installed
    if ! pip show fastapi >/dev/null 2>&1; then
        echo -e "${YELLOW}Installing Python dependencies...${NC}"
        pip install -r requirements.txt
    fi
    
    # Start backend in background
    python main.py &
    BACKEND_PID=$!
    echo -e "${GREEN}Backend started with PID: $BACKEND_PID${NC}"
    
    # Wait for backend to be ready
    echo "Waiting for backend to start..."
    sleep 5
    
    cd ..
}

# Function to start frontend
start_frontend() {
    echo -e "${YELLOW}Starting React frontend...${NC}"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
        npm install
    fi
    
    # Start frontend
    npm start &
    FRONTEND_PID=$!
    echo -e "${GREEN}Frontend started with PID: $FRONTEND_PID${NC}"
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${RED}Shutting down services...${NC}"
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "Backend stopped"
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "Frontend stopped"
    fi
    exit 0
}

# Set up signal handling
trap cleanup SIGINT SIGTERM

# Check if ports are already in use
if check_port 8000; then
    echo -e "${RED}Port 8000 is already in use. Please stop the existing service.${NC}"
    exit 1
fi

if check_port 3000; then
    echo -e "${RED}Port 3000 is already in use. Please stop the existing service.${NC}"
    exit 1
fi

# Start services
start_backend
start_frontend

echo -e "${GREEN}✅ Application started successfully!${NC}"
echo -e "Backend API: ${GREEN}http://localhost:8000${NC}"
echo -e "Frontend App: ${GREEN}http://localhost:3000${NC}"
echo -e "API Documentation: ${GREEN}http://localhost:8000/docs${NC}"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"

# Wait for processes
wait
