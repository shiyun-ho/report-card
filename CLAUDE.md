# CLAUDE.md

This file provides comprehensive guidance to Claude Code when working with the Teacher Report Card Assistant project, covering both Python FastAPI backend and Next.js TypeScript frontend.

## 🚨 CRITICAL: Always Reference Security Policy and Learnings

**BEFORE starting any task, ALWAYS consult:**

1. **Security Policy**: `@.claude/docs/context/steering/SECURITY.md` - Contains mandatory security requirements including:
   - Environment variable management (NEVER hardcode credentials)
   - Docker Compose security patterns  
   - Production deployment checklists
   - Credential generation procedures

2. **Project Learnings**: `@.claude/docs/learnings/` - Contains lessons from previous tasks:
   - Docker-first development patterns
   - Environment consistency requirements
   - Error resolution strategies
   - Security compliance patterns

**Any deviation from security policies or learnings must be explicitly justified and documented.**

## Core Development Philosophy

### KISS (Keep It Simple, Stupid)

Simplicity should be a key goal in design. Choose straightforward solutions over complex ones whenever possible. Simple solutions are easier to understand, maintain, and debug.

### YAGNI (You Aren't Gonna Need It)

Avoid building functionality on speculation. Implement features only when they are needed, not when you anticipate they might be useful in the future.

### Design Principles

- **Dependency Inversion**: High-level modules should not depend on low-level modules. Both should depend on abstractions.
- **Open/Closed Principle**: Software entities should be open for extension but closed for modification.
- **Single Responsibility**: Each function, class, and module should have one clear purpose.
- **Fail Fast**: Check for potential errors early and raise exceptions immediately when issues occur.

## 🏗️ Project Structure

### Full-Stack Architecture

```
report-card-assistant/
├── backend/                    # FastAPI backend
│   ├── src/
│   │   └── app/
│   │       ├── __init__.py
│   │       ├── main.py
│   │       ├── core/           # Core functionality
│   │       ├── models/         # SQLAlchemy models
│   │       ├── api/            # API routes
│   │       └── services/       # Business logic
│   ├── alembic/                # Database migrations
│   ├── tests/                  # Backend tests
│   ├── pyproject.toml         # UV dependencies
│   ├── uv.lock                 # Lock file
│   ├── Dockerfile              # Backend container
│   └── justfile                # Backend automation
├── frontend/                   # Next.js frontend
│   ├── src/
│   │   ├── app/                # App router pages
│   │   ├── components/         # React components
│   │   ├── lib/                # Utilities
│   │   └── types/              # TypeScript types
│   ├── package.json            # Node dependencies
│   ├── tsconfig.json           # TypeScript config
│   ├── next.config.js          # Next.js config
│   ├── Dockerfile              # Frontend container
│   └── justfile                # Frontend automation
├── docker-compose.yml          # Docker orchestration
├── docker-compose.override.yml # Development overrides
├── .mise.toml                  # Environment management
├── justfile                    # Root automation
├── .env.example                # Environment template
├── check_prerequisites.sh      # Prerequisites check
└── README.md                   # Project documentation
```

### Backend Code Structure

Module-based architecture (not file-type based):

```
src/app/
    __init__.py
    main.py              # FastAPI application entry

    # Core modules
    core/
        __init__.py
        config.py        # Settings management
        database.py      # Database connection
        security.py      # Authentication & security
    
    # Data models
    models/
        __init__.py
        base.py          # Base model class
        user.py          # User model
        student.py       # Student model
        report_card.py   # Report card model
    
    # API routes
    api/
        __init__.py
        v1/
            __init__.py
            api.py       # Route aggregation
            auth.py      # Auth endpoints
            users.py     # User endpoints
            students.py  # Student endpoints
            reports.py   # Report endpoints
    
    # Business logic
    services/
        __init__.py
        auth_service.py
        report_service.py
        ai_service.py
    
    # Utilities
    utils/
        __init__.py
        validators.py
        formatters.py
```

### Frontend Code Structure

```
src/
├── app/                        # Next.js 13+ app router
│   ├── layout.tsx
│   ├── page.tsx
│   ├── globals.css
│   ├── (auth)/
│   │   ├── login/
│   │   └── register/
│   └── api/
│       └── auth/
├── components/
│   ├── ui/                     # Reusable UI components
│   ├── forms/                  # Form components
│   ├── layout/                 # Layout components
│   └── __tests__/
├── lib/
│   ├── utils.ts               # Utility functions
│   ├── api.ts                 # API client
│   ├── auth.ts                # Auth utilities
│   └── validations.ts         # Zod schemas
├── types/
│   ├── api.ts                 # API response types
│   ├── auth.ts                # Auth types
│   └── global.ts              # Global types
└── hooks/
    ├── useAuth.ts
    └── useApi.ts
```

