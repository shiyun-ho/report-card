# Teacher Report Card Assistant

A multi-tenant report card generation system for mid-sized school groups (3 schools, ~120 teachers), enabling teachers to efficiently review student performance and generate professional term report cards.

## 🎬 Demo

<!-- TODO: Add demo video/gif here -->
![Demo Video Placeholder](docs/report-card.gif)

## 📚 Project Documentation

- **[🤖 AI Development Documentation](docs/AI_DEVELOPMENT_DOCUMENTATION.md)** - Comprehensive guide to the AI-assisted development workflow, prompt engineering strategies, and lessons learned
- **[🧪 Testing Guide](docs/TESTING.md)** - Complete testing strategy with validation commands and results

## 🎯 Assignment Overview

This system fulfills the take-home assignment requirements by allowing teachers to:

1. **Review student performance**: Recent performance data, notes, and achievements from multiple sources
2. **Record grades**: Core subjects (Math, English, Science, Chinese) with behavior comments and performance bands  
3. **Auto-suggest achievements**: AI-powered suggestions from shared achievement database with quick inclusion/exclusion
4. **Generate & export**: Professional, printable PDF report cards for selected terms

### Core Pages
- **Dashboard**: View all students and overall states
- **Report Generation**: Complete workflow for creating individual student reports

## 🏗️ Stack Overview & Key Decisions

### Technology Choices
- **Backend API**: Python 3.12 + FastAPI (fast development, excellent docs, type safety)
- **Frontend UI**: Next.js 15 + TypeScript (modern React patterns, full-stack capabilities)  
- **Database**: PostgreSQL 15 (ACID compliance, excellent JSON support for flexible data)
- **Containerization**: Docker Compose (simple deployment, environment consistency)

### Architecture Decisions
- **Multi-tenant**: Single database with school_id isolation (simpler than per-tenant DBs)
- **Session-based auth**: Better UX than JWT for web app (automatic renewal, secure httpOnly cookies)
- **Monorepo structure**: Backend + Frontend in single repo (easier development coordination)
- **Service layer pattern**: Clean separation between API routes and business logic

## 🚀 Setup/Run Instructions

### Prerequisites
- **Docker** and **Docker Compose** (v2.0+)
- **Git** for cloning the repository

### Quick Start (Recommended)
```bash
# 1. Clone and enter directory
git clone <repository-url>
cd report-card

# 2. Set up environment (first time only)
cp .env.example .env.development
# Edit .env.development with your credentials (or use defaults for development)

# 3. Start all services (builds automatically)
docker compose up --build

# 4. Access the application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000/docs
# Database: localhost:5432
```

That's it! The system will:
- Build all Docker images  
- Start PostgreSQL database
- **Automatically seed sample data** (3 schools, 12 teachers, 36 students)
- Start backend API server
- Start frontend development server

**🔧 Environment Configuration**: 
- Copy `.env.example` to `.env` and update with your credentials
- For development: You can use the default values in `.env.development`
- For production: Generate secure keys using `openssl rand -hex 32`

### Test Credentials
Use these credentials to test different roles across all schools:

#### **Form Teachers** (Can see assigned class students only)
- **Riverside Primary**: `tan@rps.edu.sg` / `dev_password_123`
- **Hillview Primary**: `wong@hps.edu.sg` / `dev_password_123`  
- **Eastwood Primary**: `chen@eps.edu.sg` / `dev_password_123`

#### **Year Heads** (Can see all students in their school)
- **Riverside Primary**: `lim@rps.edu.sg` / `dev_password_123`
- **Hillview Primary**: `kumar@hps.edu.sg` / `dev_password_123`
- **Eastwood Primary**: `lee@eps.edu.sg` / `dev_password_123`

```bash
**Note:** The above credentials are for locally seeded database only. 
They are provided solely for assessment/testing locally and are not accessibly in other environments.
```

## 🔒 Code Security

### Role-Based Access Control (RBAC)
- **Form Teachers**: Can only see students in their assigned classes
- **Year Heads**: Can see all students in their school  
- **Multi-tenant isolation**: Schools cannot access other schools' data

### Security Implementation
- **Input validation**: Pydantic (backend) and Zod (frontend) for data validation
- **Safe SQL**: SQLAlchemy ORM prevents SQL injection attacks
- **CSRF protection**: Secure tokens for state-changing operations
- **Session security**: httpOnly cookies with configurable expiry
- **Password hashing**: bcrypt with secure salt rounds

### Data Protection
- Environment variable isolation for sensitive configuration
- Container security with minimal attack surfaces
- Database connection pooling with proper limits

## 📊 Database Schema

### Core Tables
- **Schools**: Multi-tenant isolation with school-specific data
- **Users**: Teachers with role-based permissions (form_teacher, year_head)
- **Students**: Student records linked to schools and classes
- **Classes**: Class organization within schools
- **Terms**: Academic term management
- **Grades**: Subject grades linked to students and terms
- **Achievements**: Suggestion system for student accomplishments

