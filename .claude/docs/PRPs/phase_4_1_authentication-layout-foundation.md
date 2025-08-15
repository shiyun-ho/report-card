# PRP: Phase 4.1 - Authentication & Layout Foundation

**Feature**: Next.js Frontend Authentication System with Session Management and Layout  
**Target**: Complete authentication UI, session management, and basic layout for Report Card Assistant  
**Complexity**: Medium  
**Time Estimate**: 1 hour

---

## 📋 Overview

Implement the frontend authentication system for the Teacher Report Card Assistant using Next.js 15 App Router with session-based authentication, React Context for state management, and role-based access control integration. **All development MUST follow Docker-first patterns** as established in project learnings.

### Requirements Alignment
- **Session-based authentication** with secure HTTP-only cookies
- **Role-based access control** (Form Teachers vs Year Heads) 
- **Multi-tenant isolation** (school-level data access)
- **Basic layout** with navigation and logout functionality
- **Error handling** for authentication failures
- **Client-side validation** with server-side verification
- **Docker-first development** following established project patterns

---

## 🐳 Docker-First Development Context

### Critical Docker Patterns (From Learnings)
Based on `.claude/docs/learnings/1_2_docker_environment_management.md` and `1_3_prp_execution_docker_validation.md`:

**Environment Consistency Rule**: 
- ✅ **ALWAYS** use Docker containers for development and validation
- ✅ **ALWAYS** use environment files (`--env-file .env.development`)
- ✅ **NEVER** mix host/container execution mid-task
- ✅ **NEVER** expose credentials in command line

**Docker Network Discovery**:
```bash
# ✅ Discover project network name
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)

# ✅ Use discovered network in commands
docker run --rm --network $NETWORK_NAME --env-file .env.development
```

**Container Path Configuration**:
```bash
# ✅ Frontend container execution pattern
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  cd /app &&
  npm run dev
"
```

---

## 🏗️ Implementation Blueprint

### High-Level Architecture
```typescript
// 1. Authentication Context Provider (Docker containerized)
AuthProvider (React Context)
├── User state management
├── Login/logout functions  
├── Session persistence
└── Role-based helpers

// 2. API Client Layer (Backend integration via Docker network)
ApiClient
├── Cookie-based session handling
├── Error handling for 401/403
├── Request/response interceptors
└── Type-safe endpoints

// 3. Route Protection (Next.js middleware)
Middleware & Layout
├── Protected route checking
├── Role-based redirects
├── Loading states
└── Error boundaries

// 4. UI Components (shadcn/ui)
Components
├── LoginForm (email/password)
├── Navigation (role-aware)
├── Layout wrapper
└── Error displays
```

### Docker-First Implementation Flow
```pseudocode
1. DISCOVER Docker network name for backend communication
2. SETUP frontend Docker environment with backend connectivity
3. CREATE authentication context using containerized API client
4. BUILD login form components using Docker dev environment
5. IMPLEMENT protected layout with Docker validation
6. ADD route protection and session management
7. INTEGRATE logout functionality via Docker containers
8. VALIDATE all features using Docker-first testing approach
```

---

## 🔗 Backend Integration Context

### Authentication API (Fully Implemented)
Based on `@.claude/docs/reference/backend-api-reference.md`:

**Session-Based Authentication Flow:**
- `POST /api/v1/auth/login` - Email/password authentication
- `GET /api/v1/auth/me` - Get current authenticated user
- `GET /api/v1/auth/status` - Check session status  
- `POST /api/v1/auth/logout` - End session and clear cookies

**Docker Network Communication:**
```typescript
// ✅ Backend communication from frontend container
const API_BASE_URL = 'http://backend:8000/api/v1'  // Service name, not localhost
```

**Cookie Management:**
- `session_id`: HTTP-only session cookie (30 min expiry)
- `csrf_token`: CSRF protection token
- Automatic session extension on activity

**User Roles & Permissions:**
```typescript
interface User {
  id: number
  email: string
  username: string
  full_name: string
  role: "form_teacher" | "year_head" | "admin"
  school_id: number
}

// Access Patterns
// Form Teacher: Only assigned students in their class
// Year Head: All students in their school
// Multi-tenant isolation by school_id
```

**Error Handling:**
- `401`: Authentication required / Invalid session
- `403`: Insufficient permissions / Access denied
- `422`: Validation errors (email format, etc.)

---

## 🧱 Existing Codebase Patterns

