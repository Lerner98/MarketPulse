#!/bin/bash
# MarketPulse Development Environment Setup Script
# This script sets up the complete development environment

set -e  # Exit on error

echo "🚀 MarketPulse Development Environment Setup"
echo "=============================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Python $(python3 --version)"

# Check Node.js
if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 18+${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Node.js $(node --version)"

# Check npm
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} npm $(npm --version)"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker Desktop${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker $(docker --version)"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose not found. Please install Docker Compose${NC}"
    exit 1
fi
echo -e "${GREEN}✓${NC} Docker Compose $(docker-compose --version)"

echo ""
echo "📦 Installing Python dependencies..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null || {
    echo -e "${RED}❌ Failed to activate virtual environment${NC}"
    exit 1
}

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Install pre-commit
pip install pre-commit
echo ""
echo "🔧 Setting up pre-commit hooks..."
pre-commit install
echo -e "${GREEN}✓${NC} Pre-commit hooks installed"

echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..
echo -e "${GREEN}✓${NC} Frontend dependencies installed"

echo ""
echo "🐳 Starting Docker services..."
docker-compose up -d postgres redis

# Wait for services to be healthy
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if services are running
if docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${GREEN}✓${NC} PostgreSQL is running"
else
    echo -e "${YELLOW}⚠️  PostgreSQL may not be ready yet${NC}"
fi

if docker-compose ps | grep -q "redis.*Up"; then
    echo -e "${GREEN}✓${NC} Redis is running"
else
    echo -e "${YELLOW}⚠️  Redis may not be ready yet${NC}"
fi

echo ""
echo "🧪 Running tests to verify setup..."

# Backend tests
echo "Testing backend..."
if pytest backend/tests/unit -v --tb=short -q; then
    echo -e "${GREEN}✓${NC} Backend tests passed"
else
    echo -e "${YELLOW}⚠️  Some backend tests failed (this might be expected on first run)${NC}"
fi

# Frontend tests
echo "Testing frontend..."
cd frontend
if npm test -- --run --reporter=basic; then
    echo -e "${GREEN}✓${NC} Frontend tests passed"
else
    echo -e "${YELLOW}⚠️  Some frontend tests failed (this might be expected on first run)${NC}"
fi
cd ..

echo ""
echo "=============================================="
echo -e "${GREEN}✅ Development environment setup complete!${NC}"
echo "=============================================="
echo ""
echo "📚 Next steps:"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate  # Linux/Mac"
echo "   venv\\Scripts\\activate     # Windows"
echo ""
echo "2. Start the backend (in a new terminal):"
echo "   cd backend"
echo "   uvicorn api.main:app --reload"
echo ""
echo "3. Start the frontend (in another terminal):"
echo "   cd frontend"
echo "   npm run dev"
echo ""
echo "4. Access the application:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📖 Read CONTRIBUTING.md for development workflow"
echo "📖 Read docs/CI_CD_BEST_PRACTICES.md for testing strategy"
echo ""
echo "Happy coding! 🚀"
