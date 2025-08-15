# PRP: Data Seeding & Mock Data Enhancement (Task 1.3)

## Feature Overview

Enhance the existing seed_data.py to populate the database with comprehensive realistic test data for the Teacher Report Card Assistant, including 3 schools, 12 students, historical grades across 3 terms, and 15 achievement categories with trigger conditions.

## Context & Background

### Current State Analysis
The existing `backend/src/app/core/seed_data.py` provides basic seeding but lacks:
- Historical grade data across multiple terms 
- Varied grade patterns (improvement/decline/stable)
- Complete achievement categories (only 3 exist, need 15)
- Realistic grade distributions for testing achievement triggers
- Comprehensive Singapore student names

### Business Requirements
From `/home/shiyun/Documents/assessment/report-card-assistant/.claude/docs/context/steering/requirements.md`:
- **Multi-school context**: 3 schools with complete isolation
- **Achievement Auto-Suggestion Engine**: Must trigger based on improvement patterns
- **Performance Band Calculation**: Test data must validate band calculations
- **RBAC Testing**: Data must support form teacher vs year head access patterns

### Technical Foundation
From existing codebase analysis:
- **Models**: Complete SQLAlchemy 2.0 models exist with proper relationships
- **Environment**: UV + Docker containerized development 
- **Security**: Environment variable-based password management
- **Validation**: Ruff, MyPy, and pytest integration

## Implementation Blueprint

### 1. Enhanced Data Structure

#### School & User Distribution
```python
# Existing structure (keep unchanged):
schools = [
    School(name="Riverside Primary School", code="RPS", address="123 Riverside Road"),
    School(name="Hillview Primary School", code="HPS", address="456 Hillview Avenue"), 
    School(name="Eastwood Primary School", code="EPS", address="789 Eastwood Street"),
]

users = [
    # Form Teachers (one per school)
    ("Ms. Tan", "tan@rps.edu.sg", UserRole.FORM_TEACHER, schools[0]),
    ("Ms. Wong", "wong@hps.edu.sg", UserRole.FORM_TEACHER, schools[1]),
    ("Mr. Chen", "chen@eps.edu.sg", UserRole.FORM_TEACHER, schools[2]),
    # Year Heads (one per school)
    ("Mr. Lim", "lim@rps.edu.sg", UserRole.YEAR_HEAD, schools[0]),
    ("Mrs. Kumar", "kumar@hps.edu.sg", UserRole.YEAR_HEAD, schools[1]),
    ("Ms. Lee", "lee@eps.edu.sg", UserRole.YEAR_HEAD, schools[2]),
]
```

#### Singapore Student Names (Enhanced)
Replace existing basic names with authentic Singapore names:
```python
singapore_student_names = [
    # Riverside Primary (4A) - Chinese majority with diversity
    ("Wei Jie", "Tan"), ("Hui Min", "Lim"), ("Kai Rui", "Chen"), ("Mei Hua", "Wong"),
    # Hillview Primary (4B) - Mixed ethnic representation  
    ("Arjun", "Kumar"), ("Priya", "Sharma"), ("Zhi Hao", "Ong"), ("Siti", "Hashim"),
    # Eastwood Primary (4C) - Diverse Singapore names
    ("Marcus", "Teo"), ("Aisyah", "Rahman"), ("Jun Ming", "Low"), ("Kavitha", "Raj")
]
```

#### Subjects & Terms Structure
```python
subjects = [
    Subject(name="English", code="ENG", sort_order=1),
    Subject(name="Mathematics", code="MATH", sort_order=2), 
    Subject(name="Science", code="SCI", sort_order=3),
    Subject(name="Chinese", code="CHI", sort_order=4),  # Mother Tongue
]

# Create 3 terms per school for historical data
terms_per_school = [
    Term(name="Term 1 2024", academic_year=2024, term_number=1, school_id=school.id),
    Term(name="Term 2 2024", academic_year=2024, term_number=2, school_id=school.id), 
    Term(name="Term 3 2024", academic_year=2024, term_number=3, school_id=school.id),
]
```

### 2. Grade Pattern Generation Strategy