### Current Frontend Structure
```
frontend/src/
├── app/
│   ├── layout.tsx          # Root layout (to be enhanced)
│   ├── page.tsx            # Home page (to be converted to dashboard)
│   └── globals.css         # Tailwind styles
├── components/
│   └── ui/                 # shadcn/ui components
│       ├── button.tsx      # ✅ Available
│       ├── input.tsx       # ✅ Available  
│       ├── card.tsx        # ✅ Available
│       └── label.tsx       # ✅ Available
└── lib/
    └── utils.ts            # cn() utility available
```

### Docker Environment (Already Configured)
```yaml
# docker-compose.yml frontend service exists
services:
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000/api/v1
    depends_on:
      - backend
```

### Package Dependencies (Already Available)
- **Next.js 15** with App Router
- **React 19** with TypeScript
- **Tailwind CSS v4** for styling
- **shadcn/ui** component library
- **clsx + tailwind-merge** for className utilities

---

## 📚 External Documentation & Resources

### Next.js 15 Authentication Patterns
- **App Router Authentication**: https://nextjs.org/docs/app/guides/authentication
- **Middleware for Route Protection**: https://nextjs.org/docs/app/building-your-application/routing/middleware
- **Client Components vs Server Components**: https://nextjs.org/docs/app/building-your-application/rendering/client-components

### React Context Best Practices
- **Context Provider Patterns**: https://react.dev/learn/passing-data-deeply-with-context
- **useContext Hook**: https://react.dev/reference/react/useContext
- **Context Performance**: https://react.dev/learn/passing-data-deeply-with-context#use-context-and-usereducer-together

### Session-Based Authentication
- **Cookie Management**: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch#sending_a_request_with_credentials_included
- **CSRF Protection**: https://developer.mozilla.org/en-US/docs/Glossary/CSRF

---

## 🛠️ Detailed Implementation Tasks (Docker-First)

### Task 4.1.1: Configure API Client with Docker Backend Communication
**File**: `frontend/src/lib/api.ts`

```typescript
// ✅ Docker-first API client implementation
const apiClient = {
  // Service name communication within Docker network
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000/api/v1',
  
  async request(endpoint: string, options: RequestInit = {}) {
    const url = `${this.baseURL}${endpoint}`
    const config: RequestInit = {
      credentials: 'include',  // Critical: include cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }
    
    const response = await fetch(url, config)
    
    // Handle authentication errors
    if (response.status === 401) {
      throw new AuthError('Authentication required')
    }
    
    if (response.status === 403) {
      throw new AuthError('Permission denied')
    }
    
    if (!response.ok) {
      const error = await response.json()
      throw new ApiError(error.detail || 'Request failed')
    }
    
    return response.json()
  }
}
```

**Docker Validation**:
```bash
# ✅ Test API client within Docker network
docker run --rm --network PROJECT_network --env-file .env.development frontend bash -c "
  cd /app &&
  npm run test:api-client
"
```

### Task 4.1.2: Authentication Context Provider (Docker Environment)
**File**: `frontend/src/contexts/AuthContext.tsx`

```typescript
interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<User>
  logout: () => Promise<void>
  checkAuth: () => Promise<User | null>
  isLoading: boolean
  isAuthenticated: boolean
}

// Implement session persistence using the /auth/me endpoint
// Handle role-based access patterns
// Manage loading states during authentication checks
```

**Docker Development**:
```bash
# ✅ Develop with hot reload in Docker
docker run --rm --network PROJECT_network --env-file .env.development -v $(pwd)/frontend:/app frontend bash -c "
  cd /app &&
  npm run dev
"
```

### Task 4.1.3: Login Form Component (Docker Development)
**File**: `frontend/src/components/LoginForm.tsx`

Follow existing component patterns from `frontend/src/components/ui/`:
```typescript
// Use existing Input, Button, Card components
// Implement client-side validation (email format, required fields)
// Handle form submission with error states
// Show loading spinner during authentication
// Display error messages from API
```

**Docker Testing**:
```bash
# ✅ Component testing in Docker environment
docker run --rm --network PROJECT_network --env-file .env.development frontend bash -c "
  cd /app &&
  npm run test:components
"
```

### Task 4.1.4: Client-Side Validation (Docker Environment)
**File**: `frontend/src/lib/validation.ts`

```typescript
// Email validation
// Password requirements (if any)  
// Form field validation helpers
// Error message standardization
```

