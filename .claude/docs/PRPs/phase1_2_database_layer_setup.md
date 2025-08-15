# PRP: Database Layer Setup for Teacher Report Card Assistant

## Overview
Implement the complete database layer for a multi-tenant report card generation system using SQLAlchemy 2.0, PostgreSQL, and Alembic migrations. The system will support 3 schools with role-based access control (form teachers vs year heads).

## Context and Research Findings

### Existing Codebase Structure
The project already has a foundational structure in place:

**Key Files:**
- `backend/src/app/core/database.py` - Database engine setup with connection pooling
- `backend/src/app/core/config.py` - Settings management with Pydantic
- `backend/src/app/models/base.py` - BaseModel with common fields (id, created_at, updated_at, is_active)
- `backend/alembic/env.py` - Alembic configuration ready for migrations
- `backend/pyproject.toml` - Dependencies including SQLAlchemy 2.0.43 and Alembic 1.16.4

**Current Database Configuration:**
```python
# From backend/src/app/core/database.py
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    echo=settings.DEBUG,
)
```

### SQLAlchemy 2.0 Best Practices

**Use Modern Declarative Style with Type Hints:**
```python
from typing import List, Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship

class School(BaseModel):
    __tablename__ = "schools"
    
    name: Mapped[str] = mapped_column(String(100))
    users: Mapped[List["User"]] = relationship(back_populates="school")
```

**Key Documentation:**
- SQLAlchemy 2.0 Basic Relationships: https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html
- Declarative Mapping Styles: https://docs.sqlalchemy.org/en/20/orm/declarative_styles.html
- Alembic Auto-generation: https://alembic.sqlalchemy.org/en/latest/autogenerate.html

### Multi-Tenant Security Patterns

**Row-Level Security Implementation:**
- Every table with user data must include `school_id` for tenant isolation
- Use SQLAlchemy query filters to enforce school-based access
- Consider PostgreSQL RLS for additional security layer
- Reference: https://adityamattos.com/multi-tenancy-in-python-fastapi-and-sqlalchemy-using-postgres-row-level-security

### Security Requirements (from SECURITY.md)
- Never commit credentials to version control
- SQL injection prevention via SQLAlchemy ORM (parameterized queries)
- Multi-tenant data isolation
- Input validation with Pydantic
- Role-based access control (RBAC)

## Implementation Blueprint

### Phase 1: Create Model Files
```
backend/src/app/models/
├── __init__.py        # Import all models
├── base.py           # Already exists - BaseModel
├── school.py         # School model
├── user.py           # User model with roles
├── student.py        # Student model
├── class_model.py    # Class model (avoid 'class' keyword)
├── term.py           # Academic terms
├── subject.py        # Subjects
├── grade.py          # Grade records
├── achievement.py    # Achievement categories
└── report.py         # Report components
```

### Phase 2: Model Relationships
```
School (1) --> (*) User
School (1) --> (*) Class
School (1) --> (*) Student
School (1) --> (*) Term

User (1) --> (*) TeacherClassAssignment
Class (1) --> (*) Student
Class (1) --> (*) TeacherClassAssignment

Student (1) --> (*) Grade
Student (1) --> (*) ReportCard

Term (1) --> (*) Grade
Term (1) --> (*) ReportCard

Subject (1) --> (*) Grade
Grade (*) --> (1) Student

ReportCard (1) --> (*) Achievement
```

### Phase 3: Database Indexes
- school_id on all tenant tables (for multi-tenant queries)
- user.email (unique constraint)
- student.student_id + school_id (composite unique)
- grade.student_id + term_id + subject_id (composite unique)
- Performance indexes on frequently queried fields

## Detailed Implementation Tasks

### Task 1: Update Model Imports
**File:** `backend/src/app/models/__init__.py`
```python
from app.models.base import BaseModel
from app.models.school import School
from app.models.user import User, UserRole
from app.models.class_model import Class
from app.models.student import Student
from app.models.term import Term
from app.models.subject import Subject
from app.models.grade import Grade
from app.models.achievement import AchievementCategory, Achievement
from app.models.report import ReportCard, ReportComponent
from app.models.teacher_assignment import TeacherClassAssignment

__all__ = [
    "BaseModel", "School", "User", "UserRole", "Class", "Student",
    "Term", "Subject", "Grade", "AchievementCategory", "Achievement",
    "ReportCard", "ReportComponent", "TeacherClassAssignment"
]
```

