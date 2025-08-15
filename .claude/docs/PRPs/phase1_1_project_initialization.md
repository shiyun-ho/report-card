name: "Phase 1.1 - Project Initialization"
description: |
  Set up the complete monorepo structure for the Teacher Report Card Assistant system with FastAPI backend, 
  Next.js 13+ frontend with shadcn/ui, PostgreSQL database, and Docker Compose orchestration.

## Purpose
Initialize a production-ready monorepo with proper structure, configuration, and tooling for a multi-tenant report card generation system for Singapore primary schools.

## System Requirements

### Minimum Requirements
- **OS**: Linux, macOS, or Windows (with WSL2)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for Docker images and development
- **CPU**: 2 cores minimum, 4 cores recommended

### Required Software
- **Docker**: v20.10+ (for containerization)
- **Docker Compose**: v2.0+ (for orchestration)
- **Node.js**: v18+ (for Next.js frontend)
- **npm**: v8+ (for package management)
- **Git**: v2.0+ (for version control)

### Optional but Recommended
- **Just**: v1.0+ (for task automation)
- **Python**: v3.9+ (for local backend development)

### Network Requirements
- Ports 3000, 8000, and 5432 must be available
- Internet connection for downloading packages and Docker images

## Core Principles
1. **Module-Based Architecture**: Use domain/module structure for FastAPI, not file-type structure
2. **App Router First**: Use Next.js 13+ App Router with React Server Components
3. **Type Safety**: TypeScript frontend, Pydantic backend
4. **Developer Experience**: Hot reload, type checking, linting, formatting
5. **Container-First**: Everything runs in Docker for consistency

---

## Goal
Create a fully configured monorepo with:
- FastAPI backend with modular structure
- Next.js 13+ frontend with shadcn/ui components
- PostgreSQL database container
- Docker Compose orchestration
- Justfile task automation
- Proper environment configuration

## Why
- **Consistency**: Docker ensures same environment across all developers
- **Scalability**: Module-based structure supports growth
- **Type Safety**: Catch errors early with TypeScript and Pydantic
- **Developer Experience**: Fast iteration with hot reload and automation

## What
A working development environment where `docker-compose up` starts all services with hot reload, and developers can immediately begin implementing features.

### Success Criteria
- [ ] All prerequisites installed and verified
- [ ] Required ports (3000, 8000, 5432) are available
- [ ] Docker daemon is running and accessible
- [ ] `docker-compose up` starts all services successfully
- [ ] Backend accessible at http://localhost:8000 with auto-reload
- [ ] Frontend accessible at http://localhost:3000 with hot reload
- [ ] PostgreSQL accessible on port 5432
- [ ] shadcn/ui components installed and working
- [ ] Justfile commands execute properly
- [ ] Environment variables properly configured

## All Needed Context

### Documentation & References
```yaml
# MUST READ - Core Documentation
- url: https://fastapi.tiangolo.com/tutorial/bigger-applications/
  why: FastAPI module structure for larger applications

- url: https://github.com/zhanymkanov/fastapi-best-practices
  why: Production FastAPI patterns and structure

- url: https://ui.shadcn.com/docs/installation/next
  why: Official shadcn/ui Next.js installation guide

- url: https://github.com/Nneji123/fastapi-nextjs
  why: Working example of FastAPI + Next.js + PostgreSQL + Docker

- url: https://github.com/zhanymkanov/fastapi_production_template/blob/main/justfile
  why: Production-ready Justfile examples

- url: https://fastapi.tiangolo.com/deployment/docker/
  why: FastAPI Docker best practices

- url: https://github.com/casey/just
  why: Justfile syntax and features
```

### Target Directory Structure
```bash
report-card-assistant/
├── backend/
│   ├── src/
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py              # FastAPI app entry point
│   │       ├── core/
│   │       │   ├── __init__.py
│   │       │   ├── config.py        # Settings with pydantic-settings
│   │       │   ├── database.py      # Database connection
│   │       │   └── security.py      # Security utilities
│   │       ├── models/
│   │       │   ├── __init__.py
│   │       │   └── base.py          # SQLAlchemy base
│   │       ├── api/
│   │       │   ├── __init__.py
│   │       │   └── v1/
│   │       │       ├── __init__.py
│   │       │       └── api.py       # API router aggregation
│   │       └── services/
│   │           └── __init__.py
│   ├── tests/
│   │   └── __init__.py
│   ├── alembic.ini
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   └── globals.css
│   │   ├── components/
│   │   │   └── ui/              # shadcn/ui components
│   │   ├── lib/
│   │   │   └── utils.ts
│   │   └── types/
│   │       └── index.ts
│   ├── public/
│   ├── package.json
│   ├── tsconfig.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── components.json          # shadcn/ui config
│   ├── Dockerfile
│   └── .env.local.example
├── docker-compose.yml
├── justfile
├── .env.example
├── .gitignore
└── README.md
```

