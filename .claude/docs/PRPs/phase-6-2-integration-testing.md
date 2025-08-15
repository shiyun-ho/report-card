# PRP: Phase 6.2 Integration Testing

## Overview

**Feature**: End-to-end integration testing for report generation workflow  
**Phase**: 6.2 of Implementation Plan  
**Priority**: Critical (required for assignment completion validation)  
**Estimated Time**: 1 hour  
**Confidence Level**: 9/10  

This PRP implements assignment-appropriate integration testing for the Teacher Report Card Assistant, focusing on core workflow validation and edge case handling as specified in the assignment brief.

## Context & Requirements

### From Assignment Brief  
**Testing Requirements**: "Unit tests, Integration Tests"
**Edge Case Testing**: "Will test some edge cases on both frontend and API-side e.g. student doesn't exist or date range doesn't exist"

**Core Requirements to Validate**:
- [ ] End-to-end report generation workflow works
- [ ] RBAC works (teachers see only their students, heads see all)
- [ ] Multi-tenant isolation (cross-school access prevention)
- [ ] Edge cases handled (non-existent students, invalid data)

**Assignment Scope**: Basic integration tests that prove the system works end-to-end, not comprehensive test infrastructure.

## Security Compliance

**MANDATORY: Follow security patterns from `@.claude/docs/context/steering/SECURITY.md`**

Key security requirements:
- Use `.env.development` for test credentials (already established)
- Never expose credentials in test output or logs
- Test security isolation between schools and roles
- Validate CSRF protection in complete workflows

## Existing Infrastructure Analysis

### Current Test Structure (Strong Foundation)
```
backend/tests/
├── conftest.py                    # Global test config ✅
├── test_auth/
│   ├── test_integration.py        # Auth workflow tests ✅
│   ├── test_auth_endpoints.py     # API endpoint tests ✅
│   └── conftest.py               # Auth fixtures ✅
├── test_seed_data/
│   ├── test_integration_seeding.py # Database integration ✅
│   └── test_docker_execution.sh   # Docker test script ✅
├── test_achievement_service.py    # Unit tests ✅
└── test_report_service.py         # Unit tests ✅
```

### Established Patterns to Follow
From `backend/tests/test_auth/test_integration.py`:
- **TestClient usage**: Session-based authentication testing
- **Multi-tenant isolation**: Cross-school access prevention
- **Role-based testing**: Form Teacher vs Year Head scenarios
- **Complete workflows**: Login → Protected endpoints → Logout
- **Error handling**: Invalid credentials, expired sessions, access denied

### Available Test Data (From testing-credentials.md)
- **3 Schools**: RPS, HPS, EPS with known user credentials
- **6 Test Users**: 3 Form Teachers + 3 Year Heads with known passwords
- **12 Students**: 4 per school with known grade patterns
- **Achievement Triggers**: Students 1-3 (significant improvement), 4-6 (steady progress), 7-9 (excellence), 10-12 (stable)

## Implementation Blueprint

### 1. End-to-End API Workflow Testing

**Core Workflow to Test**:
```
Login → Dashboard (Get Students) → Select Student → 
View Grades → Get Achievement Suggestions → Generate Report → 
Download PDF → Logout
```

**Test Structure**:
```python
class TestReportGenerationWorkflow:
    """End-to-end testing of complete report generation workflow."""
    
    def test_form_teacher_complete_workflow(self, test_client):
        """Test complete workflow as Form Teacher."""
        # 1. Login as form teacher
        # 2. Get accessible students (should be filtered)
        # 3. Access student details and grades
        # 4. Get achievement suggestions
        # 5. Generate report PDF
        # 6. Verify PDF content structure
        # 7. Logout
    
    def test_year_head_complete_workflow(self, test_client):
        """Test complete workflow as Year Head."""
        # Same workflow but with broader access permissions
    
    def test_cross_school_access_prevention(self, test_client):
        """Test that users cannot access other schools' data."""
        # Login to school 1, attempt to access school 2 data
    
    def test_workflow_error_scenarios(self, test_client):
        """Test error handling throughout workflow."""
        # Invalid student IDs, unauthorized access, etc.
```

### 2. Frontend-Backend Integration Testing

**Focus Areas**:
- Session management across multiple requests
- CSRF protection in real scenarios  
- API response validation
- Error handling propagation