### Task 2: Create School Model
**File:** `backend/src/app/models/school.py`
```python
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class School(BaseModel):
    __tablename__ = "schools"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    code: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    address: Mapped[str] = mapped_column(String(255))
    
    # Relationships
    users: Mapped[List["User"]] = relationship(back_populates="school", cascade="all, delete-orphan")
    classes: Mapped[List["Class"]] = relationship(back_populates="school", cascade="all, delete-orphan")
    students: Mapped[List["Student"]] = relationship(back_populates="school", cascade="all, delete-orphan")
    terms: Mapped[List["Term"]] = relationship(back_populates="school", cascade="all, delete-orphan")
```

### Task 3: Create User Model with Roles
**File:** `backend/src/app/models/user.py`
```python
from typing import List, Optional
from enum import Enum
from sqlalchemy import String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class UserRole(str, Enum):
    FORM_TEACHER = "form_teacher"
    YEAR_HEAD = "year_head"
    ADMIN = "admin"

class User(BaseModel):
    __tablename__ = "users"
    
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False)
    
    # Multi-tenant field
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)
    
    # Relationships
    school: Mapped["School"] = relationship(back_populates="users")
    class_assignments: Mapped[List["TeacherClassAssignment"]] = relationship(
        back_populates="teacher", cascade="all, delete-orphan"
    )
```

### Task 4: Create Class Model
**File:** `backend/src/app/models/class_model.py`
```python
from typing import List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Class(BaseModel):
    __tablename__ = "classes"
    
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Primary 4A"
    level: Mapped[int] = mapped_column(nullable=False)  # e.g., 4 for Primary 4
    section: Mapped[str] = mapped_column(String(10), nullable=False)  # e.g., "A"
    academic_year: Mapped[int] = mapped_column(nullable=False)  # e.g., 2024
    
    # Multi-tenant field
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)
    
    # Relationships
    school: Mapped["School"] = relationship(back_populates="classes")
    students: Mapped[List["Student"]] = relationship(back_populates="class_obj", cascade="all, delete-orphan")
    teacher_assignments: Mapped[List["TeacherClassAssignment"]] = relationship(
        back_populates="class_obj", cascade="all, delete-orphan"
    )
```

### Task 5: Create Student Model
**File:** `backend/src/app/models/student.py`
```python
from typing import List, Optional
from datetime import date
from sqlalchemy import String, ForeignKey, Date, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Student(BaseModel):
    __tablename__ = "students"
    __table_args__ = (
        UniqueConstraint('student_id', 'school_id', name='_student_school_uc'),
    )
    
    student_id: Mapped[str] = mapped_column(String(20), nullable=False)  # School's student ID
    first_name: Mapped[str] = mapped_column(String(50), nullable=False)
    last_name: Mapped[str] = mapped_column(String(50), nullable=False)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date)
    gender: Mapped[Optional[str]] = mapped_column(String(10))
    
    # Multi-tenant and foreign keys
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False, index=True)
    
    # Relationships
    school: Mapped["School"] = relationship(back_populates="students")
    class_obj: Mapped["Class"] = relationship(back_populates="students")
    grades: Mapped[List["Grade"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    report_cards: Mapped[List["ReportCard"]] = relationship(back_populates="student", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"
```

### Task 6: Create Term Model
**File:** `backend/src/app/models/term.py`
```python
from typing import List
from datetime import date
from sqlalchemy import String, ForeignKey, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Term(BaseModel):
    __tablename__ = "terms"
    
    name: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "Term 1 2024"
    academic_year: Mapped[int] = mapped_column(nullable=False)
    term_number: Mapped[int] = mapped_column(nullable=False)  # 1, 2, 3, or 4
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    
    # Multi-tenant field
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), nullable=False, index=True)
    
    # Relationships
    school: Mapped["School"] = relationship(back_populates="terms")
    grades: Mapped[List["Grade"]] = relationship(back_populates="term", cascade="all, delete-orphan")
    report_cards: Mapped[List["ReportCard"]] = relationship(back_populates="term", cascade="all, delete-orphan")
```

