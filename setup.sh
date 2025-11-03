#!/bin/bash

# Moplexity Setup Script
# This script sets up Moplexity for local development

set -e

echo "🚀 Setting up Moplexity..."
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.11 or higher.${NC}"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 18 or higher.${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Python found: $(python3 --version)${NC}"
echo -e "${GREEN}✓ Node.js found: $(node --version)${NC}"
echo ""

# Setup Backend
echo "📦 Setting up backend..."
cd backend

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo -e "${YELLOW}Creating .env file from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠️  Please edit backend/.env and add your API keys${NC}"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

# Setup Frontend
cd ../frontend
echo "📦 Setting up frontend..."

# Install Node dependencies
echo "Installing Node dependencies..."
npm install

echo -e "${GREEN}✓ Frontend setup complete${NC}"
echo ""

# Initialize database
cd ../backend
echo "🗄️  Initializing database..."
# The database will be created automatically when the backend starts

echo ""
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "To start Moplexity:"
echo ""
echo "Option 1 - Using Docker (recommended):"
echo "  docker-compose up --build"
echo ""
echo "Option 2 - Local development:"
echo "  Terminal 1 (Backend):"
echo "    cd backend"
echo "    source venv/bin/activate"
echo "    uvicorn app.main:app --reload"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "Then open: http://localhost:5173 (local) or http://localhost:3000 (Docker)"
echo ""
echo -e "${YELLOW}⚠️  Don't forget to configure your API keys in:${NC}"
echo "  - Backend: backend/.env"
echo "  - Frontend: Settings page (http://localhost:5173/settings)"
echo ""