### Task 4.1.5: Session Persistence & Logout (Docker Integration)
**Files**: Extend `AuthContext.tsx`

```typescript
// Implement checkAuth() using /api/v1/auth/me via Docker network
// Handle session restoration on app start
// Implement logout with /api/v1/auth/logout via backend service
// Clear user state on logout
// Handle session expiry (401 errors)
```

### Task 4.1.6: Basic Layout with Navigation (Docker Development)
**File**: `frontend/src/app/layout.tsx` (enhance existing)

```typescript
// Wrap app in AuthProvider
// Create navigation with role-based menu items
// Add logout button
// Show user information (name, role, school)
// Handle loading states during auth check
```

**Docker Validation**:
```bash
# ✅ Layout testing with backend integration
docker run --rm --network PROJECT_network --env-file .env.development frontend bash -c "
  cd /app &&
  npm run build &&
  npm start
"
```

---

## 🚀 Implementation Order (Docker-First)

### Phase 1: Docker Environment Setup
```bash
# ✅ Discover project network
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)
echo "Using network: $NETWORK_NAME"

# ✅ Verify frontend container builds
docker compose build frontend

# ✅ Test backend connectivity from frontend container
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  curl http://backend:8000/health
"
```

### Phase 2: API Client Setup (Task 4.1.1)
```bash
# ✅ Create API client in Docker environment
docker run --rm --network $NETWORK_NAME --env-file .env.development -v $(pwd)/frontend:/app frontend bash -c "
  cd /app &&
  touch src/lib/api.ts &&
  npm run type-check
"
```

### Phase 3: Authentication Context (Task 4.1.2)
```bash
# ✅ Develop context in Docker environment
docker run --rm --network $NETWORK_NAME --env-file .env.development -v $(pwd)/frontend:/app frontend bash -c "
  cd /app &&
  mkdir -p src/contexts &&
  touch src/contexts/AuthContext.tsx &&
  npm run dev
"
```

### Phase 4: Components Development (Tasks 4.1.3-4.1.4)
```bash
# ✅ Create components with hot reload
docker run --rm --network $NETWORK_NAME --env-file .env.development -v $(pwd)/frontend:/app frontend bash -c "
  cd /app &&
  npm run dev
" &

# ✅ Test in parallel
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  cd /app &&
  npm run test:watch
"
```

### Phase 5: Integration & Validation (Tasks 4.1.5-4.1.6)
```bash
# ✅ Final integration testing
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  cd /app &&
  npm run build &&
  npm run lint &&
  npm run type-check
"
```

---

## 🧪 Testing Strategy (Docker-First)

### Docker Environment Testing
**Network Discovery**:
```bash
# ✅ Find correct network name
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)
```

**Backend Connectivity Test**:
```bash
# ✅ Test backend communication from frontend container
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  curl -f http://backend:8000/health || exit 1
"
```

### Manual Testing (Docker Environment)
**Note**: Test using credentials from testing documentation (not included here for security).

```bash
# ✅ Full application testing in Docker
docker compose up -d

# ✅ Frontend accessible at localhost:3000
# ✅ Backend accessible via Docker network at backend:8000

# Test scenarios:
# 1. Login Flow: Form teacher and year head credentials
# 2. Session Persistence: Container restart, verify user stays logged in  
# 3. Logout: Clear session via backend
# 4. Invalid Credentials: Show error message
# 5. Session Expiry: Handle 401 errors gracefully
# 6. Role Display: Show correct role information in navigation
```

### API Integration Testing (Docker Network)
```bash
# ✅ Test API client with real backend via Docker network
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  cd /app &&
  npm run test:integration
"
```

---

## 🎯 Validation Gates (Docker-First)

### 1. Docker Network Connectivity
```bash
# ✅ Network discovery and connectivity test
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  curl -f http://backend:8000/health
"
```

### 2. Code Quality (Docker Environment)
```bash
# ✅ Frontend linting and type checking in Docker
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  cd /app &&
  npm run lint &&
  npm run type-check
"
```

### 3. Build Verification (Docker Container)
```bash
# ✅ Build verification in Docker environment
docker run --rm --network $NETWORK_NAME --env-file .env.development frontend bash -c "
  cd /app &&
  npm run build
"
```

### 4. Development Server (Docker Integration)
```bash
# ✅ Start development server with backend connectivity
docker compose up -d
# Verify http://localhost:3000 loads without errors
# Verify API calls reach http://backend:8000/api/v1
```