## 🧱 Code Structure & Modularity

### File and Function Limits

- **Never create a file longer than 500 lines of code**. If approaching this limit, refactor by splitting into modules.
- **Functions should be under 50 lines** with a single, clear responsibility.
- **Classes should be under 100 lines** and represent a single concept or entity.
- **Organize code into clearly separated modules**, grouped by feature or responsibility.
- **Line length should be max 100 characters** for Python (ruff rule in pyproject.toml) and max 120 characters for TypeScript (ESLint rule).
- **Docker-First Development**: Always use Docker containers for execution following patterns from `@.claude/docs/learnings/`

## 🛠️ Development Environment

### MANDATORY: Docker-First Development Patterns

**ALL development MUST follow Docker-first patterns from `@.claude/docs/learnings/`**

Critical patterns from learnings:
- **Environment Consistency**: Use Docker containers over host tools for execution
- **Network Discovery**: `docker network ls | grep project-name` to find networks
- **Container Execution**: Proper user context (`--user root` when needed) and path config
- **Environment Files**: Always use `--env-file .env.development` for container execution
- **Security Compliance**: Never expose credentials in command line history

### Mise Environment Management

Use mise for managing multiple tool versions across the project:

```toml
# .mise.toml
[tools]
python = "3.12"
node = "20"
uv = "latest"

[env]
DATABASE_URL = "postgresql://localhost:5432/myapp"
NEXTAUTH_URL = "http://localhost:3000"
```

```bash
# Install tools defined in .mise.toml
mise install

# Use mise shell integration
mise use
```

### Backend Development with UV in Docker

**CRITICAL: All UV operations MUST use Docker containers per security policy and learnings.**

Docker-first UV usage (following `@.claude/docs/learnings/` patterns):

```bash
# ✅ CORRECT: Docker execution with environment files
docker run --rm --env-file .env.development --network PROJECT_network --user root PROJECT_backend bash -c "
  export PYTHONPATH=/app/src &&
  cd /app &&
  uv sync
"

# ✅ CORRECT: Add packages via Docker
docker run --rm --env-file .env.development --network PROJECT_network --user root PROJECT_backend bash -c "
  cd /app &&
  uv add requests
"

# ❌ WRONG: Host UV execution (violates Docker-first patterns)
uv run python script.py  # Never use host UV

# ❌ WRONG: Explicit credentials (security violation) 
DATABASE_URL=postgresql://... uv run python  # Never expose credentials
```

**Package Management Rules:**
- **NEVER UPDATE DEPENDENCIES DIRECTLY IN pyproject.toml** 
- **ALWAYS USE `uv add` via Docker**
- **ALWAYS use environment files, never explicit credentials**

### Frontend Development with NPM

```bash
# Install dependencies
npm install

# Add dependencies
npm install @next/auth zod

# Add development dependencies
npm install --save-dev @types/node eslint-config-next

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm test
```

### Just Commands

Use justfile for project automation:

#### Root justfile
```just
# Show available commands
default:
    @just --list

# Install all dependencies
install:
    cd backend && uv sync
    cd frontend && npm install

# Start development servers
dev:
    just dev-backend &
    just dev-frontend

# Start backend development server
dev-backend:
    cd backend && uv run uvicorn src.project.main:app --reload --host 0.0.0.0 --port 8000

# Start frontend development server
dev-frontend:
    cd frontend && npm run dev

# Run all tests
test:
    just test-backend
    just test-frontend

# Run backend tests
test-backend:
    cd backend && uv run pytest

# Run frontend tests
test-frontend:
    cd frontend && npm test

# Lint and format all code
lint:
    just lint-backend
    just lint-frontend

# Lint backend
lint-backend:
    cd backend && uv run ruff check .
    cd backend && uv run ruff format .
    cd backend && uv run mypy src/

# Lint frontend
lint-frontend:
    cd frontend && npm run lint
    cd frontend && npm run format

# Build production
build:
    cd backend && uv build
    cd frontend && npm run build

# Clean all build artifacts
clean:
    cd backend && rm -rf dist/ .pytest_cache/ __pycache__/
    cd frontend && rm -rf .next/ out/
```

#### Backend justfile
```just
# Backend-specific commands
set working-directory := justfile_directory()

# Run development server
dev:
    uv run uvicorn src.project.main:app --reload --host 0.0.0.0 --port 8000

# Run tests with coverage
test:
    uv run pytest --cov=src --cov-report=html

# Format and lint code
lint:
    uv run ruff format .
    uv run ruff check --fix .
    uv run mypy src/

# Database migrations
migrate:
    uv run alembic upgrade head

# Create new migration
migration name:
    uv run alembic revision --autogenerate -m "{{name}}"
```

### Development Commands

#### Backend Commands (Docker-First)

**CRITICAL: All commands MUST use Docker following learnings patterns**

