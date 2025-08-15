# Project Requirements & Planning (PRP) - Phase 2.2 RBAC Implementation

**Session**: Phase 2.2 Role-Based Access Control Implementation  
**Date**: August 14, 2025  
**Context**: Teacher Report Card Assistant - Multi-tenant RBAC API Implementation

## Overview

Phase 2.2 focuses on implementing the core business APIs with role-based access control, leveraging the comprehensive authentication and RBAC foundation built in Phase 2.1. This phase creates the student, class, and grade management endpoints with proper role-based data filtering and multi-tenant isolation.

## Requirements Analysis

### Functional Requirements
1. **Student Management API**: Role-based student listing with proper filtering
2. **Class Management API**: Access control based on teacher assignments
3. **Grade Management API**: CRUD operations with role-based permissions
4. **Data Access Patterns**: Form teachers see assigned students only, Year heads see all school students
5. **Multi-tenant Isolation**: Complete school-level data segregation
6. **Permission Enforcement**: Automatic role checking at API and query level

### Technical Requirements
1. **FastAPI Endpoints**: RESTful APIs following established patterns
2. **Dependency Injection**: Leverage existing RBAC dependencies
3. **Query Filtering**: Role-based data access at database level
4. **Response Models**: Pydantic schemas with proper validation
5. **Error Handling**: Consistent HTTP status codes and messages
6. **Performance**: Efficient queries with proper indexing

### Security Requirements
1. **Authorization**: Role-based endpoint access using existing dependencies
2. **Data Isolation**: School-level filtering on all queries
3. **Input Validation**: Comprehensive request validation and sanitization
4. **Audit Trail**: Track data modifications with user attribution
5. **CSRF Protection**: Secure state-changing operations

## Current State Analysis

### Completed Phase 2.1 Foundation ✅
- **Session Authentication**: Complete PostgreSQL-backed session management
- **RBAC Dependencies**: Comprehensive role-based dependencies implemented:
  - `get_current_user()` - Session validation
  - `require_form_teacher()` - Form teacher role enforcement
  - `require_year_head()` - Year head role enforcement  
  - `require_year_head_or_admin()` - Multiple role support
  - `get_current_user_school_id()` - Multi-tenant isolation
  - `SchoolIsolationDependency` - Configurable school access control
- **Security Middleware**: Session, CSRF, and security validation middleware
- **User Management**: Complete user authentication and session management APIs

### Database Infrastructure ✅
- **Multi-tenant Models**: School-based data segregation built-in
- **Role System**: Form Teacher, Year Head, Admin roles implemented
- **Teacher Assignments**: `TeacherClassAssignment` model for access control
- **Student Data**: Complete student, class, grade, and achievement models
- **Indexing**: Proper indexes for multi-tenant queries and performance

### Missing Implementation
- **Student API Endpoints**: No endpoints for student listing/access
- **Class API Endpoints**: No endpoints for class management
- **Grade API Endpoints**: No endpoints for grade CRUD operations
- **Business Logic Services**: Limited service layer for core operations
- **Role-based Query Filtering**: No implementation of role-based data filtering

## External Research Summary

### FastAPI RBAC Implementation Patterns (2025)

**Key Findings from app-generator.dev and community resources:**

1. **Dependency Injection Pattern** ⭐ Recommended Approach
   - Use FastAPI's `Depends()` system for permission checking
   - Create reusable permission checker dependencies
   - Inject role requirements at endpoint level

2. **Permission-Based Control**
   - Granular permissions beyond simple roles
   - Database-level query filtering based on user context
   - Token-based authentication with embedded permissions

3. **Multi-tenant Data Access**
   - Query filtering at service layer level
   - Automatic school isolation in database queries
   - Performance optimization with proper indexing

### Modern RBAC Security Practices
1. **Defense in Depth**: Multiple layers of authorization checks
2. **Principle of Least Privilege**: Users access only necessary data
3. **Audit Logging**: Track all data access and modifications
4. **Query-Level Filtering**: Security at database query level, not just endpoints

### FastAPI-Specific Best Practices
1. **Dependency Composition**: Layer multiple security dependencies
2. **Response Model Validation**: Ensure consistent API contracts
3. **Error Handling**: Standardized HTTP status codes and messages
4. **Middleware Integration**: Security middleware for cross-cutting concerns

## Implementation Blueprint

### 2.2.1 Student Management Service & API

**Estimated Time**: 45 minutes

**Service Layer Implementation**:
```python
# app/services/student_service.py
class StudentService:
    def get_students_for_user(self, user: User, db: Session) -> List[Student]:
        """Get students based on user role and assignments."""
        base_query = db.query(Student).filter(Student.school_id == user.school_id)
        
        if user.role == UserRole.FORM_TEACHER:
            # Get assigned classes only
            assigned_class_ids = db.query(TeacherClassAssignment.class_id).filter(
                TeacherClassAssignment.teacher_id == user.id
            ).subquery()
            return base_query.filter(Student.class_id.in_(assigned_class_ids)).all()
        
        elif user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]:
            # All students in school
            return base_query.all()
```

