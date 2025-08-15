# Phase 6.1 Backend Unit Tests - PRP

**PRP ID**: phase-6-1-backend-unit-tests  
**Phase**: 6.1 Backend Unit Tests  
**Time Estimate**: 10 minutes  
**Priority**: HIGH (Assignment requirement)

## 📋 **Context & Requirements**

### **Assignment Brief Requirements**
From `.claude/docs/context/brief/assignment_brief.md`:
- **Line 34**: "Testing: Unit tests, Integration Tests"
- **Line 40**: "Ensuring edge cases are handled"  
- **Line 41**: "Will test some edge cases on both frontend and API-side e.g. student doesn't exist or date range doesn't exist"

### **Security Policy Compliance**
From `.claude/docs/context/steering/SECURITY.md`:
- **Docker-First Execution**: All commands must use Docker containers with environment files
- **Never Expose Credentials**: Use `--env-file .env.development` pattern only
- **Environment Consistency**: Maintain production parity through container execution

### **Existing Test Patterns**
From `backend/tests/test_achievement_service.py` and `backend/tests/conftest.py`:
- Service layer testing with proper mocking (`unittest.mock.patch`)
- RBAC testing patterns for multi-tenant isolation
- Database session fixtures with seeded test data
- TestClient integration for full API testing
- Comprehensive edge case coverage (unauthorized access, invalid IDs)

## 🎯 **Implementation Approach**

### **Service Under Test: ReportService**
Located at `backend/src/app/services/report_service.py` with these key methods:
```python
def can_generate_report(user: User, student_id: int) -> bool
def generate_pdf_report(student_id, term_id, report_data, current_user) -> bytes  
def get_report_metadata(student_id, term_id, current_user) -> Optional[Dict]
def _compile_report_data(...) -> Dict[str, Any]
```

### **Testing Strategy**
1. **Unit Tests**: Mock all service dependencies (StudentService, GradeService, AchievementService)
2. **RBAC Testing**: Comprehensive authorization scenarios (form teacher, year head, cross-school)
3. **Edge Cases**: Invalid student/term IDs, missing data, WeasyPrint failures
4. **PDF Generation**: Mock WeasyPrint for speed, validate return types and content structure

### **Dependencies to Mock**
```python
from unittest.mock import patch, Mock
# Mock WeasyPrint for speed
@patch('app.services.report_service.HTML')  
# Mock service dependencies  
@patch.object(ReportService, 'student_service')
@patch.object(ReportService, 'grade_service')
```

## 📝 **Implementation Tasks**

### **Task 6.1.1: Create ReportService Unit Tests (5 minutes)**

**File**: `backend/tests/test_report_service.py`

**Test Functions to Implement**:
```python
class TestReportService:
    def test_can_generate_report_form_teacher_authorized(self, db_session)
    def test_can_generate_report_cross_school_denied(self, db_session)  
    def test_can_generate_report_year_head_access(self, db_session)
    def test_generate_pdf_returns_valid_bytes(self, db_session)
    def test_generate_pdf_access_denied_403(self, db_session)
    def test_generate_pdf_student_not_found_404(self, db_session)  
    def test_generate_pdf_term_not_found_404(self, db_session)
    def test_get_report_metadata_success(self, db_session)
    def test_get_report_metadata_no_access_returns_none(self, db_session)
    def test_compile_report_data_structure(self, db_session)
```

**Key Patterns to Follow**:
- Use `with patch('app.core.seed_data.SessionLocal', return_value=db_session)` for data setup
- Mock `HTML(string=html_content).write_pdf()` to return `b'mock_pdf_bytes'`
- Test RBAC with different user roles and schools
- Validate PDF response headers and content-type

### **Task 6.1.2: Enhanced Achievement Service Tests (3 minutes)**

**File**: `backend/tests/test_achievement_service.py` (existing, add missing tests)

**Additional Test Functions**:
```python
def test_achievement_service_rbac_edge_cases(self, db_session)
def test_achievement_service_invalid_student_id(self, db_session) 
def test_achievement_service_invalid_term_id(self, db_session)
```

### **Task 6.1.3: Test Runner Integration (2 minutes)**

**Verification Commands**:
```bash
# Discover network name for Docker execution
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)

# Run new tests with Docker
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && uv run pytest tests/test_report_service.py -v
"
```

## 🔍 **Technical Implementation Details**

### **WeasyPrint Mocking Pattern**
```python
from unittest.mock import patch, Mock

@patch('app.services.report_service.HTML')
def test_generate_pdf_returns_valid_bytes(self, mock_html, db_session):
    # Mock PDF generation to return bytes
    mock_pdf = Mock()
    mock_pdf.write_pdf.return_value = b'mock_pdf_content'
    mock_html.return_value = mock_pdf
    
    # Test business logic without actual PDF generation
    service = ReportService(db_session)
    result = service.generate_pdf_report(student_id, term_id, report_data, user)
    
    assert isinstance(result, bytes)
    assert len(result) > 0
```

