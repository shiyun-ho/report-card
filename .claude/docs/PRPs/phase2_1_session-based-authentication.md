# PRP: Session-Based Authentication System (Phase 2.1)

## Goal
Implement secure session-based authentication for the Teacher Report Card Assistant, providing login/logout functionality, session management, CSRF protection, and role-based access control for form teachers and year heads across multiple schools.

## Why
- **RBAC Requirement**: Assignment requires teachers see assigned students only, head teachers see all school students
- **Security Compliance**: Multi-tenant system needs proper authentication with school-level isolation
- **User Experience**: Simple session-based auth is easier to implement and debug than JWT for this MVP
- **Foundation for Phase 3+**: All subsequent APIs require authentication dependencies

## What
Session-based authentication system with PostgreSQL session storage, secure cookies, CSRF protection, and FastAPI dependencies for route protection.

### Success Criteria
- [ ] Users can log in with username/password and get secure session cookies
- [ ] Session data stored in PostgreSQL with proper expiry and cleanup
- [ ] CSRF tokens generated and validated on state-changing operations
- [ ] Authentication dependencies work for protecting routes
- [ ] Role-based access control isolates form teachers vs year heads
- [ ] Multi-tenant school isolation prevents cross-school access
- [ ] Session expires after 30 minutes of inactivity
- [ ] Secure cookie attributes (httpOnly, secure, samesite) properly configured

## All Needed Context

### Documentation & References
```yaml
# External Best Practices
- url: https://betterstack.com/community/guides/scaling-python/authentication-fastapi/
  why: FastAPI authentication patterns and security best practices
  
- url: https://fastapi.tiangolo.com/advanced/response-cookies/
  why: Secure cookie configuration with httpOnly, secure, samesite attributes
  
- url: https://docs.sqlalchemy.org/en/20/orm/relationships.html
  why: SQLAlchemy 2.0 relationship patterns for User-Session association

# Existing Codebase Patterns
- file: backend/src/app/models/user.py
  why: Existing User model with roles, follow SQLAlchemy 2.0 patterns, multi-tenant school_id
  
- file: backend/src/app/models/base.py
  why: BaseModel pattern with id, created_at, updated_at, is_active fields
  
- file: backend/src/app/core/security.py
  why: Already implemented bcrypt, session ID generation, CSRF tokens - use these utilities
  
- file: backend/src/app/core/config.py
  why: Settings pattern with environment variables, SESSION_EXPIRE_MINUTES already configured
  
- file: backend/src/app/core/database.py
  why: Database connection pattern with get_db() dependency injection
  
- file: backend/src/app/api/v1/api.py
  why: API router patterns and FastAPI dependency injection structure
  
- file: backend/tests/test_seed_data/conftest.py
  why: Test patterns with database fixtures and Docker-first testing
```

### Current Codebase Tree (Relevant Parts)
```bash
backend/src/app/
├── __init__.py
├── main.py                     # FastAPI app with CORS configured
├── core/
│   ├── config.py              # Settings with SESSION_EXPIRE_MINUTES
│   ├── database.py            # get_db() dependency pattern
│   └── security.py            # bcrypt, session utils ready
├── models/
│   ├── base.py                # BaseModel with common fields
│   ├── user.py                # User with roles, school_id
│   └── __init__.py
├── api/
│   └── v1/
│       ├── api.py             # Router aggregation
│       └── __init__.py
└── services/                  # Empty, need to create auth_service.py
```

### Desired Codebase Tree (After Implementation)
```bash
backend/src/app/
├── models/
│   ├── session.py             # NEW: Session model for PostgreSQL storage
│   └── user.py                # MODIFY: Add sessions relationship
├── services/
│   └── auth_service.py        # NEW: Authentication business logic
├── api/v1/endpoints/
│   └── auth.py                # NEW: Login/logout/me endpoints
├── dependencies/
│   └── auth.py                # NEW: Authentication dependencies
├── middleware/
│   ├── session.py             # NEW: Session validation middleware
│   └── csrf.py                # NEW: CSRF protection middleware
└── main.py                    # MODIFY: Add middleware and auth routes
```