### Key Relationships
```
Schools (1) → (N) Users, Students, Classes, Terms
Students (1) → (N) Grades  
Classes (1) → (N) Students
Terms × Students → Grades (many-to-many through grades table)
```

### Multi-tenant Architecture
All data queries include `school_id` filtering to ensure complete data isolation between schools.

## 🌐 API Contract

### Authentication Endpoints
- `POST /api/v1/auth/login` - User login with email/password
- `POST /api/v1/auth/logout` - Session logout
- `GET /api/v1/auth/me` - Get current user info

### Core Data Endpoints
- `GET /api/v1/students` - List students (filtered by role/assignments)
- `GET /api/v1/students/{id}` - Get student details with RBAC
- `GET /api/v1/grades/students/{id}/terms/{term_id}` - Get student grades for term
- `GET /api/v1/achievements/suggest/{student_id}/{term_id}` - AI achievement suggestions

### Report Generation
- `POST /api/v1/reports/generate/{student_id}/{term_id}` - Generate PDF report

### Multi-tenant Security
All endpoints automatically filter data by the authenticated user's school_id, ensuring complete isolation.

## 🧪 How to Run Tests

### Quick Test Validation (One Command)
```bash
# Run all core tests (28 tests total - integration workflows + achievement AI)
docker run --rm --env-file .env.development --network report-card-assistant_report-card-network --user root report-card-assistant-backend bash -c "export PYTHONPATH=/app/src && cd /app && uv run pytest tests/test_integration_workflow.py tests/test_achievement_service.py -v"
```

**Expected Result**: ✅ **28/28 tests passing** - validates complete assignment functionality

### What This Validates
- **Multi-tenant RBAC**: Form teachers vs year heads access control across 3 schools
- **Complete User Workflows**: Dashboard → Student Selection → Report Generation → PDF Download  
- **Security**: Authentication, authorization, cross-school access prevention
- **AI Features**: Achievement suggestions based on grade improvement patterns
- **API Endpoints**: All core functionality working correctly

**For detailed testing strategy and individual test categories**: See [docs/TESTING.md](docs/TESTING.md)

## 📁 Project Structure

```
report-card-assistant/
├── backend/                    # FastAPI Backend (Python 3.12)
│   ├── src/app/               # Source code
│   │   ├── main.py           # Application entry point
│   │   ├── api/              # API routes and endpoints
│   │   ├── core/             # Configuration and database
│   │   ├── models/           # SQLAlchemy database models
│   │   ├── services/         # Business logic layer
│   │   └── schemas/          # Pydantic data validation
│   ├── tests/                # Backend tests (Pytest)
│   ├── alembic/              # Database migrations
│   ├── templates/            # PDF report templates
│   └── Dockerfile           # Backend container
│   
├── frontend/                  # Next.js Frontend (TypeScript)
│   ├── src/app/              # App Router pages
│   ├── src/components/       # React components
│   ├── src/lib/              # Utilities and API client
│   └── Dockerfile           # Frontend container
│
├── docker-compose.yml        # Multi-container orchestration
├── .env.development         # Development environment config (included)
├── .env                     # Docker Compose environment file (auto-created)
├── TESTING.md              # Comprehensive testing guide
└── README.md               # This file
```

## 🔧 Common Operations

### Development
```bash
# View logs
docker compose logs -f

# Access backend container
docker compose exec backend bash

# Access database
docker compose exec db psql -U dev_user -d report_card_dev

# Stop all services
docker compose down
```

### Troubleshooting
```bash
# Reset everything (if login issues or database problems)
docker compose down -v
docker compose up --build

# Check service status
docker compose ps

# View specific service logs
docker compose logs backend
docker compose logs frontend

# If environment issues, verify files exist
ls -la .env*
```

### Environment Files
- **`.env.example`**: Template with placeholders - copy this to `.env` and fill in your values
- **`.env.development`**: Development configuration (committed, safe values for development)
- **`.env`**: Your local configuration (not committed to git)

**Setup Steps:**
1. Copy `.env.example` to `.env.development`
2. Replace placeholder values with your actual credentials
3. For development, you can reference values from `.env.development`

## 🌟 Key Features Demonstrated

### Assignment Requirements ✅
- Multi-school system with 3 schools and realistic sample data
- Multi-role RBAC (form teachers vs year heads)
- Dashboard showing all students with role-appropriate filtering
- Complete report generation workflow with PDF export
- Achievement suggestion system based on performance patterns
- Professional UI/UX with proper validation and error handling

### Technical Excellence ✅
- Clean architecture with service layer separation
- Comprehensive input validation and security measures
- Docker-first development with easy setup
- Pragmatic testing focused on core functionality
- Thoughtful AI-assisted development workflow

### Beyond Requirements 🚀
- Professional PDF generation with WeasyPrint
- Real-time grade input with immediate validation
- Responsive design for various screen sizes
- Comprehensive error handling and user feedback
- Production-ready deployment configuration

---

**Status**: Ready for Submission ✅  
**Last Updated**: August 2025  
**Version**: 1.0.0