### Known Gotchas & Solutions
```python
# CRITICAL: FastAPI async route blocking - use synchronous routes for blocking operations
# CRITICAL: Next.js 13+ requires 'use client' directive for client components
# CRITICAL: Docker networking - services communicate via service names, not localhost
# CRITICAL: PostgreSQL ready check - backend must wait for DB to be ready
# CRITICAL: shadcn/ui requires Tailwind CSS and specific postcss config
# CRITICAL: Environment variables - Next.js needs NEXT_PUBLIC_ prefix for client-side vars
# CRITICAL: Hot reload in Docker requires proper volume mounting
# CRITICAL: Alembic migrations need proper database URL configuration
```

## Implementation Blueprint

### Backend Structure (FastAPI)
```python
# backend/src/app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.v1.api import api_router

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    
    # CORS middleware for Next.js frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:3000"],  # Next.js dev server
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app

app = create_application()
```

### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER:-reportcard}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB:-reportcard_db}
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER:-reportcard}"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
      PYTHONUNBUFFERED: 1
    volumes:
      - ./backend:/app
    depends_on:
      postgres:
        condition: service_healthy
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      NEXT_PUBLIC_API_URL: http://localhost:8000/api/v1
    volumes:
      - ./frontend/src:/app/src
      - ./frontend/public:/app/public
    depends_on:
      - backend
    command: npm run dev

volumes:
  postgres_data:
```

### Justfile Configuration
```makefile
# justfile
# Show available commands
default:
    @just --list

# Install all dependencies
install:
    cd backend && pip install -r requirements.txt
    cd frontend && npm install

# Start all services
up:
    docker-compose up

# Start services in background
up-d:
    docker-compose up -d

# Stop all services
down:
    docker-compose down

# View logs
logs service="":
    #!/bin/bash
    if [ -z "{{service}}" ]; then
        docker-compose logs -f
    else
        docker-compose logs -f {{service}}
    fi

# Backend specific commands
backend-shell:
    docker-compose exec backend bash

backend-test:
    docker-compose exec backend pytest

backend-lint:
    docker-compose exec backend ruff check src/

backend-format:
    docker-compose exec backend ruff format src/

# Frontend specific commands
frontend-shell:
    docker-compose exec frontend sh

frontend-build:
    docker-compose exec frontend npm run build

frontend-lint:
    docker-compose exec frontend npm run lint

# Database commands
db-shell:
    docker-compose exec postgres psql -U reportcard -d reportcard_db

db-migrate:
    docker-compose exec backend alembic upgrade head

db-makemigrations message:
    docker-compose exec backend alembic revision --autogenerate -m "{{message}}"

# Clean everything
clean:
    docker-compose down -v
    find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
    find . -type d -name ".next" -exec rm -r {} + 2>/dev/null || true

# Rebuild containers
rebuild:
    docker-compose build --no-cache

# Full reset and restart
reset: down clean install rebuild up
```

## Prerequisites Check

### Required Software
Before starting implementation, verify all required tools are installed:

```bash
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
            version=$($version_cmd 2>&1)
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
check_command "docker" "20.10" "docker --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1"
check_command "docker-compose" "2.0" "docker-compose --version | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1"
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
check_command "python3" "3.9" "python3 --version | grep -oE '[0-9]+\.[0-9]+'"

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
check_command "git" "2.0" "git --version | grep -oE '[0-9]+\.[0-9]+'"

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
```

### Manual Prerequisites Installation

If the script reports missing prerequisites, install them:

#### Docker & Docker Compose
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install docker.io docker-compose
sudo systemctl start docker
sudo usermod -aG docker $USER
# Logout and login again

# macOS
# Download and install Docker Desktop from https://www.docker.com/products/docker-desktop

# Windows
# Download and install Docker Desktop from https://www.docker.com/products/docker-desktop
# Ensure WSL2 is enabled
```

#### Node.js & npm
```bash
# Using Node Version Manager (recommended)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 20
nvm use 20

# Or direct installation
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# macOS
brew install node
```

#### Just (Task Runner)
```bash
# macOS
brew install just

# Linux/Windows - Using cargo
cargo install just

# Or download pre-built binary
wget https://github.com/casey/just/releases/download/1.16.0/just-1.16.0-x86_64-unknown-linux-musl.tar.gz
tar xvf just-1.16.0-x86_64-unknown-linux-musl.tar.gz
sudo mv just /usr/local/bin/
```