### Known Gotchas & Library Quirks
```python
# CRITICAL: SQLAlchemy 2.0 uses Mapped[] type annotations
# Example: user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

# CRITICAL: FastAPI cookies require Response object
# Example: response.set_cookie(key="session", value=token, httponly=True)

# CRITICAL: Existing security.py functions to use:
# - verify_password(plain, hashed) -> bool
# - get_password_hash(password) -> str  
# - generate_session_id() -> str (uses secrets.token_urlsafe(32))
# - generate_csrf_token() -> str
# - is_session_expired(expires_at) -> bool

# CRITICAL: Multi-tenant isolation via school_id
# - All queries must filter by current user's school_id
# - Form teachers: additional filter by assigned classes
# - Year heads: all students in their school only

# CRITICAL: FastAPI dependency injection pattern
# - Use Depends(get_db) for database sessions
# - Use Depends(get_current_user) for authentication
# - Dependencies compose: auth -> role check -> school access

# CRITICAL: Session security requirements
# - httponly=True (prevent XSS)
# - secure=True in production (HTTPS only)
# - samesite="lax" (CSRF protection)
# - max_age=settings.SESSION_EXPIRE_MINUTES * 60
```

## Implementation Blueprint

### Data Models and Structure

Session model following existing patterns with proper relationships:
```python
# models/session.py - PostgreSQL session storage
class Session(BaseModel):
    __tablename__ = "user_sessions"
    
    # Primary key is hashed session token
    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    
    # Foreign key to user
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Session lifecycle
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # Security tracking
    csrf_token: Mapped[str] = mapped_column(String(64), nullable=False)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    
    # Relationship back to user
    user: Mapped["User"] = relationship(back_populates="sessions")
```

### List of Tasks to Complete the PRP (in order)

```yaml
Task 1 - Create Session Model:
CREATE backend/src/app/models/session.py:
  - MIRROR pattern from: backend/src/app/models/user.py
  - USE BaseModel inheritance for common fields
  - FOLLOW SQLAlchemy 2.0 Mapped[] type annotations
  - INCLUDE security tracking fields (csrf_token, user_agent, ip_address)

Task 2 - Update User Model:
MODIFY backend/src/app/models/user.py:
  - FIND pattern: "class User(BaseModel)"
  - ADD relationship: sessions: Mapped[List["Session"]] = relationship(back_populates="user", cascade="all, delete-orphan")
  - PRESERVE existing relationships and constraints

Task 3 - Generate Database Migration:
EXECUTE in backend directory:
  - RUN: uv run alembic revision --autogenerate -m "Add user sessions table"
  - VERIFY migration includes user_sessions table with proper indexes
  - RUN: uv run alembic upgrade head

Task 4 - Create Authentication Service:
CREATE backend/src/app/services/auth_service.py:
  - MIRROR pattern from: existing service structure (dependency injection)
  - USE existing security utilities: verify_password, generate_session_id, generate_csrf_token
  - IMPLEMENT: authenticate_user, create_session, get_session, delete_session, cleanup_expired_sessions
  - FOLLOW multi-tenant isolation patterns

Task 5 - Create Authentication Endpoints:
CREATE backend/src/app/api/v1/endpoints/auth.py:
  - MIRROR pattern from: backend/src/app/api/v1/api.py router structure
  - IMPLEMENT: POST /login, POST /logout, GET /me
  - USE Pydantic models for request/response validation
  - SET secure cookies with proper attributes

Task 6 - Create Authentication Dependencies:
CREATE backend/src/app/dependencies/auth.py:
  - FOLLOW FastAPI dependency injection patterns
  - IMPLEMENT: get_current_user, get_current_user_optional, require_role, require_school_access
  - USE existing UserRole enum for role validation
  - ENFORCE multi-tenant school isolation

Task 7 - Create Session Middleware:
CREATE backend/src/app/middleware/session.py:
  - FOLLOW Starlette BaseHTTPMiddleware pattern
  - IMPLEMENT automatic session validation on requests
  - SET request.state.user and request.state.authenticated
  - EXCLUDE authentication paths from validation

Task 8 - Create CSRF Middleware:
CREATE backend/src/app/middleware/csrf.py:
  - FOLLOW BaseHTTPMiddleware pattern
  - VALIDATE CSRF tokens on state-changing methods (POST, PUT, PATCH, DELETE)
  - USE existing generate_csrf_token utility
  - IMPLEMENT double-submit cookie pattern

Task 9 - Integrate with Main Application:
MODIFY backend/src/app/main.py:
  - FIND pattern: "app = FastAPI("
  - ADD middleware: SessionMiddleware, CSRFMiddleware (in correct order)
  - PRESERVE existing CORS middleware with allow_credentials=True
  
MODIFY backend/src/app/api/v1/api.py:
  - FIND pattern: "api_router = APIRouter()"
  - ADD: api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])

Task 10 - Create Authentication Tests:
CREATE backend/tests/test_auth/:
  - MIRROR pattern from: backend/tests/test_seed_data/ structure
  - CREATE: test_auth_service.py, test_auth_endpoints.py, test_middleware.py
  - FOLLOW Docker-first testing patterns
  - TEST: login flow, RBAC enforcement, session expiry, CSRF protection
```

