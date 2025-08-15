#!/bin/bash
# Prerequisites verification script

echo "========================================="
echo "Checking Prerequisites for Project Setup"
echo "========================================="
echo ""

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PREREQUISITES_MET=true

# Function to check if a command exists
check_command() {
    local cmd=$1
    local min_version=$2
    local version_cmd=$3
    
    if command -v $cmd &> /dev/null; then
        if [ -n "$version_cmd" ]; then
            version=$($version_cmd 2>&1 | head -1)
            echo -e "${GREEN}✓${NC} $cmd found: $version"
        else
            echo -e "${GREEN}✓${NC} $cmd found"
        fi
    else
        echo -e "${RED}✗${NC} $cmd NOT found - Required!"
        PREREQUISITES_MET=false
        return 1
    fi
}

# Function to check Docker service
check_docker_running() {
    if docker info &> /dev/null; then
        echo -e "${GREEN}✓${NC} Docker daemon is running"
    else
        echo -e "${YELLOW}⚠${NC} Docker daemon is not running - Please start Docker"
        echo "  Try: sudo systemctl start docker (Linux) or open Docker Desktop (Mac/Windows)"
        PREREQUISITES_MET=false
    fi
}

# Function to check port availability
check_port() {
    local port=$1
    local service=$2
    
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠${NC} Port $port is in use (needed for $service)"
        echo "  Run: lsof -i :$port to see what's using it"
        PREREQUISITES_MET=false
    else
        echo -e "${GREEN}✓${NC} Port $port is available for $service"
    fi
}

echo "1. Checking Core Requirements:"
echo "------------------------------"

# Docker and Docker Compose
check_command "docker" "20.10" "docker --version"

# Check for docker compose v2 (as a docker plugin)
if docker compose version &> /dev/null; then
    echo -e "${GREEN}✓${NC} docker compose found (v2): $(docker compose version)"
elif command -v docker-compose &> /dev/null; then
    echo -e "${GREEN}✓${NC} docker-compose found (v1): $(docker-compose --version)"
else
    echo -e "${RED}✗${NC} docker compose NOT found - Required!"
    echo "  Docker Compose v2 is now integrated into Docker"
    echo "  Install Docker Desktop for the easiest setup"
    PREREQUISITES_MET=false
fi

check_docker_running

# Node.js and npm
echo ""
echo "2. Checking Node.js Tools:"
echo "-------------------------"
check_command "node" "18.0" "node --version"
check_command "npm" "8.0" "npm --version"
check_command "npx" "" "npx --version"

# Python (optional, for local development)
echo ""
echo "3. Checking Python (Optional for local dev):"
echo "-------------------------------------------"
check_command "python3" "3.9" "python3 --version"

# Just (task runner)
echo ""
echo "4. Checking Task Runner:"
echo "-----------------------"
if ! command -v just &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} 'just' command not found (optional but recommended)"
    echo "  Install with: cargo install just"
    echo "  Or: brew install just (Mac)"
    echo "  Or: Download from https://github.com/casey/just/releases"
else
    check_command "just" "" "just --version"
fi

# Git
echo ""
echo "5. Checking Version Control:"
echo "---------------------------"
check_command "git" "2.0" "git --version"

# Check required ports
echo ""
echo "6. Checking Port Availability:"
echo "-----------------------------"
check_port 3000 "Next.js frontend"
check_port 8000 "FastAPI backend"
check_port 5432 "PostgreSQL database"

# Check disk space
echo ""
echo "7. Checking Disk Space:"
echo "----------------------"
available_space=$(df -h . | awk 'NR==2 {print $4}')
echo -e "${GREEN}✓${NC} Available disk space: $available_space"
echo "  (Recommended: At least 2GB for Docker images and development)"

# Docker permissions check (Linux only)
echo ""
echo "8. Checking Docker Permissions:"
echo "------------------------------"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if groups | grep -q docker; then
        echo -e "${GREEN}✓${NC} Current user is in docker group"
    else
        echo -e "${YELLOW}⚠${NC} Current user is not in docker group"
        echo "  Add with: sudo usermod -aG docker $USER"
        echo "  Then logout and login again"
    fi
else
    echo -e "${GREEN}✓${NC} Not on Linux, Docker Desktop handles permissions"
fi

# Final summary
echo ""
echo "========================================="
if [ "$PREREQUISITES_MET" = true ]; then
    echo -e "${GREEN}✓ All required prerequisites are met!${NC}"
    echo "You can proceed with the implementation."
else
    echo -e "${RED}✗ Some prerequisites are missing!${NC}"
    echo "Please install missing requirements before proceeding."
    echo ""
    echo "Quick installation guide:"
    echo "------------------------"
    echo "Docker: https://docs.docker.com/get-docker/"
    echo "Node.js: https://nodejs.org/ (LTS version recommended)"
    echo "Just: https://github.com/casey/just#installation"
    exit 1
fi
echo "========================================="