### Quick Start After Prerequisites
Once all prerequisites are installed, you can verify everything works:

```bash
# Run the prerequisites check again
bash check_prerequisites.sh

# If all green, create a test Docker container
docker run hello-world

# Test Docker Compose
echo "version: '3.8'
services:
  test:
    image: alpine
    command: echo 'Docker Compose works!'" > test-compose.yml
docker-compose -f test-compose.yml up
docker-compose -f test-compose.yml down
rm test-compose.yml
```

## List of Implementation Tasks

```yaml
Task 0: Verify Prerequisites
COMMANDS:
  # Save and run the prerequisites check script
  cat > check_prerequisites.sh << 'EOF'
  [INSERT SCRIPT FROM ABOVE]
  EOF
  chmod +x check_prerequisites.sh
  ./check_prerequisites.sh
  
EXPECTED:
  All required tools installed and accessible
  All required ports available
  Docker daemon running

Task 1: Create Project Root Structure
COMMANDS:
  mkdir -p report-card-assistant/{backend,frontend}
  cd report-card-assistant
  
FILES TO CREATE:
  - .gitignore (Python, Node, IDE files)
  - README.md (Project overview)
  - .env.example (All environment variables)

Task 2: Initialize Backend Structure
COMMANDS:
  cd backend
  mkdir -p src/app/{core,models,api/v1,services} tests
  touch src/app/__init__.py
  
FILES TO CREATE:
  - requirements.txt:
    fastapi==0.109.0
    uvicorn[standard]==0.27.0
    sqlalchemy==2.0.25
    psycopg2-binary==2.9.9
    alembic==1.13.1
    pydantic==2.5.3
    pydantic-settings==2.1.0
    python-multipart==0.0.6
    passlib[bcrypt]==1.7.4
    pytest==7.4.4
    pytest-asyncio==0.23.3
    httpx==0.26.0
    ruff==0.1.14
    
  - Dockerfile:
    FROM python:3.11-slim
    WORKDIR /app
    COPY requirements.txt .
    RUN pip install --no-cache-dir -r requirements.txt
    COPY . .
    EXPOSE 8000
    CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

Task 3: Create FastAPI Application
CREATE src/app/main.py:
  - FastAPI app with CORS middleware
  - Health check endpoint
  - Router includes

CREATE src/app/core/config.py:
  - Pydantic Settings class
  - Environment variable loading
  - Database URL construction

CREATE src/app/core/database.py:
  - SQLAlchemy engine setup
  - Session management
  - Database dependency

Task 4: Initialize Frontend with Next.js
COMMANDS:
  cd frontend
  npx create-next-app@latest . --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"
  
MODIFY package.json scripts:
  "dev": "next dev",
  "build": "next build",
  "start": "next start",
  "lint": "next lint",
  "format": "prettier --write ."

Task 5: Install and Configure shadcn/ui
COMMANDS:
  cd frontend
  npx shadcn-ui@latest init
  
PROMPTS TO ANSWER:
  - Style: Default
  - Base color: Slate
  - CSS variables: Yes
  
ADD INITIAL COMPONENTS:
  npx shadcn-ui@latest add button card input label

Task 6: Create Frontend Docker Configuration
CREATE frontend/Dockerfile:
  FROM node:20-alpine
  WORKDIR /app
  COPY package*.json ./
  RUN npm ci
  COPY . .
  EXPOSE 3000
  CMD ["npm", "run", "dev"]

CREATE frontend/.env.local.example:
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

Task 7: Setup Alembic for Database Migrations
COMMANDS:
  cd backend
  alembic init alembic
  
MODIFY alembic.ini:
  - Set sqlalchemy.url from environment variable
  
MODIFY alembic/env.py:
  - Import models
  - Set target_metadata
  - Load database URL from environment

Task 8: Create Docker Compose Configuration
CREATE docker-compose.yml:
  - PostgreSQL service with health check
  - Backend service with volume mount
  - Frontend service with volume mount
  - Proper depends_on configuration
  - Environment variable injection

Task 9: Create Project Automation
CREATE justfile:
  - All commands from blueprint
  - Proper shell script blocks
  - Service-specific commands

Task 10: Final Configuration Files
CREATE .env.example:
  # Database
  POSTGRES_USER=reportcard
  POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
  POSTGRES_DB=reportcard_db
  DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@postgres:5432/${POSTGRES_DB}
  
  # Backend
  SECRET_KEY=${SECRET_KEY}
  API_V1_STR=/api/v1
  PROJECT_NAME="Report Card Assistant"
  
  # Frontend
  NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1

CREATE .gitignore:
  # Python
  __pycache__/
  *.py[cod]
  .pytest_cache/
  .env
  venv/
  
  # Node
  node_modules/
  .next/
  out/
  .env.local
  
  # IDE
  .vscode/
  .idea/
  
  # Docker
  postgres_data/
```