```bash
# ✅ CORRECT: Docker execution with environment files
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)

# Run all tests
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && uv run pytest
"

# Run specific tests with verbose output
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && uv run pytest tests/test_module.py -v
"

# Format code
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  cd /app && uv run ruff format .
"

# Check linting  
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  cd /app && uv run ruff check .
"

# ❌ WRONG: Host execution (violates Docker-first patterns)
uv run pytest  # Never run directly on host
```

#### Frontend Commands
```bash
# Run development server
npm run dev

# Run tests
npm test

# Run tests in watch mode
npm run test:watch

# Run linting
npm run lint

# Fix linting issues
npm run lint:fix

# Format code
npm run format

# Type checking
npm run type-check

# Build for production
npm run build
```

## 📋 Style & Conventions

### Python Style Guide

- **Follow PEP8** with these specific choices:
  - Line length: 100 characters (set by Ruff in pyproject.toml)
  - Use double quotes for strings
  - Use trailing commas in multi-line structures
- **Always use type hints** for function signatures and class attributes
- **Format with `ruff format`** (faster alternative to Black)
- **Use `pydantic` v2** for data validation and settings management

### TypeScript Style Guide

- **Follow strict TypeScript configuration** with these choices:
  - Line length: 120 characters (ESLint rule)
  - Use single quotes for strings
  - Use trailing commas in multi-line structures
  - Prefer explicit return types for functions
  - Use `const` assertions where appropriate
- **Always use TypeScript strict mode**
- **Prefer type over interface** for simple types
- **Use interface for extensible object shapes**
- **Use Zod for runtime validation**

### Docstring Standards

#### Python (Google-style)
Use Google-style docstrings for all public functions, classes, and modules:

```python
def calculate_discount(
    price: Decimal,
    discount_percent: float,
    min_amount: Decimal = Decimal("0.01")
) -> Decimal:
    """
    Calculate the discounted price for a product.

    Args:
        price: Original price of the product
        discount_percent: Discount percentage (0-100)
        min_amount: Minimum allowed final price

    Returns:
        Final price after applying discount

    Raises:
        ValueError: If discount_percent is not between 0 and 100
        ValueError: If final price would be below min_amount

    Example:
        >>> calculate_discount(Decimal("100"), 20)
        Decimal('80.00')
    """
```

#### TypeScript (JSDoc)
Use JSDoc comments for complex functions and public APIs:

```typescript
/**
 * Validates user input and returns normalized data
 * 
 * @param input - Raw user input to validate
 * @param schema - Zod schema for validation
 * @returns Promise resolving to validated data
 * @throws ValidationError when input is invalid
 * 
 * @example
 * ```typescript
 * const result = await validateInput(userInput, userSchema);
 * ```
 */
```

### Naming Conventions

#### Python
- **Variables and functions**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private attributes/methods**: `_leading_underscore`
- **Type aliases**: `PascalCase`
- **Enum values**: `UPPER_SNAKE_CASE`

#### TypeScript
- **Variables and functions**: `camelCase`
- **Classes and interfaces**: `PascalCase`
- **Types**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private properties**: `#private` or `_private`
- **File names**: `kebab-case.ts` or `PascalCase.tsx` for components
- **Component files**: `PascalCase.tsx`

## 🧪 Testing Strategy

### Test-Driven Development (TDD)

1. **Write the test first** - Define expected behavior before implementation
2. **Watch it fail** - Ensure the test actually tests something
3. **Write minimal code** - Just enough to make the test pass
4. **Refactor** - Improve code while keeping tests green
5. **Repeat** - One test at a time

### Test Organization

- **Backend**: Unit tests, integration tests, end-to-end tests
- **Frontend**: Component tests, integration tests, e2e tests with Playwright
- Keep test files next to the code they test
- Use `conftest.py` (Python) and `jest.setup.js` (TypeScript) for shared configuration

## 🔒 Security Best Practices

### MANDATORY: Follow Security Policy

**ALL security implementations MUST follow `@.claude/docs/context/steering/SECURITY.md`.**

Key requirements from security policy:
- **Environment Variables**: Use `.env.development` for local development, `.env` for production
- **Never commit credentials**: Only `.env.example` and `.env.development` are safe to commit
- **Docker Security**: Use environment variables, no hardcoded values in docker-compose.yml
- **Credential Generation**: Use `openssl rand -hex 32` for production keys
- **Deployment Checklist**: Must complete all security checks before deployment

### General Security Guidelines

- **Never commit secrets** - ALWAYS use environment files as specified in security policy
- Keep dependencies updated regularly using `uv` for Python and `npm audit` for Node.js
- Implement proper logging and monitoring for security events
- Use HTTPS for all external communications
- Follow principle of least privilege for all system access

### RBAC (Role-Based Access Control) Prevention

