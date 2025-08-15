# Project Overview - Teacher Report Card Assistant

## Executive Summary
This is a **Teacher Report Card Assistant** system - a full-stack web application for Singapore primary schools to generate student report cards. The project is currently in the planning phase with comprehensive documentation but no implementation yet.

## Project Structure
```
report-card-assistant/
├── CLAUDE.md                      # Development guidelines for AI-assisted coding
├── context/
│   ├── brief/
│   │   └── assignment_brief.md    # Original take-home assignment requirements
│   ├── PRPs/
│   │   ├── EXAMPLE_multi_agent_prp.md  # Example PRP template
│   │   └── templates/
│   └── steering/
│       ├── requirements.md        # Detailed functional and technical requirements
│       └── system_design.md       # Comprehensive architecture and technical design
└── [To be implemented]
    ├── backend/                   # FastAPI backend with vertical slice architecture
    ├── frontend/                  # Next.js frontend with TypeScript
    └── docker-compose.yml         # Containerization configuration
```

## Project Purpose and Goals

### Primary Purpose
Enable teachers to efficiently create professional term report cards by reviewing student performance data, selecting achievements, and adding behavioral comments.

### Target Users
- **Form Teachers**: Can access and generate reports for students in their assigned classes
- **Year Heads**: Can access all students across all classes in their school
- **Scale**: 3 schools, ~120 teachers total

### Core Workflow
1. **Dashboard View**: Teachers see their accessible classes and student report statuses
2. **Student Selection**: Choose a student to generate report for
3. **Review Grades**: View current and previous term grades (read-only)
4. **Select Achievements**: Choose from auto-suggested achievements based on improvement patterns
5. **Add Comments**: Include behavioral observations and comments
6. **Generate PDF**: Create and download professional report card

## Key Files and Their Purposes

### Planning & Documentation Files

#### `CLAUDE.md`
- Development philosophy (KISS, YAGNI principles)
- Code structure guidelines (500 line file limit, 50 line function limit)
- Security best practices (RBAC, input validation, CSRF protection)
- Testing strategy (TDD, >80% coverage)
- Style guides for Python and TypeScript

#### `context/brief/assignment_brief.md`
- Original take-home assignment specifications
- 6-day implementation timeline
- Requirements for AI-assisted development workflow
- Deliverables and success criteria

#### `context/steering/requirements.md`
- Detailed functional requirements for both user roles
- Achievement auto-suggestion engine rules
- Performance band calculation logic
- Mock data specifications (3 schools, 12 students)
- Database schema outline

#### `context/steering/system_design.md`
- System architecture diagrams (Mermaid)
- User journey flows
- API endpoint specifications
- Service layer implementation details
- Security architecture
- Deployment configuration

## Technology Stack

### Backend Stack
- **Framework**: FastAPI (Python)
- **ORM**: SQLAlchemy
- **Validation**: Pydantic v2
- **Package Manager**: UV (fast Python package manager)
- **Testing**: pytest with coverage
- **Code Quality**: Ruff (linting & formatting), mypy (type checking)
- **Authentication**: JWT with 30-minute expiry
- **PDF Generation**: reportlab or weasyprint

### Frontend Stack
- **Framework**: Next.js 13+ (App Router)
- **Language**: TypeScript (strict mode)
- **Validation**: Zod schemas
- **Data Fetching**: SWR
- **Styling**: Tailwind CSS (expected)
- **Testing**: Jest, React Testing Library, Playwright (e2e)
- **Code Quality**: ESLint, Prettier

### Infrastructure
- **Database**: PostgreSQL 15
- **Migrations**: Alembic
- **Containerization**: Docker Compose
- **Environment Management**: Mise
- **Task Automation**: Justfile
- **Background Jobs**: FastAPI BackgroundTasks (upgradeable to Celery)

## Important Dependencies

### Backend Dependencies
```python
# Core
fastapi
uvicorn
sqlalchemy
alembic
pydantic-settings

# Security
passlib[bcrypt]
python-jose[cryptography]
python-multipart

# Testing
pytest
pytest-cov
pytest-asyncio

# Code Quality
ruff
mypy
```

### Frontend Dependencies
```json
{
  "dependencies": {
    "@next/auth": "latest",
    "zod": "latest",
    "swr": "latest",
    "react": "latest",
    "next": "latest"
  },
  "devDependencies": {
    "@types/node": "latest",
    "eslint-config-next": "latest",
    "typescript": "latest"
  }
}
```

## Important Configuration

### Environment Management
- **Mise**: Tool version management (.mise.toml)
  - Python 3.12
  - Node 20
  - UV latest

### Development Automation (Justfile)
```just
# Key commands
just dev          # Start both frontend and backend
just test         # Run all tests
just lint         # Lint and format all code
just build        # Build for production
```

### Security Configuration
- **RBAC**: Role-based access control for form teachers vs year heads
- **Multi-tenancy**: Complete school isolation
- **CSRF Protection**: Anti-CSRF tokens for state changes
- **Input Validation**: Server-side validation with Pydantic/Zod
- **SQL Security**: Parameterized queries via SQLAlchemy ORM

### Testing Strategy
- **Approach**: Test-Driven Development (TDD)
- **Coverage Target**: >80%
- **Test Types**: Unit, Integration, E2E, Security tests
- **Test Organization**: Tests live next to code (vertical slice)

## Architecture Highlights

### Design Pattern
**Modular Monolith** - Single deployable unit with clear service boundaries, designed for future microservices evolution.

### Service Boundaries
```
/app/services/
├── auth_service.py       # Authentication & Authorization
├── student_service.py    # Student data operations
├── report_service.py     # Report generation logic
├── achievement_service.py # Achievement suggestions
└── pdf_service.py        # PDF generation & export
```

### Data Flow
1. **Authentication Layer**: JWT-based with role validation
2. **API Gateway**: FastAPI routes with permission checks
3. **Service Layer**: Business logic with clear boundaries
4. **Data Layer**: PostgreSQL with multi-tenant isolation
5. **Background Tasks**: Async PDF generation

### Performance Requirements
- Dashboard load: <2 seconds
- Report generation: <5 seconds
- Concurrent user support
- Horizontal scaling ready

## Development Workflow

### Initial Setup
1. Clone repository
2. Set up environment with Mise
3. Configure .env file
4. Run database migrations
5. Seed mock data
6. Start development servers

### Development Cycle
1. Write tests first (TDD)
2. Implement feature
3. Run linting and formatting
4. Ensure tests pass
5. Check coverage
6. Document changes

### Deployment
- Single command: `docker-compose up`
- Three containers: frontend, backend, database
- Environment-specific configurations
- Health checks and monitoring ready

## Project Status
**Current Phase**: Planning and Documentation Complete
**Next Phase**: Implementation following the documented architecture and requirements
**Timeline**: 6-day implementation sprint

## Success Criteria
- [ ] Multi-tenant system with school isolation
- [ ] Role-based access control working correctly
- [ ] Achievement auto-suggestions based on grade improvements
- [ ] Professional PDF report generation
- [ ] All security requirements implemented
- [ ] >80% test coverage achieved
- [ ] Single-command deployment working
- [ ] Clean, AI-curated codebase without artifacts