## Validation Loop

### Level 0: Prerequisites Validation
```bash
# Run prerequisites check
./check_prerequisites.sh
# Expected: All green checkmarks, no red X marks

# If any prerequisites missing, stop and install them first
# The script will exit with code 1 if prerequisites aren't met
if [ $? -ne 0 ]; then
    echo "Please install missing prerequisites before continuing"
    exit 1
fi
```

### Level 1: Structure Verification
```bash
# Verify directory structure
find . -type d -name "src" | head -5
# Expected: ./backend/src, ./frontend/src

# Check all init files exist
find . -name "__init__.py" | wc -l
# Expected: At least 5 files

# Verify Docker files
ls -la */Dockerfile docker-compose.yml
# Expected: All files present
```

### Level 2: Docker Build Test
```bash
# Build all containers
docker-compose build
# Expected: All images build successfully

# Test individual services
docker-compose run --rm backend python -c "from app.main import app; print('Backend OK')"
# Expected: "Backend OK"

docker-compose run --rm frontend npm --version
# Expected: npm version number
```

### Level 3: Service Startup Test
```bash
# Start all services
docker-compose up -d

# Wait for services
sleep 10

# Test backend health
curl http://localhost:8000/health
# Expected: {"status":"healthy"}

# Test frontend
curl -I http://localhost:3000
# Expected: HTTP/1.1 200 OK

# Test database connection
docker-compose exec postgres pg_isready
# Expected: accepting connections

# Clean up
docker-compose down
```

### Level 4: Hot Reload Verification
```bash
# Start services
docker-compose up -d

# Modify backend
echo '# Test comment' >> backend/src/app/main.py

# Check backend logs for reload
docker-compose logs backend | grep -i reload
# Expected: "Reloading" message

# Modify frontend
echo '// Test comment' >> frontend/src/app/page.tsx

# Check frontend compilation
docker-compose logs frontend | grep -i compiled
# Expected: "Compiled" message

docker-compose down
```

### Level 5: Justfile Commands
```bash
# Test just commands
just --list
# Expected: List of all commands

just up-d
sleep 10

just backend-shell << EOF
python -c "import fastapi; print('FastAPI OK')"
exit
EOF
# Expected: "FastAPI OK"

just db-shell << EOF
\l
\q
EOF
# Expected: List of databases including reportcard_db

just down
```

## Final Validation Checklist
- [ ] All services start with `docker-compose up`
- [ ] Backend responds at http://localhost:8000/health
- [ ] Frontend loads at http://localhost:3000
- [ ] PostgreSQL accepts connections
- [ ] Hot reload works for both frontend and backend
- [ ] Justfile commands execute successfully
- [ ] shadcn/ui components render properly
- [ ] Environment variables load correctly
- [ ] No error messages in any service logs
- [ ] Git ignores appropriate files

---

## Anti-Patterns to Avoid
- ❌ Don't use file-type structure for FastAPI (routers/, models/, schemas/)
- ❌ Don't forget CORS configuration for frontend-backend communication
- ❌ Don't hardcode database URLs or secrets
- ❌ Don't use Pages Router for Next.js - use App Router
- ❌ Don't forget health checks in docker-compose
- ❌ Don't mount node_modules as a volume
- ❌ Don't use sync database operations in async FastAPI routes
- ❌ Don't forget to wait for postgres to be ready

## Common Issues & Solutions

### Issue: Backend can't connect to PostgreSQL
**Solution**: Use service name 'postgres' not 'localhost' in DATABASE_URL within Docker

### Issue: Frontend can't reach backend API
**Solution**: Use http://localhost:8000 for client-side, service names for server-side

### Issue: Hot reload not working
**Solution**: Ensure volumes are mounted correctly and WATCHPACK_POLLING=true for Next.js

### Issue: Permission errors in Docker
**Solution**: Use consistent UID/GID or run containers as non-root user

### Issue: shadcn/ui components not styling
**Solution**: Ensure tailwind.config.ts includes "./src/components/**/*.{ts,tsx}"

## Confidence Score: 9/10

High confidence due to:
- Comprehensive documentation and examples available
- Clear structure based on production patterns
- Well-tested Docker Compose configuration
- Standard tooling (FastAPI, Next.js, PostgreSQL)
- Detailed validation steps

Minor uncertainty:
- Exact shadcn/ui component requirements may need adjustment
- Alembic configuration might need tweaking for specific model structure