### 5. Authentication Flow (Docker Full-Stack)
```bash
# ✅ Manual testing checklist in Docker environment:
# ✅ Login form renders correctly
# ✅ Can submit form with valid credentials via Docker network
# ✅ User context updates after login
# ✅ Navigation shows user information
# ✅ Logout clears session via backend
# ✅ Invalid credentials show error from backend
# ✅ Session persists on container restart
```

---

## ⚠️ Critical Implementation Notes (Docker-First)

### Docker Network Configuration
- **MUST** use service names within Docker network (`backend:8000`)
- **MUST** use `localhost:3000` only for external browser access
- **NEVER** use localhost URLs within Docker containers

### Environment File Usage
```bash
# ✅ Always use environment files
docker run --env-file .env.development

# ❌ Never expose credentials inline
docker run -e NEXT_PUBLIC_API_URL=http://backend:8000  # SECURITY VIOLATION
```

### Container Path Configuration
```bash
# ✅ Proper container execution
docker run --rm --network PROJECT_network --env-file .env.development frontend bash -c "
  cd /app &&
  npm run command
"

# ✅ Volume mounting for development
docker run --rm -v $(pwd)/frontend:/app frontend npm run dev
```

### API Client Configuration
```typescript
// ✅ Docker-aware API configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://backend:8000/api/v1'

// ✅ Cookie configuration for Docker network
const apiClient = {
  baseURL: API_BASE_URL,
  credentials: 'include',  // Essential for session cookies
}
```

### Error Handling Strategy (Docker Network)
```typescript
// ✅ Handle Docker network errors
const handleApiError = (error: Error) => {
  if (error.message.includes('ECONNREFUSED')) {
    console.error('Backend service not available - check Docker network')
  }
  // ... other error handling
}
```

---

## 🔍 Quality Assurance (Docker-First)

### Docker Environment Checklist
- [ ] All commands use discovered network name
- [ ] All development uses environment files
- [ ] No explicit credentials in command line
- [ ] Frontend communicates with backend via service names
- [ ] All validation runs in Docker containers

### Code Review Checklist
- [ ] All API calls use service names within Docker network
- [ ] Environment variables loaded from files only
- [ ] Error handling covers Docker network issues
- [ ] TypeScript types match backend models exactly
- [ ] Components follow existing shadcn/ui patterns
- [ ] Loading states implemented for Docker network calls

### Security Checklist (Docker Environment)
- [ ] No credentials hardcoded in frontend code
- [ ] No manual cookie manipulation
- [ ] All environment variables from `.env` files
- [ ] Docker network isolation properly configured
- [ ] Authentication state properly initialized via Docker API calls

---

## 📈 Success Criteria (Docker-First)

### Functional Requirements
- ✅ Users can log in via Docker network backend communication
- ✅ Authentication state persists across container restarts
- ✅ Role information displays correctly from Docker backend
- ✅ Logout functionality works via Docker network
- ✅ Error messages show from Docker backend API
- ✅ Session expiry handled via Docker network calls

### Technical Requirements (Docker Environment)
- ✅ All development and testing in Docker containers
- ✅ Environment file usage for all configuration
- ✅ Service name communication within Docker network
- ✅ TypeScript strict mode compliance
- ✅ Integration with existing shadcn/ui components
- ✅ Clean separation of API client and auth logic

### Docker-First Compliance
- ✅ Zero host environment usage during development
- ✅ All validation gates executable in Docker
- ✅ Network discovery patterns properly implemented
- ✅ Environment file security compliance
- ✅ Container path configuration correct

---

## 🎯 Confidence Score: **10/10**

**Maximum confidence due to:**
- ✅ **Docker-first patterns** strictly followed from project learnings
- ✅ **Backend authentication API** fully implemented and Docker-tested
- ✅ **Network communication patterns** proven in existing backend
- ✅ **Environment file strategy** established and secure
- ✅ **Comprehensive validation gates** all Docker-based
- ✅ **Clear implementation order** with Docker validation at each step
- ✅ **Existing frontend structure** with shadcn/ui components ready
- ✅ **Proven patterns** from project learnings applied consistently

**Risk mitigation:**
- Docker network discovery prevents connection issues
- Environment file usage ensures security compliance
- Backend API already tested and validated
- Docker-first approach ensures production parity
- Progressive validation catches issues early

This PRP provides comprehensive Docker-first implementation guidance that strictly follows established project patterns while delivering the authentication foundation requirement.