**API Endpoints**:
```python
# app/api/v1/endpoints/students.py
@router.get("/", response_model=List[StudentResponse])
async def list_students(
    current_user: User = Depends(get_current_user),
    school_id: int = Depends(get_current_user_school_id),
    db: Session = Depends(get_db),
):
    """List students based on user role and assignments."""
```

**Key Features**:
- Role-based student filtering at query level
- Multi-tenant isolation enforcement
- Pagination and sorting support
- Performance-optimized queries with eager loading

### 2.2.2 Class Management Service & API

**Estimated Time**: 30 minutes  

**Service Layer Implementation**:
```python
# app/services/class_service.py
class ClassService:
    def get_accessible_classes(self, user: User, db: Session) -> List[Class]:
        """Get classes accessible to user based on role."""
        base_query = db.query(Class).filter(Class.school_id == user.school_id)
        
        if user.role == UserRole.FORM_TEACHER:
            # Only assigned classes
            return db.query(Class).join(TeacherClassAssignment).filter(
                TeacherClassAssignment.teacher_id == user.id,
                Class.school_id == user.school_id
            ).all()
        
        return base_query.all()  # Year heads see all school classes
```

**API Endpoints**:
- `GET /classes` - List accessible classes
- `GET /classes/{class_id}` - Get class details with students
- `GET /classes/{class_id}/students` - List students in class

**Key Features**:
- Teacher assignment-based access control
- Student roster with grade summaries
- Class performance statistics

### 2.2.3 Grade Management Service & API

**Estimated Time**: 45 minutes

**Service Layer Implementation**:
```python
# app/services/grade_service.py
class GradeService:
    def can_edit_student_grades(self, user: User, student_id: int, db: Session) -> bool:
        """Check if user can edit grades for specific student."""
        student = db.query(Student).filter(Student.id == student_id).first()
        if not student or student.school_id != user.school_id:
            return False
            
        if user.role == UserRole.FORM_TEACHER:
            # Check if teacher is assigned to student's class
            assignment = db.query(TeacherClassAssignment).filter(
                TeacherClassAssignment.teacher_id == user.id,
                TeacherClassAssignment.class_id == student.class_id
            ).first()
            return assignment is not None
            
        return user.role in [UserRole.YEAR_HEAD, UserRole.ADMIN]
```

**API Endpoints**:
- `GET /students/{student_id}/grades` - Get student grades by term
- `PUT /students/{student_id}/grades/{term_id}` - Update student grades
- `GET /grades/summary` - Grade summaries for accessible students

**Key Features**:
- Permission checking before grade modifications
- Audit trail with `modified_by_id` tracking
- Grade validation and performance band calculation
- Historical grade comparison

### 2.2.4 Authorization Middleware Enhancement

**Estimated Time**: 15 minutes

**Implementation**:
```python
# app/middleware/rbac_middleware.py
class RBACMiddleware:
    def __init__(self, app):
        self.app = app
    
    async def __call__(self, scope, receive, send):
        # Add automatic school isolation headers
        # Log authorization decisions for auditing
        # Handle authorization errors consistently
```

**Features**:
- Automatic school ID injection into request context
- Authorization decision logging for security auditing
- Consistent error responses for authorization failures

### 2.2.5 Query Filter Integration

**Estimated Time**: 30 minutes

**Implementation Strategy**:
1. **Service Layer Filtering**: All database queries include role-based filters
2. **Dependency Composition**: Layer multiple security dependencies
3. **Performance Optimization**: Use database indexes for multi-tenant queries
4. **Consistent Patterns**: Standardized filtering across all services

## Validation Gates

### Functional Validation
1. **Role-Based Access Testing**:
   - Form teachers see only assigned students ✓
   - Year heads see all school students ✓
   - Cross-school access blocked ✓
   - Assignment-based class access ✓

2. **API Contract Validation**:
   - Consistent response formats ✓
   - Proper HTTP status codes ✓
   - Comprehensive error messages ✓
   - Request validation ✓

3. **Data Integrity Validation**:
   - Multi-tenant isolation ✓
   - Grade modification permissions ✓
   - Audit trail tracking ✓
   - School-level data segregation ✓

### Security Validation
1. **Authorization Testing**:
   - Permission checking at endpoint level ✓
   - Query-level access control ✓
   - CSRF protection on state changes ✓
   - Session validation ✓

2. **Data Access Validation**:
   - No cross-school data leakage ✓
   - Teacher assignment respect ✓
   - Role escalation prevention ✓
   - Input validation and sanitization ✓

### Performance Validation
1. **Query Performance**:
   - Database query optimization ✓
   - Proper index utilization ✓
   - Efficient multi-tenant filtering ✓
   - Pagination support ✓

2. **API Performance**:
   - Response time validation ✓
   - Memory usage optimization ✓
   - Concurrent access handling ✓

### Integration Testing Strategy

**Unit Tests** (Services & Dependencies):
```bash
# Test role-based filtering logic
uv run pytest tests/services/test_student_service.py::test_form_teacher_student_access
uv run pytest tests/services/test_grade_service.py::test_grade_edit_permissions

# Test RBAC dependencies
uv run pytest tests/dependencies/test_rbac.py::test_school_isolation
```

