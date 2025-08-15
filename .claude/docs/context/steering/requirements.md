# Teacher Report Card System - Final Requirements Document

## Executive Summary
A web-based report card generation system for Singapore primary schools, enabling teachers to create professional term reports by selecting achievements and adding behavioral comments to pre-existing student grade data.

**Scope**: MVP with mock data, 2-page application  
**Users**: Teachers and Head Teachers across three schools  

---

## Functional Requirements

### Core User Stories

#### As a FORM TEACHER:
- **Class-Based Access**: View all students in classes I teach (e.g., Primary 4A, Primary 4B) with their current report status
- **Grade Management**: Input and edit student grades for all subjects
- **Grade Review**: View current and previous term grades for context
- **Achievement Curation**: Select from auto-suggested achievements based on student improvement patterns
- **Comment Addition**: Add behavioral observations and comments
- **Report Generation**: Create, preview, and export professional PDF report cards
- **Report Management**: Edit grades/comments/achievements and regenerate reports as needed

#### As a YEAR HEAD:
- **School-Wide Access**: View ALL students across ALL classes in the school
- **Cross-Class Management**: Generate reports for any student in any class within the school
- **Same Report Capabilities**: Identical report generation workflow as form teachers

### System Capabilities

#### Achievement Auto-Suggestion Engine
```
Trigger Conditions:
- Subject improvement ≥20%: "Significant improvement in [Subject]"
- Subject improvement ≥10%: "Steady progress in [Subject]" 
- Current grade ≥90: "Excellence in [Subject]"
- Current grade ≥80: "Strong performance in [Subject]"
- Overall improvement ≥15%: "Overall academic improvement"
```

#### Performance Band Calculation
```
Overall Band = Average of (English + Math + Science + Mother Tongue)
- Outstanding: ≥85 average
- Good: ≥70 average  
- Satisfactory: ≥55 average
- Needs Improvement: <55 average
```

---

## Business Requirements

### Academic Context
- **Location**: Singapore Primary Schools
- **Academic Structure**: 4 terms per year
- **Subjects**: English, Mathematics, Science, Mother Tongue
- **Grade Levels**: Primary 1-6 (mock data will use representative levels)

### Data Governance
- **Grades**: Editable by authorized teachers (form teachers for their classes, year heads for all school classes)
- **Comments**: Editable by report creator
- **Achievements**: Selectable/deselectable by report creator
- **Multi-tenancy**: Complete school isolation - no cross-school data access

### User Access Control
```
Form Teacher Permissions:
- Read: Students in classes they teach, grades, achievement suggestions
- Write: Grades, achievement selections, behavioral comments for their class students

Year Head Permissions:  
- Read: ALL students in their school across all classes, all data types
- Write: Grades, achievements, comments for any student in any class in school
```

---

## Technical Requirements

### Architecture
- **Pattern**: Modular Monolith (future microservices-ready)
- **Scalability**: Horizontal scaling capability
- **Message Queues**: Architecture ready for async PDF generation (future enhancement)

### Technology Stack
- **Backend**: Python with FastAPI
- **Frontend**: TypeScript with Next.js
- **Database**: PostgreSQL with Alembic migrations
- **Containerization**: Docker Compose for full stack deployment

### Security Requirements
- **Authentication**: Session-based with username/password
- **Authorization**: Role-Based Access Control (RBAC)
- **Session Management**: 30-minute session expiry with PostgreSQL session store
- **Input Validation**: Comprehensive server-side validation
- **SQL Security**: ORM-based queries (SQLAlchemy) with parameterized statements
- **CSRF Protection**: Anti-CSRF tokens for state-changing operations

### Performance Requirements
- **Dashboard Load Time**: <2 seconds
- **Report Generation**: <5 seconds
- **Concurrent Users**: Support multiple simultaneous users
- **PDF Export**: Efficient generation and download

---

## User Interface Requirements

### Page 1: Dashboard
**Purpose**: Overview of all accessible students and their report status

**Components**:
- **Class-Based Navigation**: 
  - **Form Teachers**: List of classes they teach (e.g., "Primary 4A", "Primary 4B")
  - **Year Heads**: List of all classes in the school
- **Class Overview**: Selected class header with student count and completion stats
- Student list within selected class showing: name, student ID, and current term status
- Status indicators: "Report Generated" | "Report Pending"
- Click student to navigate to report generation

**Responsive Design**: Mobile-friendly layout for tablet use

### Page 2: Report Generation
**Purpose**: Create and export student report cards

**Sections**:
1. **Student Header**: Name, class, term information
2. **Grades Management (Editable)**:
   - Input/edit current term grades for all 4 subjects
   - View previous term grades for comparison
   - Automatic calculation of overall performance band
3. **Achievement Selection (Interactive)**:
   - Auto-suggested achievements with improvement context
   - Checkbox interface for selection/deselection