#### Improvement Patterns (to trigger achievements)
```python
grade_patterns = {
    'significant_improvement': {
        'term_1': [65, 70, 75, 68],  # English, Math, Science, Chinese
        'term_2': [70, 75, 80, 72], 
        'term_3': [85, 88, 92, 85],  # 20%+ improvement triggers "Significant improvement"
    },
    'steady_progress': {
        'term_1': [75, 80, 70, 78],
        'term_2': [78, 82, 75, 80],
        'term_3': [82, 85, 80, 83],  # 10-19% improvement triggers "Steady progress"
    },
    'excellence_achiever': {
        'term_1': [85, 88, 82, 87],
        'term_2': [88, 90, 86, 89],
        'term_3': [90, 92, 90, 91],  # ≥90 triggers "Excellence" achievements
    },
    'stable_performer': {
        'term_1': [78, 75, 80, 77],
        'term_2': [79, 76, 81, 78], 
        'term_3': [80, 77, 82, 79],  # Minimal change, tests stable performance
    }
}
```

#### Performance Band Testing
Ensure data validates performance band calculation:
- **Outstanding**: ≥85 average (excellence_achiever pattern)
- **Good**: ≥70 average (steady_progress, stable_performer)  
- **Satisfactory**: ≥55 average (early terms of significant_improvement)
- **Needs Improvement**: <55 average (create one struggling student pattern)

### 3. Achievement Categories (Expand to 15)

Based on requirements trigger conditions:
```python
achievement_categories = [
    # Subject-specific improvements (4 subjects × 2 levels = 8)
    AchievementCategory(
        name="Significant improvement in English",
        description="20% or more improvement in English",
        min_improvement_percent=20.0,
        subject_filter="english"
    ),
    AchievementCategory(
        name="Steady progress in English", 
        description="10-19% improvement in English",
        min_improvement_percent=10.0,
        max_improvement_percent=19.9,
        subject_filter="english"
    ),
    # ... repeat for Math, Science, Chinese
    
    # Excellence categories (4 subjects = 4)
    AchievementCategory(
        name="Excellence in English",
        description="Scored 90 or above in English", 
        min_score=90.0,
        subject_filter="english"
    ),
    # ... repeat for other subjects
    
    # Overall performance (2)
    AchievementCategory(
        name="Overall academic improvement",
        description="15% or more overall improvement",
        min_improvement_percent=15.0,
        subject_filter="overall"
    ),
    AchievementCategory(
        name="Consistent high performance",
        description="Maintained excellence across all subjects",
        min_score=85.0,
        subject_filter="overall"
    ),
    
    # Behavioral/Additional (1)
    AchievementCategory(
        name="Outstanding effort and participation",
        description="Exceptional classroom engagement",
        category_type="behavioral"
    )
]
```

## Code Examples from Existing Patterns

### Database Connection Pattern (from existing seed_data.py)
```python
from app.core.database import SessionLocal
from app.models import (
    AchievementCategory, Class, Grade, School, Student, 
    Subject, TeacherClassAssignment, Term, User, UserRole,
)

def enhanced_seed_database():
    """Enhanced seed database with comprehensive test data."""
    db = SessionLocal()
    try:
        # Check if data already exists (keep existing pattern)
        if db.query(School).first():
            print("Database already seeded")
            return
        # Implementation continues...
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()
```

### Security Pattern (from existing code)
```python
from passlib.context import CryptContext
import os

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Use environment variable for default password (existing pattern)
hashed_password=pwd_context.hash(
    os.getenv("SEED_DEFAULT_PASSWORD", "CHANGE_ME_INSECURE_DEV_ONLY")
)
```

## Implementation Steps (Execution Order)

### Step 1: Enhance Student Names & Patterns
- Replace basic student names with authentic Singapore names
- Define grade pattern templates for different improvement types
- Ensure ethnic diversity representation

### Step 2: Create Grade History
- Generate grades for all 12 students across 3 terms
- Apply different improvement patterns to different students
- Ensure grade constraints (0-100, decimal precision) are respected

### Step 3: Expand Achievement Categories  
- Create 15 achievement categories with proper trigger conditions
- Include subject-specific and overall performance achievements
- Add behavioral/effort categories

### Step 4: Multi-Tenant Validation
- Verify each school has complete data isolation
- Test that cross-school data access is impossible
- Validate teacher-class assignments are properly configured

### Step 5: Achievement Trigger Testing
- Create specific grade patterns that trigger each achievement type  
- Verify percentage improvement calculations work correctly
- Test edge cases (exactly 20% improvement, 90.0 scores, etc.)

## Security Considerations

### Environment Variables
From `backend/src/app/core/seed_data.py` pattern:
```python
# Always use environment variables for passwords
SEED_DEFAULT_PASSWORD = os.getenv("SEED_DEFAULT_PASSWORD", "CHANGE_ME_INSECURE_DEV_ONLY")
```

### Multi-Tenant Isolation
Ensure each school's data is completely isolated:
- All students belong to correct school_id
- All classes belong to correct school_id  
- All terms belong to correct school_id
- Teachers can only access their school's data