### Task 7: Create Subject Model
**File:** `backend/src/app/models/subject.py`
```python
from typing import List
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Subject(BaseModel):
    __tablename__ = "subjects"
    
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(10), unique=True, nullable=False)
    
    # Relationships
    grades: Mapped[List["Grade"]] = relationship(back_populates="subject", cascade="all, delete-orphan")
```

### Task 8: Create Grade Model
**File:** `backend/src/app/models/grade.py`
```python
from typing import Optional
from decimal import Decimal
from sqlalchemy import ForeignKey, DECIMAL, UniqueConstraint, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class Grade(BaseModel):
    __tablename__ = "grades"
    __table_args__ = (
        UniqueConstraint('student_id', 'term_id', 'subject_id', name='_student_term_subject_uc'),
        CheckConstraint('score >= 0 AND score <= 100', name='_score_range_check'),
    )
    
    score: Mapped[Decimal] = mapped_column(DECIMAL(5, 2), nullable=False)
    
    # Foreign keys
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id"), nullable=False, index=True)
    subject_id: Mapped[int] = mapped_column(ForeignKey("subjects.id"), nullable=False, index=True)
    
    # Track who last modified
    modified_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    
    # Relationships
    student: Mapped["Student"] = relationship(back_populates="grades")
    term: Mapped["Term"] = relationship(back_populates="grades")
    subject: Mapped["Subject"] = relationship(back_populates="grades")
    modified_by: Mapped[Optional["User"]] = relationship()
```

### Task 9: Create Achievement Models
**File:** `backend/src/app/models/achievement.py`
```python
from typing import List, Optional
from sqlalchemy import String, Text, DECIMAL, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class AchievementCategory(BaseModel):
    __tablename__ = "achievement_categories"
    
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Trigger conditions
    min_improvement_percent: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    min_score: Mapped[Optional[float]] = mapped_column(DECIMAL(5, 2))
    
    # Relationships
    achievements: Mapped[List["Achievement"]] = relationship(back_populates="category", cascade="all, delete-orphan")

class Achievement(BaseModel):
    __tablename__ = "achievements"
    
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Foreign keys
    category_id: Mapped[int] = mapped_column(ForeignKey("achievement_categories.id"), nullable=False)
    report_card_id: Mapped[int] = mapped_column(ForeignKey("report_cards.id"), nullable=False)
    
    # Relationships
    category: Mapped["AchievementCategory"] = relationship(back_populates="achievements")
    report_card: Mapped["ReportCard"] = relationship(back_populates="achievements")
```

### Task 10: Create Report Models
**File:** `backend/src/app/models/report.py`
```python
from typing import List, Optional
from enum import Enum
from sqlalchemy import String, Text, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class PerformanceBand(str, Enum):
    OUTSTANDING = "outstanding"
    GOOD = "good"
    SATISFACTORY = "satisfactory"
    NEEDS_IMPROVEMENT = "needs_improvement"

class ReportCard(BaseModel):
    __tablename__ = "report_cards"
    
    # Performance data
    performance_band: Mapped[Optional[PerformanceBand]] = mapped_column(SQLEnum(PerformanceBand))
    overall_average: Mapped[Optional[float]] = mapped_column()
    
    # Comments
    behavioral_comment: Mapped[Optional[str]] = mapped_column(Text)
    teacher_comment: Mapped[Optional[str]] = mapped_column(Text)
    
    # PDF storage
    pdf_path: Mapped[Optional[str]] = mapped_column(String(255))
    
    # Foreign keys
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"), nullable=False, index=True)
    term_id: Mapped[int] = mapped_column(ForeignKey("terms.id"), nullable=False, index=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    
    # Relationships
    student: Mapped["Student"] = relationship(back_populates="report_cards")
    term: Mapped["Term"] = relationship(back_populates="report_cards")
    created_by: Mapped["User"] = relationship()
    achievements: Mapped[List["Achievement"]] = relationship(back_populates="report_card", cascade="all, delete-orphan")
    components: Mapped[List["ReportComponent"]] = relationship(back_populates="report_card", cascade="all, delete-orphan")

class ReportComponent(BaseModel):
    __tablename__ = "report_components"
    
    component_type: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., "header", "grades", "achievements"
    content: Mapped[Optional[str]] = mapped_column(Text)
    position: Mapped[int] = mapped_column(nullable=False)
    
    # Foreign key
    report_card_id: Mapped[int] = mapped_column(ForeignKey("report_cards.id"), nullable=False)
    
    # Relationships
    report_card: Mapped["ReportCard"] = relationship(back_populates="components")
```