**Design secure authorization from the ground up:**
- Define roles and permissions explicitly in your data model
- Never rely solely on client-side role checking
- Implement server-side authorization checks at every API endpoint
- Use middleware to enforce role-based access consistently
- Audit and log all authorization decisions
- Regularly review and update role definitions
- Test authorization logic thoroughly with different user roles
- Consider using established frameworks like Casbin for complex RBAC scenarios

### Input Validation

**Validate all user input rigorously:**
- Use Pydantic for Python backend validation and Zod for TypeScript frontend validation
- Validate data types, formats, lengths, and ranges
- Sanitize input to prevent injection attacks
- Use allowlists rather than blocklists where possible
- Validate file uploads carefully (type, size, content)
- Never trust data from external sources including APIs
- Implement both client-side and server-side validation
- Use parameterized queries for all database operations

### Safe SQL Practices

**Prevent SQL injection and ensure data integrity:**
- Always use parameterized queries or prepared statements
- Never concatenate user input directly into SQL strings
- Use ORM query builders when possible (SQLAlchemy for Python)
- Implement proper database connection pooling and timeout handling
- Use database transactions appropriately
- Validate and sanitize all data before database operations
- Implement database-level constraints and validation
- Regularly audit database queries for security vulnerabilities
- Use principle of least privilege for database user accounts

### CSRF Protection

**Implement comprehensive CSRF protection:**
- Use CSRF tokens for all state-changing operations
- Implement SameSite cookie attributes properly
- Validate Origin and Referer headers where appropriate
- Use double-submit cookie pattern for additional protection
- Implement proper CORS configuration
- Never use GET requests for state-changing operations
- For SPAs, use proper authentication headers instead of cookies where possible
- Regularly test CSRF protection mechanisms

### Backend Security Implementation

```python
from passlib.context import CryptContext
import secrets

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def generate_secure_token(length: int = 32) -> str:
    """Generate a cryptographically secure random token."""
    return secrets.token_urlsafe(length)
```

### Frontend Security Considerations

- Implement Content Security Policy (CSP) headers
- Use secure HTTP headers (HSTS, X-Frame-Options, etc.)
- Sanitize user input before rendering
- Use secure session management
- Implement proper authentication token handling
- Validate API responses before processing
- Use environment variables for configuration
- Implement proper error handling that doesn't leak sensitive information

## 🚨 Error Handling

### Backend Exception Handling

```python
# Create custom exceptions for your domain
class PaymentError(Exception):
    """Base exception for payment-related errors."""
    pass

class InsufficientFundsError(PaymentError):
    """Raised when account has insufficient funds."""
    def __init__(self, required: Decimal, available: Decimal):
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient funds: required {required}, available {available}"
        )

# Use specific exception handling
try:
    process_payment(amount)
except InsufficientFundsError as e:
    logger.warning(f"Payment failed: {e}")
    return PaymentResult(success=False, reason="insufficient_funds")
except PaymentError as e:
    logger.error(f"Payment error: {e}")
    return PaymentResult(success=False, reason="payment_error")
```

### Frontend Error Handling

```typescript
// Custom error types
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public code?: string
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

// Error boundary for React components
export class ErrorBoundary extends Component<
  { children: ReactNode },
  { hasError: boolean }
> {
  constructor(props: { children: ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(): { hasError: boolean } {
    return { hasError: true }
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error boundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return <ErrorFallback />
    }

    return this.props.children
  }
}
```

## 🔧 Configuration Management

### Backend Settings (Python)

```python
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with validation."""
    app_name: str = "MyApp"
    debug: bool = False
    database_url: str
    redis_url: str = "redis://localhost:6379"
    api_key: str
    max_connections: int = 100

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()

# Usage
settings = get_settings()
```

### Frontend Configuration (TypeScript)

```typescript
// lib/config.ts
interface AppConfig {
  apiUrl: string
  authUrl: string
  environment: 'development' | 'staging' | 'production'
  features: {
    analytics: boolean
    debugMode: boolean
  }
}

export const config: AppConfig = {
  apiUrl: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  authUrl: process.env.NEXT_PUBLIC_AUTH_URL || 'http://localhost:8000/auth',
  environment: (process.env.NODE_ENV as AppConfig['environment']) || 'development',
  features: {
    analytics: process.env.NEXT_PUBLIC_ENABLE_ANALYTICS === 'true',
    debugMode: process.env.NODE_ENV === 'development',
  },
}
```

## 📱 TypeScript Best Practices

### Type Safety and Strict Configuration

- Always use TypeScript in strict mode with all strict flags enabled
- Prefer `unknown` over `any` when type is uncertain
- Use type guards for runtime type checking
- Leverage discriminated unions for complex state management
- Use `const` assertions for immutable data
- Prefer type-only imports when importing only for types