## Dependencies & Context

### Environment Setup (from learnings/1_2_docker_environment_management.md)
- Use `.env.development` for development credentials
- Run all commands in Docker containers for consistency
- Use UV for Python package management

### Model Dependencies (from existing codebase)
```python
# Required imports (existing pattern)
from app.models import (
    AchievementCategory, Class, Grade, School, Student,
    Subject, TeacherClassAssignment, Term, User, UserRole,
)
from app.core.database import SessionLocal
```

### Testing Framework
```python
# Achievement trigger testing example
def verify_achievement_triggers(db_session):
    """Verify that grade patterns trigger expected achievements."""
    # Test 20%+ improvement triggers "Significant improvement"
    # Test 90+ score triggers "Excellence" 
    # Test overall 15%+ triggers "Overall academic improvement"
```

## Validation Gates (Must Pass)

### Syntax & Style Validation
```bash
# Run in Docker container (from Docker learnings)
docker run --rm --env-file .env.development backend_image bash -c "
  cd /app &&
  uv run ruff check --fix src/ &&
  uv run ruff format src/ &&
  uv run mypy src/
"
```

### Database Integration Testing
```bash
# Fresh database setup and seeding
docker compose down db && docker volume rm report-card-assistant_postgres_data
docker compose up -d db
sleep 5  # Allow database to initialize

# Run enhanced seeding
docker run --rm --env-file .env.development --network report-card-assistant_default backend_image bash -c "
  cd /app &&
  uv run alembic upgrade head &&
  uv run python -m app.core.seed_data
"
```

### Data Verification Tests
```bash
# Verify seeded data meets requirements
docker run --rm --env-file .env.development --network report-card-assistant_default backend_image bash -c "
  cd /app &&
  uv run python -c '
from app.core.database import SessionLocal
from app.models import School, Student, Grade, AchievementCategory

db = SessionLocal()
print(f\"Schools: {db.query(School).count()}\")
print(f\"Students: {db.query(Student).count()}\") 
print(f\"Grades: {db.query(Grade).count()}\")
print(f\"Achievement Categories: {db.query(AchievementCategory).count()}\")

# Verify grade patterns exist
grades_per_student = db.query(Grade).count() / db.query(Student).count()
print(f\"Average grades per student: {grades_per_student}\")

# Should output: Schools: 3, Students: 12, Grades: 144 (12×4×3), Achievement Categories: 15
db.close()
  '
"
```

### Unit Testing
```bash
# Run existing and new tests
docker run --rm --env-file .env.development --network report-card-assistant_default backend_image bash -c "
  cd /app &&
  uv run pytest tests/ -v
"
```

## Expected Outcomes

### Data Completeness
- **3 Schools**: Riverside, Hillview, Eastwood Primary Schools
- **12 Students**: 4 per school with authentic Singapore names
- **144 Grades**: 12 students × 4 subjects × 3 terms
- **15 Achievement Categories**: Complete trigger condition coverage
- **6 Users**: 3 form teachers + 3 year heads with proper assignments

### Achievement Trigger Coverage
- At least 2 students with 20%+ improvement (significant improvement)
- At least 2 students with 10-19% improvement (steady progress)  
- At least 2 students with 90+ scores (excellence)
- At least 1 student with 15%+ overall improvement
- Grade patterns that test all performance bands

### Multi-Tenant Validation
- Each school completely isolated
- Form teachers can only see their assigned class
- Year heads can see all classes in their school
- Cross-school access impossible

## Risk Mitigation

### Database State Management
- Always check if data exists before seeding (existing pattern)
- Use transactions to ensure atomicity
- Provide rollback capability on errors

### Grade Calculation Edge Cases  
- Test exactly 20.0% improvement
- Test exactly 90.0 scores
- Handle decimal precision correctly
- Verify constraint validation (0-100 range)

### Environment Consistency
- Use Docker containers for all operations
- Apply environment variables for all credentials
- Follow existing UV and justfile patterns

## Quality Metrics

**PRP Confidence Score: 9/10**

### Strengths
- ✅ Comprehensive existing codebase analysis
- ✅ Clear implementation patterns from current code
- ✅ Detailed grade pattern strategy for achievement testing
- ✅ Executable validation gates with Docker
- ✅ Complete security and environment context
- ✅ Multi-tenant isolation strategy
- ✅ Authentic Singapore cultural context

### Areas for Validation During Implementation
- Achievement trigger algorithm exact thresholds
- Database constraint validation behavior
- Cross-term improvement calculation precision

This PRP provides complete context for one-pass implementation success by including existing code patterns, comprehensive requirements, and executable validation steps.