### Task 11: Create Teacher Assignment Model
**File:** `backend/src/app/models/teacher_assignment.py`
```python
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import BaseModel

class TeacherClassAssignment(BaseModel):
    __tablename__ = "teacher_class_assignments"
    __table_args__ = (
        UniqueConstraint('teacher_id', 'class_id', name='_teacher_class_uc'),
    )
    
    # Foreign keys
    teacher_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False, index=True)
    
    # Relationships
    teacher: Mapped["User"] = relationship(back_populates="class_assignments")
    class_obj: Mapped["Class"] = relationship(back_populates="teacher_assignments")
```

### Task 12: Create Initial Migration
```bash
# From backend directory
cd backend

# Create initial migration
uv run alembic revision --autogenerate -m "Initial database schema with all models"

# Review the generated migration file in alembic/versions/
# Ensure all tables, indexes, and constraints are included

# Apply the migration
uv run alembic upgrade head
```

### Task 13: Create Seed Data Script
**File:** `backend/src/app/core/seed_data.py`
```python
from datetime import date, datetime
from decimal import Decimal
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models import *

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed_database():
    """Seed database with initial data for 3 schools."""
    db = SessionLocal()
    try:
        # Check if data already exists
        if db.query(School).first():
            print("Database already seeded")
            return
        
        # Create schools
        schools = [
            School(name="Riverside Primary School", code="RPS", address="123 Riverside Road"),
            School(name="Hillview Primary School", code="HPS", address="456 Hillview Avenue"),
            School(name="Eastwood Primary School", code="EPS", address="789 Eastwood Street"),
        ]
        db.add_all(schools)
        db.commit()
        
        # Create subjects
        subjects = [
            Subject(name="English", code="ENG"),
            Subject(name="Mathematics", code="MATH"),
            Subject(name="Science", code="SCI"),
            Subject(name="Chinese", code="CHI"),
        ]
        db.add_all(subjects)
        db.commit()
        
        # Create users (teachers)
        users_data = [
            ("Ms. Tan", "tan@rps.edu.sg", UserRole.FORM_TEACHER, schools[0]),
            ("Ms. Wong", "wong@hps.edu.sg", UserRole.FORM_TEACHER, schools[1]),
            ("Mr. Chen", "chen@eps.edu.sg", UserRole.FORM_TEACHER, schools[2]),
            ("Mr. Lim", "lim@rps.edu.sg", UserRole.YEAR_HEAD, schools[0]),
            ("Mrs. Kumar", "kumar@hps.edu.sg", UserRole.YEAR_HEAD, schools[1]),
            ("Ms. Lee", "lee@eps.edu.sg", UserRole.YEAR_HEAD, schools[2]),
        ]
        
        users = []
        for full_name, email, role, school in users_data:
            user = User(
                full_name=full_name,
                username=email.split("@")[0],
                email=email,
                hashed_password=pwd_context.hash(os.getenv("SEED_DEFAULT_PASSWORD", "changeme")),  # From environment
                role=role,
                school_id=school.id
            )
            users.append(user)
        db.add_all(users)
        db.commit()
        
        # Create classes and students for each school
        student_names = [
            ("Wei Jie", "Tan"), ("Hui Min", "Lim"), ("Kai Xuan", "Wong"), ("Jia Ying", "Chen"),
            ("Zhi Wei", "Lee"), ("Xin Yi", "Ng"), ("Jun Hao", "Ong"), ("Mei Ling", "Koh"),
            ("Hao Ran", "Sim"), ("Yu Ting", "Goh"), ("Jing Wen", "Teo"), ("Ming Yang", "Low"),
        ]
        
        class_idx = 0
        for school_idx, school in enumerate(schools):
            # Create class
            class_obj = Class(
                name=f"Primary 4{chr(65 + school_idx)}",  # 4A, 4B, 4C
                level=4,
                section=chr(65 + school_idx),
                academic_year=2024,
                school_id=school.id
            )
            db.add(class_obj)
            db.commit()
            
            # Assign form teacher to class
            teacher_assignment = TeacherClassAssignment(
                teacher_id=users[school_idx].id,  # Form teachers
                class_id=class_obj.id
            )
            db.add(teacher_assignment)
            
            # Create 4 students per class
            for i in range(4):
                student_idx = school_idx * 4 + i
                student = Student(
                    student_id=f"S{2024000 + student_idx + 1}",
                    first_name=student_names[student_idx][0],
                    last_name=student_names[student_idx][1],
                    date_of_birth=date(2014, (student_idx % 12) + 1, (student_idx % 28) + 1),
                    gender="M" if student_idx % 2 == 0 else "F",
                    school_id=school.id,
                    class_id=class_obj.id
                )
                db.add(student)
            
            # Create terms for the school
            terms = [
                Term(
                    name=f"Term {i} 2024",
                    academic_year=2024,
                    term_number=i,
                    start_date=date(2024, (i-1)*3 + 1, 1),
                    end_date=date(2024, i*3, 30),
                    school_id=school.id
                )
                for i in range(1, 4)  # 3 terms
            ]
            db.add_all(terms)
        
        db.commit()
        
        # Create achievement categories
        achievement_categories = [
            AchievementCategory(
                name="Significant Improvement",
                description="For students showing 20% or more improvement",
                min_improvement_percent=20.0
            ),
            AchievementCategory(
                name="Excellence",
                description="For students scoring 90% or above",
                min_score=90.0
            ),
            AchievementCategory(
                name="Strong Performance",
                description="For students scoring 80% or above",
                min_score=80.0
            ),
        ]
        db.add_all(achievement_categories)
        db.commit()
        
        print("Database seeded successfully!")
        
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
```

