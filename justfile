# Teacher Report Card Assistant - Project Automation

# Show available commands
default:
    @just --list

# Install all dependencies
install:
    @echo "Installing backend dependencies..."
    cd backend && uv sync
    @echo "Installing frontend dependencies..."
    cd frontend && npm install
    @echo "✅ All dependencies installed successfully!"

# Start development servers
dev:
    @echo "Starting development environment with Docker Compose..."
    docker compose up

# Start backend development server (without Docker)
dev-backend:
    cd backend && uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend development server (without Docker)
dev-frontend:
    cd frontend && npm run dev

# Run all tests
test:
    @echo "Running backend tests..."
    just test-backend
    @echo "Running frontend tests..."
    just test-frontend
    @echo "✅ All tests completed!"

# Run backend tests
test-backend:
    cd backend && uv run pytest

# Run frontend tests
test-frontend:
    cd frontend && npm test

# Lint and format all code
lint:
    @echo "Linting backend..."
    just lint-backend
    @echo "Linting frontend..."
    just lint-frontend
    @echo "✅ All linting completed!"

# Lint backend
lint-backend:
    cd backend && uv run ruff check .
    cd backend && uv run ruff format .
    cd backend && uv run mypy src/

# Lint frontend
lint-frontend:
    cd frontend && npm run lint
    cd frontend && npm run format

# Build for production
build:
    @echo "Building backend..."
    cd backend && uv build
    @echo "Building frontend..."
    cd frontend && npm run build
    @echo "✅ Build completed!"

# Database operations
db-upgrade:
    cd backend && uv run alembic upgrade head

db-downgrade:
    cd backend && uv run alembic downgrade -1

db-migration name:
    cd backend && uv run alembic revision --autogenerate -m "{{name}}"

db-reset:
    docker compose down -v
    docker compose up -d db
    sleep 5
    just db-upgrade
    @echo "✅ Database reset completed!"

# Docker operations
docker-build:
    docker compose build

docker-up:
    docker compose up -d

docker-down:
    docker compose down

docker-logs:
    docker compose logs -f

docker-clean:
    docker compose down -v
    docker system prune -f

# Clean all build artifacts
clean:
    @echo "Cleaning backend artifacts..."
    cd backend && rm -rf dist/ .pytest_cache/ **/__pycache__/
    @echo "Cleaning frontend artifacts..."
    cd frontend && rm -rf .next/ out/ node_modules/.cache/
    @echo "✅ Clean completed!"

# Setup project from scratch
setup:
    @echo "Setting up project..."
    just install
    docker compose build
    docker compose up -d db
    sleep 5
    just db-upgrade
    @echo "✅ Project setup completed! Run 'just dev' to start developing."

# Health check
health:
    @echo "Checking services health..."
    @curl -f http://localhost:8000/health || echo "❌ Backend is not running"
    @curl -f http://localhost:3000 || echo "❌ Frontend is not running"
    @docker compose ps

# View logs for specific service
logs service="":
    #!/usr/bin/env bash
    if [ -z "{{service}}" ]; then
        docker compose logs -f
    else
        docker compose logs -f {{service}}
    fi

# Execute command in container
exec service cmd:
    docker compose exec {{service}} {{cmd}}

# Format all code
format:
    just lint-backend
    just lint-frontend
    @echo "✅ All code formatted!"

# Check if pre-requisites are installed
check:
    @./check_prerequisites.sh