### Per Task Pseudocode

```python
# Task 4 - AuthService Pseudocode
class AuthService:
    def __init__(self, db: Session):
        self.db = db
    
    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        # PATTERN: Query with OR condition for username/email
        user = self.db.query(User).filter(
            or_(User.username == username, User.email == username)
        ).first()
        
        # USE existing security utility
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user
    
    async def create_session(self, user: User, user_agent: str = None, ip_address: str = None) -> Tuple[str, Session]:
        # USE existing security utilities
        session_token = generate_session_id()  # secrets.token_urlsafe(32)
        session_id = hashlib.sha256(session_token.encode()).hexdigest()
        
        # CREATE session with proper expiry
        session = Session(
            id=session_id,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(minutes=settings.SESSION_EXPIRE_MINUTES),
            csrf_token=generate_csrf_token(),
            user_agent=user_agent,
            ip_address=ip_address
        )
        
        self.db.add(session)
        self.db.commit()
        return session_token, session

# Task 5 - Authentication Endpoints Pseudocode
@router.post("/login")
async def login(response: Response, login_data: LoginRequest, db: Session = Depends(get_db)):
    # AUTHENTICATE using service
    auth_service = AuthService(db)
    user = await auth_service.authenticate_user(login_data.username, login_data.password)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # CREATE session
    session_token, session = await auth_service.create_session(
        user=user,
        user_agent=request.headers.get("User-Agent"),
        ip_address=request.client.host
    )
    
    # SET secure cookies
    response.set_cookie(
        key="session_token",
        value=session_token,
        max_age=settings.SESSION_EXPIRE_MINUTES * 60,
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS in production
        samesite="lax"
    )
    
    response.set_cookie(
        key="csrf_token", 
        value=session.csrf_token,
        httponly=False,  # Accessible to frontend
        secure=not settings.DEBUG,
        samesite="lax"
    )
```

### Integration Points
```yaml
DATABASE:
  - migration: "Add user_sessions table with indexes on user_id, expires_at"
  - relationship: "User.sessions back_populates Session.user"
  
CONFIG:
  - already configured: SESSION_EXPIRE_MINUTES, SECRET_KEY, SESSION_SECRET_KEY
  - use existing: settings.DEBUG for secure cookie conditional
  
ROUTES:
  - add to: backend/src/app/api/v1/api.py
  - pattern: "api_router.include_router(auth.router, prefix='/auth')"
  
MIDDLEWARE:
  - add to: backend/src/app/main.py  
  - order: SessionMiddleware BEFORE CSRFMiddleware
  - preserve: existing CORS with allow_credentials=True
```

## Validation Loop