### Task 14: Test Database Connection and Models
**File:** `backend/tests/test_database.py`
```python
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models import *

def test_all_models_imported():
    """Test that all models are properly imported."""
    assert School.__tablename__ == "schools"
    assert User.__tablename__ == "users"
    assert Class.__tablename__ == "classes"
    assert Student.__tablename__ == "students"
    assert Term.__tablename__ == "terms"
    assert Subject.__tablename__ == "subjects"
    assert Grade.__tablename__ == "grades"
    assert AchievementCategory.__tablename__ == "achievement_categories"
    assert Achievement.__tablename__ == "achievements"
    assert ReportCard.__tablename__ == "report_cards"
    assert ReportComponent.__tablename__ == "report_components"
    assert TeacherClassAssignment.__tablename__ == "teacher_class_assignments"

def test_relationships():
    """Test that relationships are properly defined."""
    # Test School relationships
    assert hasattr(School, 'users')
    assert hasattr(School, 'classes')
    assert hasattr(School, 'students')
    assert hasattr(School, 'terms')
    
    # Test User relationships
    assert hasattr(User, 'school')
    assert hasattr(User, 'class_assignments')
    
    # Test Student relationships
    assert hasattr(Student, 'school')
    assert hasattr(Student, 'class_obj')
    assert hasattr(Student, 'grades')
    assert hasattr(Student, 'report_cards')

def test_multi_tenant_fields():
    """Test that all relevant models have school_id for multi-tenancy."""
    models_with_school_id = [User, Class, Student, Term]
    for model in models_with_school_id:
        columns = [c.name for c in model.__table__.columns]
        assert 'school_id' in columns, f"{model.__name__} missing school_id"

def test_unique_constraints():
    """Test that unique constraints are properly defined."""
    # Check Student unique constraint
    student_constraints = [c.name for c in Student.__table__.constraints]
    assert '_student_school_uc' in student_constraints
    
    # Check Grade unique constraint
    grade_constraints = [c.name for c in Grade.__table__.constraints]
    assert '_student_term_subject_uc' in grade_constraints
```