**Implementation Pattern**:
```python
class TestFrontendBackendIntegration:
    """Test frontend-backend communication patterns."""
    
    def test_session_persistence_across_requests(self, test_client):
        """Test session cookies work across multiple API calls."""
        
    def test_csrf_protection_workflow(self, test_client):
        """Test CSRF tokens in complete workflows."""
        
    def test_api_data_consistency(self, test_client):
        """Test data consistency between API endpoints."""
        # Dashboard data should match individual student data
```

### 3. Docker Container Integration Testing

**Container Orchestration Tests**:
```python
class TestDockerIntegration:
    """Test Docker container integration and networking."""
    
    def test_database_connectivity(self):
        """Test backend can connect to PostgreSQL container."""
        
    def test_container_network_communication(self):
        """Test containers can communicate via Docker network."""
        
    def test_environment_variable_propagation(self):
        """Test environment variables reach all containers."""
```

## Test Data Utilization Strategy

### Leveraging Known Patterns (From seed data)
```python
# Test users with known credentials
FORM_TEACHERS = [
    ("tan@rps.edu.sg", "${SEED_DEFAULT_PASSWORD}", "Riverside Primary"),
    ("wong@hps.edu.sg", "${SEED_DEFAULT_PASSWORD}", "Hillview Primary"), 
    ("chen@eps.edu.sg", "${SEED_DEFAULT_PASSWORD}", "Eastwood Primary"),
]

YEAR_HEADS = [
    ("lim@rps.edu.sg", "${SEED_DEFAULT_PASSWORD}", "Riverside Primary"),
    ("kumar@hps.edu.sg", "${SEED_DEFAULT_PASSWORD}", "Hillview Primary"),
    ("lee@eps.edu.sg", "${SEED_DEFAULT_PASSWORD}", "Eastwood Primary"),
]

# Known achievement patterns for testing
ACHIEVEMENT_TEST_CASES = {
    "significant_improvement": [1, 2, 3],  # ≥20% improvement
    "steady_progress": [4, 5, 6],         # 10-19% improvement  
    "excellence": [7, 8, 9],              # ≥90% scores
    "stable": [10, 11, 12],               # <10% improvement
}
```

## Technology Integration

### FastAPI TestClient (Established Pattern)
```python
from fastapi.testclient import TestClient
from app.main import app

# Following existing conftest.py pattern
@pytest.fixture(scope="function")
def test_client(db_session: Session) -> TestClient:
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
```

### Docker Integration (New Implementation)
Following 2024 best practices from research:
```python
import docker
import pytest
from urllib.parse import urlparse

@pytest.fixture(scope="session")  
def docker_compose_integration():
    """Test Docker Compose service integration."""
    client = docker.from_env()
    
    # Verify containers are running
    backend_container = client.containers.get("report-card-backend")
    db_container = client.containers.get("report-card-db")
    
    assert backend_container.status == "running"
    assert db_container.status == "running"
    
    yield {
        "backend": backend_container,
        "database": db_container
    }
```

## Error Handling Strategy

### Comprehensive Error Scenarios
1. **Authentication Errors**: Invalid credentials, expired sessions
2. **Authorization Errors**: Cross-school access, insufficient permissions
3. **Data Errors**: Non-existent students, invalid grade data
4. **System Errors**: Database connectivity, container communication

### Error Validation Pattern
```python
def test_error_response_consistency(self, test_client):
    """Test error responses follow consistent format."""
    
    # Test authentication error
    response = test_client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "detail" in response.json()
    
    # Test authorization error
    # Login as form teacher, try to access different school
    # Should get 403 or 404 (access denied pattern)
```

## Validation Gates (Executable)

### Backend Integration Tests
```bash
# Docker-first execution following established patterns
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)

# Run integration tests
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && 
  uv run pytest tests/test_integration/ -v --tb=short
"

# Run specific workflow tests
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && 
  uv run pytest tests/test_integration/test_report_workflow.py::TestReportGenerationWorkflow::test_form_teacher_complete_workflow -v
"
```

### Docker Integration Validation
```bash
# Test container health and connectivity
docker compose exec backend curl -f http://db:5432 || echo "DB connection test"
docker compose exec backend curl -f http://localhost:8000/health || echo "Backend health test"

# Test database operations
docker compose exec backend bash -c "
  export PYTHONPATH=/app/src && 
  uv run python -c 'from app.core.database import SessionLocal; SessionLocal().execute(\"SELECT 1\")'
"
```

### Style and Quality Gates  
```bash
# Code quality (established patterns)
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  cd /app && uv run ruff check --fix && uv run ruff format .
"

# Type checking
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  cd /app && uv run mypy src/
"
```