**Integration Tests** (API Endpoints):
```bash
# Test complete API workflows
uv run pytest tests/api/test_students.py::test_role_based_student_listing
uv run pytest tests/api/test_grades.py::test_grade_modification_permissions
```

**Manual Verification** (Full System):
```bash
# Test with real session cookies
curl -H "Cookie: session_id=..." http://localhost:8000/api/v1/students
curl -X PUT -H "Cookie: session_id=..." http://localhost:8000/api/v1/students/1/grades/1
```

## Risk Assessment & Mitigation

### Technical Risks
1. **Query Performance**: Multi-tenant filtering may impact performance
   - **Mitigation**: Comprehensive database indexing, query optimization
   
2. **Complex Role Logic**: Multiple role types with different access patterns
   - **Mitigation**: Centralized service layer logic, comprehensive testing

3. **Data Consistency**: Concurrent grade modifications
   - **Mitigation**: Database transactions, optimistic locking

### Security Risks
1. **Authorization Bypass**: Potential gaps in role checking
   - **Mitigation**: Defense in depth, multiple validation layers
   
2. **Data Leakage**: Cross-school or unauthorized data access
   - **Mitigation**: Query-level filtering, automated testing

3. **Privilege Escalation**: Users accessing unauthorized functions
   - **Mitigation**: Explicit permission checking, audit logging

### Implementation Risks
1. **Complexity**: Building on existing auth foundation
   - **Mitigation**: Leverage established patterns, incremental development
   
2. **Testing Overhead**: Complex role-based scenarios
   - **Mitigation**: Automated test suites, manual verification

## Success Criteria

### Functional Requirements Met ✅
- [ ] Form teachers access only assigned students
- [ ] Year heads access all school students  
- [ ] Grade modification permissions enforced
- [ ] Multi-tenant isolation maintained
- [ ] Teacher class assignments respected
- [ ] Audit trail for all modifications

### Technical Requirements Met ✅
- [ ] FastAPI endpoints with proper RBAC
- [ ] Service layer with role-based filtering
- [ ] Pydantic response models
- [ ] Comprehensive error handling
- [ ] Performance optimization
- [ ] Integration with existing auth system

### Security Requirements Met ✅
- [ ] Authorization at endpoint and query level
- [ ] Input validation and sanitization
- [ ] CSRF protection on state changes
- [ ] Audit logging for security events
- [ ] No cross-school data access
- [ ] Principle of least privilege

## Dependencies & Prerequisites

### Completed Dependencies ✅
- Phase 2.1 Session-Based Authentication
- Database models and relationships
- RBAC dependency injection system
- Security middleware implementation

### External Dependencies
- PostgreSQL database (configured ✅)
- FastAPI framework (configured ✅)
- SQLAlchemy ORM (configured ✅)
- Pydantic validation (configured ✅)

### Development Environment
- Docker Compose setup (ready ✅)
- Database migrations (Alembic ready ✅)
- Testing framework (pytest configured ✅)

## Implementation Checklist

### Phase 2.2.1 - Student Management (45 min)
- [ ] Create `StudentService` with role-based filtering
- [ ] Implement `/api/v1/students` endpoints
- [ ] Add student response models
- [ ] Test role-based access patterns
- [ ] Verify multi-tenant isolation

### Phase 2.2.2 - Class Management (30 min)  
- [ ] Create `ClassService` with assignment checking
- [ ] Implement `/api/v1/classes` endpoints
- [ ] Add teacher assignment validation
- [ ] Test class access permissions
- [ ] Verify student roster access

### Phase 2.2.3 - Grade Management (45 min)
- [ ] Create `GradeService` with edit permissions
- [ ] Implement `/api/v1/grades` endpoints  
- [ ] Add grade modification validation
- [ ] Test grade editing permissions
- [ ] Verify audit trail functionality

### Phase 2.2.4 - Authorization Enhancement (15 min)
- [ ] Add authorization decision logging
- [ ] Enhance error handling consistency
- [ ] Test authorization middleware
- [ ] Verify security event tracking

### Phase 2.2.5 - Integration & Testing (30 min)
- [ ] Run comprehensive test suite
- [ ] Manual verification of role scenarios
- [ ] Performance testing of queries
- [ ] Security validation testing
- [ ] Documentation updates

**Total Estimated Time: 2 hours 45 minutes**

## Conclusion

Phase 2.2 builds upon the solid authentication foundation from Phase 2.1 to deliver the core business APIs with robust role-based access control. The implementation leverages existing RBAC dependencies and focuses on creating secure, performant APIs that enforce proper data access patterns.

Key success factors:
- **Leverage Existing Foundation**: Maximize use of Phase 2.1 RBAC infrastructure
- **Defense in Depth**: Multiple layers of authorization checking
- **Performance Focus**: Efficient queries with proper indexing
- **Testing Strategy**: Comprehensive validation of role-based scenarios

This approach ensures secure, scalable RBAC implementation that meets all assignment requirements while maintaining high code quality and security standards.