### Level 1: Syntax & Style
```bash
# Run these FIRST - fix any errors before proceeding
cd backend
uv run ruff format .                    # Format all code
uv run ruff check --fix .               # Auto-fix linting issues  
uv run mypy src/                        # Type checking

# Expected: No errors. If errors, READ the error message and fix.
```

### Level 2: Database Validation
```bash
# Verify database migration and models
cd backend
uv run alembic upgrade head             # Apply migration
uv run python -c "
from app.core.database import SessionLocal
from app.models.session import Session
from app.models.user import User
db = SessionLocal()
print('Session table created:', db.query(Session).count() == 0)
print('User.sessions relationship:', hasattr(User, 'sessions'))
db.close()
"

# Expected: Both should print True
```

### Level 3: Unit Tests
```bash
# Create and run authentication tests
cd backend
uv run pytest tests/test_auth/ -v

# Test categories to verify:
# - AuthService: authenticate_user, create_session, session expiry
# - Endpoints: login success/failure, logout, me endpoint  
# - Dependencies: get_current_user, role validation, school isolation
# - Middleware: session validation, CSRF protection
```

### Level 4: Integration Test
```bash
# Start the application
cd backend
docker-compose up -d                    # Start PostgreSQL
uv run uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000

# Test login flow
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "tan", "password": "'"$SEED_DEFAULT_PASSWORD"'"}' \
  -c cookies.txt

# Expected: {"message": "Login successful", "user": {...}, "csrf_token": "..."}
# Expected: Set-Cookie headers with session_token and csrf_token

# Test authenticated endpoint
curl -X GET http://localhost:8000/api/v1/auth/me \
  -b cookies.txt

# Expected: {"id": 1, "username": "tan", "role": "FORM_TEACHER", ...}
```

## Final Validation Checklist
- [ ] All tests pass: `uv run pytest tests/ -v`
- [ ] No linting errors: `uv run ruff check .`
- [ ] No type errors: `uv run mypy src/`
- [ ] Database migration successful: `uv run alembic upgrade head`
- [ ] Login endpoint returns secure cookies: `curl -c cookies.txt /api/v1/auth/login`
- [ ] Authentication dependencies work: `curl -b cookies.txt /api/v1/auth/me`  
- [ ] CSRF protection active on state-changing operations
- [ ] Session expiry and cleanup working
- [ ] Multi-tenant isolation enforced (form teachers vs year heads)
- [ ] Error cases handled gracefully (401, 403 status codes)

---

## Anti-Patterns to Avoid
- ❌ Don't create new password hashing - use existing `get_password_hash`, `verify_password`
- ❌ Don't skip CSRF protection on state-changing operations  
- ❌ Don't use sync database operations in async FastAPI endpoints
- ❌ Don't hardcode session expiry - use `settings.SESSION_EXPIRE_MINUTES`
- ❌ Don't forget multi-tenant school_id isolation in queries
- ❌ Don't set insecure cookies (missing httpOnly, secure, samesite)
- ❌ Don't skip proper error handling for authentication failures

## Implementation Confidence Score: 9/10

**Rationale:**
- **Strong Foundation** (10/10): Security utilities, User model, database patterns all exist and ready
- **Clear Documentation** (9/10): External FastAPI patterns researched, existing codebase patterns documented
- **Established Patterns** (9/10): SQLAlchemy 2.0, dependency injection, middleware patterns understood
- **Security Compliance** (9/10): CSRF, secure cookies, multi-tenant isolation requirements clear
- **Testing Strategy** (8/10): Existing test patterns established, Docker-first validation ready
- **Validation Gates** (9/10): Executable commands provided for each validation level

**Success Factors:**
- Leverages existing bcrypt and session utilities (no reinvention)
- Follows established SQLAlchemy 2.0 and FastAPI patterns from codebase
- Clear task breakdown with specific file modifications
- Comprehensive validation strategy from syntax to integration testing
- Multi-tenant RBAC requirements clearly understood and implementable

**Minor Risk:**
- Custom middleware implementation requires careful testing with existing CORS setup
- Session cleanup background job may need separate implementation later

The implementation has excellent chances of success due to strong existing foundations and clear execution plan.