### **RBAC Testing Pattern (Following Existing)**
```python
def test_can_generate_report_cross_school_denied(self, db_session):
    with patch('app.core.seed_data.SessionLocal', return_value=db_session):
        seed_database()
    
    schools = db_session.query(School).all()
    student_school1 = db_session.query(Student).filter(Student.school_id == schools[0].id).first()
    teacher_school2 = db_session.query(User).filter(User.school_id == schools[1].id).first()
    
    service = ReportService(db_session)
    assert not service.can_generate_report(teacher_school2, student_school1.id)
```

### **Edge Case Testing (Assignment Requirement)**
```python
def test_generate_pdf_student_not_found_404(self, db_session):
    service = ReportService(db_session)
    teacher = db_session.query(User).first()
    
    with pytest.raises(HTTPException) as exc_info:
        service.generate_pdf_report(99999, 1, report_data, teacher)
    
    assert exc_info.value.status_code == 404
    assert "not found" in exc_info.value.detail.lower()
```

## ✅ **Validation Gates**

### **Gate 1: Syntax and Style Validation**
```bash
# Docker-first linting execution
NETWORK_NAME=$(docker network ls | grep report-card-assistant | awk '{print $2}' | head -1)

docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  cd /app && uv run ruff check --fix tests/test_report_service.py
"

docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  cd /app && uv run mypy tests/test_report_service.py
"
```

### **Gate 2: Unit Test Execution**
```bash
# Run ReportService unit tests
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && uv run pytest tests/test_report_service.py -v
"

# Run all service layer tests
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && uv run pytest tests/test_*_service.py -v
"
```

### **Gate 3: Test Coverage Validation**
```bash
# Verify test coverage for ReportService
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && uv run pytest tests/test_report_service.py --cov=src/app/services/report_service --cov-report=term-missing
"
```

### **Gate 4: Integration with Existing Test Suite**
```bash
# Ensure all tests still pass together
docker run --rm --env-file .env.development --network $NETWORK_NAME --user root backend bash -c "
  export PYTHONPATH=/app/src && cd /app && uv run pytest tests/ -v --tb=short
"
```

## 🎯 **Success Criteria**

### **Functional Requirements**
- [ ] 10+ unit tests for ReportService covering all public methods
- [ ] RBAC enforcement tested for form teachers, year heads, cross-school scenarios
- [ ] Edge cases tested: invalid student ID, invalid term ID, missing data
- [ ] PDF generation mocked for performance, actual bytes returned validated
- [ ] All existing tests continue to pass

### **Assignment Requirements Met**
- [ ] ✅ **Unit Tests**: Service layer business logic thoroughly tested
- [ ] ✅ **Edge Cases**: "student doesn't exist", "term doesn't exist" scenarios covered
- [ ] ✅ **Error Handling**: HTTP exceptions and status codes validated
- [ ] ✅ **Security**: RBAC and multi-tenant isolation verified

### **Security Compliance**
- [ ] All validation gates use Docker-first execution
- [ ] Environment files used consistently (`--env-file .env.development`)
- [ ] No credentials exposed in command line history
- [ ] Container networking properly configured

## 📚 **External References**

- **FastAPI Testing Guide**: https://fastapi.tiangolo.com/tutorial/testing/
- **Pytest Documentation**: https://docs.pytest.org/en/stable/
- **pytest-docker Plugin**: https://pypi.org/project/pytest-docker/
- **WeasyPrint Testing**: https://weasyprint.org/ (mocking strategies)

## 🚨 **Risk Mitigation**

### **Performance Considerations**
- Mock WeasyPrint PDF generation for unit tests (fast execution)
- Use existing seeded database for realistic data testing
- Limit test scope to business logic, not full integration

### **Docker Execution Issues** 
- Network discovery commands included for environment consistency
- User permissions handled with `--user root` when needed
- Environment file patterns following security policy

### **Test Isolation**
- Each test uses fresh database session from fixtures
- Service instances created per test method
- Mocking prevents external dependencies affecting test results

---

## 📊 **PRP Quality Score: 9/10**

**Confidence Level**: HIGH - One-pass implementation success expected

**Justification**:
- ✅ **Comprehensive Context**: Assignment requirements, existing patterns, security policies
- ✅ **Technical Blueprint**: Specific test functions, mocking strategies, validation commands  
- ✅ **Docker-First Compliance**: All commands follow established security patterns
- ✅ **Existing Pattern Reuse**: Based on proven `test_achievement_service.py` structure
- ✅ **Assignment Alignment**: Directly addresses unit tests, integration tests, edge cases
- ⚠️ **Minor Risk**: WeasyPrint mocking complexity, but fallback patterns provided

**Expected Outcome**: Complete unit test suite for ReportService with comprehensive RBAC coverage and edge case handling, fully compliant with assignment requirements and security policies.