## Validation Gates

Execute these commands to verify successful implementation:

```bash
# 1. Check Python syntax and formatting
cd backend
uv run ruff check --fix .
uv run ruff format .

# 2. Type checking
uv run mypy src/

# 3. Create and apply migration
uv run alembic revision --autogenerate -m "Initial database schema"
uv run alembic upgrade head

# 4. Test database connection
uv run python -c "from app.core.database import test_connection; print('Connection:', test_connection())"

# 5. Seed the database
uv run python src/app/core/seed_data.py

# 6. Run tests
uv run pytest tests/test_database.py -v

# 7. Verify tables created
uv run python -c "
from app.core.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
tables = inspector.get_table_names()
print(f'Created {len(tables)} tables:', sorted(tables))
"

# 8. Verify multi-tenant isolation query works
uv run python -c "
from app.core.database import SessionLocal
from app.models import Student
db = SessionLocal()
# This should only return students from school_id=1
students = db.query(Student).filter(Student.school_id == 1).all()
print(f'Found {len(students)} students in school 1')
db.close()
"
```

## Critical Implementation Notes

1. **Use SQLAlchemy 2.0 Syntax**: All models use `Mapped` type annotations and `mapped_column()`
2. **Multi-Tenant Isolation**: Every query involving user data MUST filter by `school_id`
3. **Foreign Key Naming**: Use descriptive names like `class_obj` to avoid Python keyword conflicts
4. **Index Strategy**: Add indexes on all foreign keys and frequently queried fields
5. **Cascade Deletes**: Use `cascade="all, delete-orphan"` for dependent relationships
6. **Password Hashing**: Never store plain text passwords - use bcrypt via passlib
7. **Decimal for Grades**: Use DECIMAL(5,2) for grade scores to maintain precision
8. **Enum Types**: Use SQLAlchemy's Enum type for role and performance band fields

## Common Pitfalls to Avoid

1. **Don't use Python keywords**: Avoid naming models `class` - use `class_model` or `Class`
2. **Don't forget indexes**: Add indexes on `school_id` for all tenant tables
3. **Don't skip validation**: Add CHECK constraints for grade ranges (0-100)
4. **Don't miss relationships**: Use `back_populates` to ensure bidirectional relationships
5. **Don't forget imports**: Update `__init__.py` when adding new models
6. **Don't skip type hints**: Use proper `Mapped` annotations for all fields

## Success Criteria

✅ All 12 model files created with proper SQLAlchemy 2.0 syntax
✅ Alembic migration generated and applied successfully
✅ All tables created in PostgreSQL with proper constraints
✅ Seed data script populates 3 schools, 6 users, 3 classes, 12 students
✅ Multi-tenant queries work correctly (filtering by school_id)
✅ All tests pass (syntax, typing, database connection, relationships)
✅ No security vulnerabilities (passwords hashed, SQL injection prevented)

## Additional Resources

- SQLAlchemy 2.0 ORM Quick Start: https://docs.sqlalchemy.org/en/20/orm/quickstart.html
- Alembic Tutorial: https://alembic.sqlalchemy.org/en/latest/tutorial.html
- PostgreSQL Row Level Security: https://www.postgresql.org/docs/current/ddl-rowsecurity.html
- FastAPI Database Tutorial: https://fastapi.tiangolo.com/tutorial/sql-databases/

## Confidence Score: 9/10

This PRP provides comprehensive context for one-pass implementation success. The only potential challenge might be debugging relationship configurations if there are circular import issues, but the proper use of string forward references ("User" instead of User) should prevent this.