## Implementation Tasks (Assignment-Focused)

### Task 1: Basic Integration Tests
- [ ] Create `test_integration_workflow.py` with core workflow test
- [ ] Test: Login → Get Students → Generate Report → PDF Download

### Task 2: RBAC Integration Tests  
- [ ] Test Form Teacher can only see assigned students
- [ ] Test Year Head can see all students in their school
- [ ] Test cross-school access prevention

### Task 3: Edge Case Integration Tests
- [ ] Test non-existent student ID handling
- [ ] Test invalid term/date handling  
- [ ] Test unauthorized access scenarios

### Task 4: Validation
- [ ] Run tests and ensure core workflow passes
- [ ] Verify edge cases return appropriate errors

## Success Criteria

### Functional Validation
- [ ] Complete report generation workflow works for all user roles
- [ ] Multi-tenant isolation prevents cross-school data access
- [ ] All API endpoints work together seamlessly
- [ ] PDF generation works within complete workflow
- [ ] Error handling works consistently throughout workflows

### Technical Validation  
- [ ] All integration tests pass in Docker environment
- [ ] Container networking and communication verified
- [ ] Database transactions work across workflow steps
- [ ] Session management persists through complete workflows
- [ ] CSRF protection doesn't interfere with legitimate workflows

### Performance Validation
- [ ] Complete workflows execute in reasonable time (<5 seconds)
- [ ] Container startup and networking doesn't cause delays
- [ ] Database queries remain performant in integrated environment

## Risk Mitigation

### Known Challenges
1. **Container Dependencies**: Database must be ready before backend tests
2. **Session Management**: Cookies must persist across TestClient requests  
3. **PDF Generation**: WeasyPrint dependencies in Docker environment
4. **Test Data**: Must use consistent seeded data across all test scenarios

### Mitigation Strategies
1. **Health Checks**: Wait for container readiness before running tests
2. **Session Fixtures**: Create reusable authenticated session fixtures
3. **PDF Mocking**: Mock PDF generation for speed, test actual generation separately
4. **Data Isolation**: Use transaction rollback or test database reset

## External References

### Documentation URLs
- **FastAPI Testing**: https://fastapi.tiangolo.com/tutorial/testing/
- **Pytest Docker Integration**: https://github.com/avast/pytest-docker
- **Integration Testing Best Practices**: https://jnikenoueba.medium.com/unit-and-integration-testing-with-fastapi-e30797242cd7

### Code Examples from Codebase
- **Auth Integration Tests**: `backend/tests/test_auth/test_integration.py`
- **Test Configuration**: `backend/tests/conftest.py`
- **Docker Execution**: `backend/tests/test_seed_data/test_docker_execution.sh`
- **API Reference**: `@.claude/docs/reference/backend-api-reference.md`
- **Test Credentials**: `@.claude/docs/reference/testing-credentials.md`

## Gotchas and Common Issues

### FastAPI TestClient Limitations
- TestClient doesn't handle WebSocket connections
- Session cookies need explicit management for multi-request tests
- Async endpoints require special handling with pytest-asyncio

### Docker Integration Challenges  
- Container networking requires proper network discovery
- Environment variables must be properly passed to test containers
- Volume mounts can interfere with test isolation

### Database Testing Issues
- Foreign key constraints can cause test data setup issues
- Transaction rollback may not work with certain operations
- Connection pooling can cause test interference

## Quality Checklist

- [x] All necessary context included (existing patterns, test data, security requirements)
- [x] Validation gates are executable by AI (Docker commands with proper flags)
- [x] References existing patterns (auth integration tests, conftest setup)
- [x] Clear implementation path (6 sequential tasks with specific deliverables)
- [x] Error handling documented (authentication, authorization, data, system errors)
- [x] Security compliance addressed (environment variables, credentials, isolation)
- [x] External references provided (FastAPI docs, pytest patterns, best practices)
- [x] Docker-first execution patterns (following established container usage)

## Confidence Level: 9/10

**High confidence based on**:
- Strong existing test infrastructure and patterns to follow
- Well-documented API endpoints and test credentials
- Established Docker-first development patterns  
- Clear requirements and success criteria
- Comprehensive research of 2024 best practices

**Remaining 1 point risk**: Integration complexity between all three layers (API, Docker, Frontend) may reveal edge cases not covered in unit tests.

This PRP provides complete context for one-pass implementation success through comprehensive coverage of all integration testing requirements while following established patterns and security guidelines.