4. **Comments Section (Editable)**:
   - Text area for behavioral observations
   - Character limit enforcement
5. **Report Actions**:
   - Generate PDF (simple HTML-to-PDF conversion)
   - Export/download functionality
   - Save and return to dashboard

---

## Data Requirements

### Mock Data Specification
Following assignment requirements with multi-school context

**Data Set**:
- **3 Schools**: Riverside Primary School, Hillview Primary School, Eastwood Primary School
- **12 Students Total**: 4 students per school (as per clarification)
- **Class Structure**:
  - **Riverside Primary**: Primary 4A (4 students)
  - **Hillview Primary**: Primary 4B (4 students)  
  - **Eastwood Primary**: Primary 4C (4 students)
- **Users**: 
  - **Form Teachers**: 1 per class (3 total - each teaching one specific class)
  - **Year Heads**: 1 per school (3 total - managing all classes in their school)
- **Historical Data**: 2-3 terms of grade history for achievement auto-suggestions
- **Achievement Categories**: 12-15 predefined achievement templates

### Database Schema (Core Entities)
```sql
-- Multi-tenant structure
schools (id, name, code)
users (id, username, password_hash, role, school_id)
classes (id, name, year_level, school_id)
teacher_class_assignments (teacher_id, class_id, academic_year)
students (id, name, student_id, class_id, school_id)

-- Academic data  
terms (id, name, year, quarter)
subjects (id, name) -- English, Math, Science, Mother Tongue
grades (id, student_id, subject_id, term_id, grade_value, created_at)

-- Report components
achievement_categories (id, name, description, trigger_conditions)
report_components (id, student_id, term_id, teacher_id, behavioral_comments, selected_achievements, updated_at)
```

### Sample Data Characteristics
- **Realistic Names**: Singapore-appropriate student and teacher names
- **Class Structure**: 
  - **Riverside Primary**: Primary 4A (4 students) - Form Teacher: Ms. Tan + Year Head: Mr. Lim
  - **Hillview Primary**: Primary 4B (4 students) - Form Teacher: Ms. Wong + Year Head: Mrs. Kumar  
  - **Eastwood Primary**: Primary 4C (4 students) - Form Teacher: Mr. Chen + Year Head: Ms. Lee
- **Access Patterns**:
  - Form Teachers can only access their specific class students
  - Year Heads can access ALL students across all classes in their school
- **Grade Patterns**: Varied performance showing improvement, decline, and consistency
- **Achievement Triggers**: Data designed to test percentage-based auto-suggestion algorithm
- **Cross-Term Data**: Sufficient history to demonstrate percentage improvement tracking

---

## Testing Requirements

### Test Categories
- **Unit Tests**: Core business logic (achievement suggestions, performance bands)
- **Integration Tests**: API endpoints with authentication and authorization
- **Database Tests**: CRUD operations and data integrity
- **Security Tests**: RBAC enforcement, input validation, SQL injection prevention
- **Edge Case Tests**: Non-existent students, missing grades, cross-school access attempts

### Testing Approach (Simplified for 6-day Timeline)
- Focus on critical path testing
- Prioritize security test coverage
- Target essential functionality over coverage percentage
- Manual testing for UI edge cases

---

## Deployment Requirements

### Containerization
- **Docker Compose**: Single-command deployment (`docker-compose up`)
- **Service Isolation**: Separate containers for frontend, backend, database
- **Environment Configuration**: Configurable secrets and settings
- **Development vs Production**: Environment-specific configurations

### Documentation
- **README.md**: Setup instructions, architecture overview, API documentation
- **API Documentation**: OpenAPI/Swagger specification
- **Database Documentation**: Schema diagrams and migration guides
- **Security Documentation**: Security measures and compliance notes

---

## Success Criteria

### Functional Success
- [ ] Teachers can generate professional report cards for their students
- [ ] Head teachers can access all school students
- [ ] Achievement auto-suggestions work based on grade improvements
- [ ] PDF reports contain all required elements with proper formatting
- [ ] School isolation is maintained (no cross-school data access)

### Technical Success
- [ ] System handles concurrent users without conflicts
- [ ] All security requirements implemented and tested
- [ ] Edge cases handled gracefully with appropriate error messages
- [ ] Complete test coverage for critical functionality
- [ ] Single-command deployment works reliably

### Business Success
- [ ] Report generation workflow is intuitive for teachers
- [ ] System performance meets stated requirements
- [ ] Generated reports are professional and print-ready
- [ ] Achievement suggestions provide valuable insights for teachers

---

## Future Enhancements (Out of Scope)
- Message queue integration for async PDF generation
- Parent/student portal access
- Email notification system
- Advanced reporting and analytics
- Mobile app development
- Integration with existing Student Information Systems