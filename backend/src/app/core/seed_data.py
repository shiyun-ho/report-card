import os
from datetime import date
from decimal import Decimal

from passlib.context import CryptContext

from app.core.database import SessionLocal
from app.models import (
    AchievementCategory,
    Class,
    Grade,
    School,
    Student,
    Subject,
    TeacherClassAssignment,
    Term,
    User,
    UserRole,
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Singapore student names with ethnic diversity - module level for testing
# Expanded to support multiple classes per school (24 students total)
singapore_student_names = [
    # Riverside Primary - 8 students across 2 classes (4A: 0-3, 4B: 4-7)
    ("Wei Jie", "Tan"),        # 4A - Form teacher sees these 4
    ("Hui Min", "Lim"),        # 4A
    ("Kai Rui", "Chen"),       # 4A  
    ("Mei Hua", "Wong"),       # 4A
    ("Jun Wei", "Ng"),         # 4B - Year head sees all 8
    ("Li Hua", "Goh"),         # 4B
    ("Xin Yi", "Koh"),         # 4B
    ("Ming Hao", "Sim"),       # 4B
    # Hillview Primary - 8 students across 2 classes (4A: 8-11, 4B: 12-15)
    ("Arjun", "Kumar"),        # 4A - Form teacher sees these 4
    ("Priya", "Sharma"),       # 4A
    ("Zhi Hao", "Ong"),        # 4A
    ("Siti", "Hashim"),        # 4A
    ("Raj", "Menon"),          # 4B - Year head sees all 8
    ("Fatimah", "Ali"),        # 4B
    ("Wei Ming", "Tay"),       # 4B
    ("Nisha", "Devi"),         # 4B
    # Eastwood Primary - 8 students across 2 classes (4A: 16-19, 4B: 20-23)
    ("Marcus", "Teo"),         # 4A - Form teacher sees these 4
    ("Aisyah", "Rahman"),      # 4A
    ("Jun Ming", "Low"),       # 4A
    ("Kavitha", "Raj"),        # 4A
    ("Daniel", "Wee"),         # 4B - Year head sees all 8
    ("Sarah", "Chua"),         # 4B
    ("Ethan", "Lim"),          # 4B
    ("Maya", "Singh"),         # 4B
]

# Grade patterns for achievement trigger testing - module level for testing
grade_patterns = {
    "significant_improvement": {
        "term_1": [65, 70, 75, 68],  # English, Math, Science, Chinese
        "term_2": [70, 75, 80, 72],
        "term_3": [85, 88, 92, 85],  # 20%+ improvement triggers achievements
    },
    "steady_progress": {
        "term_1": [75, 80, 70, 78],
        "term_2": [78, 82, 75, 80],
        "term_3": [83, 88, 80, 86],  # 10-19% improvement triggers achievements
    },
    "excellence_achiever": {
        "term_1": [85, 88, 82, 87],
        "term_2": [88, 90, 86, 89],
        "term_3": [90, 92, 90, 91],  # ≥90 triggers excellence achievements
    },
    "stable_performer": {
        "term_1": [78, 75, 80, 77],
        "term_2": [79, 76, 81, 78],
        "term_3": [80, 77, 82, 79],  # Minimal change, tests stable performance
    },
}

# Pattern assignment for students - module level for testing
# Updated for 24 students (8 per school, 2 classes each)
pattern_assignment = [
    # Riverside Primary 4A (0-3): Form teacher students
    "significant_improvement",  # Wei Jie Tan
    "steady_progress",          # Hui Min Lim
    "excellence_achiever",      # Kai Rui Chen
    "stable_performer",         # Mei Hua Wong
    # Riverside Primary 4B (4-7): Year head only students
    "significant_improvement",  # Jun Wei Ng
    "steady_progress",          # Li Hua Goh
    "excellence_achiever",      # Xin Yi Koh
    "stable_performer",         # Ming Hao Sim
    # Hillview Primary 4A (8-11): Form teacher students
    "steady_progress",          # Arjun Kumar
    "excellence_achiever",      # Priya Sharma
    "stable_performer",         # Zhi Hao Ong
    "significant_improvement",  # Siti Hashim
    # Hillview Primary 4B (12-15): Year head only students
    "excellence_achiever",      # Raj Menon
    "stable_performer",         # Fatimah Ali
    "significant_improvement",  # Wei Ming Tay
    "steady_progress",          # Nisha Devi
    # Eastwood Primary 4A (16-19): Form teacher students
    "stable_performer",         # Marcus Teo
    "significant_improvement",  # Aisyah Rahman
    "steady_progress",          # Jun Ming Low
    "excellence_achiever",      # Kavitha Raj
    # Eastwood Primary 4B (20-23): Year head only students
    "significant_improvement",  # Daniel Wee
    "excellence_achiever",      # Sarah Chua
    "stable_performer",         # Ethan Lim
    "steady_progress",          # Maya Singh
]


def seed_database():
    """
    Seed database with initial data for 3 schools with proper RBAC demonstration.
    
    Structure created:
    - 3 schools (Riverside, Hillview, Eastwood)
    - 6 classes total (2 per school: 4A and 4B)  
    - 24 students total (8 per school, 4 per class)
    - 3 form teachers (assigned to 4A classes only - see 4 students each)
    - 3 year heads (see all classes in school - see 8 students each)
    - Comprehensive grade data across 3 terms for achievement testing
    """
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
        # Each school now has 1 form teacher (for 4A only) and 1 year head (sees all classes)
        users_data = [
            # Riverside Primary School
            ("Ms. Tan", "tan@rps.edu.sg", UserRole.FORM_TEACHER, schools[0]),      # Form teacher 4A only
            ("Mr. Lim", "lim@rps.edu.sg", UserRole.YEAR_HEAD, schools[0]),        # Year head sees 4A + 4B
            # Hillview Primary School  
            ("Ms. Wong", "wong@hps.edu.sg", UserRole.FORM_TEACHER, schools[1]),    # Form teacher 4A only
            ("Mrs. Kumar", "kumar@hps.edu.sg", UserRole.YEAR_HEAD, schools[1]),   # Year head sees 4A + 4B
            # Eastwood Primary School
            ("Mr. Chen", "chen@eps.edu.sg", UserRole.FORM_TEACHER, schools[2]),   # Form teacher 4A only
            ("Ms. Lee", "lee@eps.edu.sg", UserRole.YEAR_HEAD, schools[2]),        # Year head sees 4A + 4B
        ]

        users = []
        for full_name, email, role, school in users_data:
            user = User(
                full_name=full_name,
                username=email.split("@")[0],
                email=email,
                hashed_password=pwd_context.hash(
                    os.getenv("SEED_DEFAULT_PASSWORD", "CHANGE_ME_INSECURE_DEV_ONLY")
                ),
                role=role,
                school_id=school.id,
            )
            users.append(user)
        db.add_all(users)
        db.commit()

        # Create classes and students for each school
        # Each school now has 2 classes: 4A (form teacher assigned) and 4B (no form teacher)
        # Using module-level singapore_student_names for consistency and testing

        all_classes = []
        form_teacher_idx = 0  # Index for form teachers only
        
        for school_idx, school in enumerate(schools):
            # Create 2 classes per school: 4A and 4B
            for class_section_idx in range(2):  # 0 for A, 1 for B
                section_letter = chr(65 + class_section_idx)  # A, B
                class_obj = Class(
                    name=f"Primary 4{section_letter}",  # 4A, 4B
                    level=4,
                    section=section_letter,
                    academic_year=2024,
                    school_id=school.id,
                )
                db.add(class_obj)
                db.commit()
                all_classes.append(class_obj)

                # Only assign form teacher to 4A classes (class_section_idx == 0)
                if class_section_idx == 0:
                    teacher_assignment = TeacherClassAssignment(
                        teacher_id=users[form_teacher_idx].id,  # Form teachers (0, 2, 4)
                        class_id=class_obj.id,
                    )
                    db.add(teacher_assignment)
                    form_teacher_idx += 2  # Skip year head, go to next form teacher

                # Create 4 students per class
                for student_in_class_idx in range(4):
                    # Calculate global student index: 8 students per school
                    student_idx = school_idx * 8 + class_section_idx * 4 + student_in_class_idx
                    student = Student(
                        student_id=f"S{2024000 + student_idx + 1}",
                        first_name=singapore_student_names[student_idx][0],
                        last_name=singapore_student_names[student_idx][1],
                        date_of_birth=date(2014, (student_idx % 12) + 1, (student_idx % 28) + 1),
                        gender="M" if student_idx % 2 == 0 else "F",
                        school_id=school.id,
                        class_id=class_obj.id,
                    )
                    db.add(student)

            # Create terms for the school
            terms = [
                Term(
                    name=f"Term {i} 2024",
                    academic_year=2024,
                    term_number=i,
                    start_date=date(2024, (i - 1) * 3 + 1, 1),
                    end_date=date(2024, i * 3, 30),
                    school_id=school.id,
                )
                for i in range(1, 4)  # 3 terms
            ]
            db.add_all(terms)

        db.commit()

        # Create comprehensive achievement categories (15 total)
        achievement_categories = [
            # Subject-specific significant improvements (4 subjects)
            AchievementCategory(
                name="Significant improvement in English",
                description="20% or more improvement in English",
                min_improvement_percent=20.0,
            ),
            AchievementCategory(
                name="Significant improvement in Mathematics",
                description="20% or more improvement in Mathematics",
                min_improvement_percent=20.0,
            ),
            AchievementCategory(
                name="Significant improvement in Science",
                description="20% or more improvement in Science",
                min_improvement_percent=20.0,
            ),
            AchievementCategory(
                name="Significant improvement in Chinese",
                description="20% or more improvement in Chinese",
                min_improvement_percent=20.0,
            ),
            # Subject-specific steady progress (4 subjects)
            AchievementCategory(
                name="Steady progress in English",
                description="10-19% improvement in English",
                min_improvement_percent=10.0,
            ),
            AchievementCategory(
                name="Steady progress in Mathematics",
                description="10-19% improvement in Mathematics",
                min_improvement_percent=10.0,
            ),
            AchievementCategory(
                name="Steady progress in Science",
                description="10-19% improvement in Science",
                min_improvement_percent=10.0,
            ),
            AchievementCategory(
                name="Steady progress in Chinese",
                description="10-19% improvement in Chinese",
                min_improvement_percent=10.0,
            ),
            # Excellence in subjects (4 subjects)
            AchievementCategory(
                name="Excellence in English",
                description="Scored 90 or above in English",
                min_score=90.0,
            ),
            AchievementCategory(
                name="Excellence in Mathematics",
                description="Scored 90 or above in Mathematics",
                min_score=90.0,
            ),
            AchievementCategory(
                name="Excellence in Science",
                description="Scored 90 or above in Science",
                min_score=90.0,
            ),
            AchievementCategory(
                name="Excellence in Chinese",
                description="Scored 90 or above in Chinese",
                min_score=90.0,
            ),
            # Overall performance achievements (2)
            AchievementCategory(
                name="Overall academic improvement",
                description="15% or more overall improvement across all subjects",
                min_improvement_percent=15.0,
            ),
            AchievementCategory(
                name="Consistent high performance",
                description="Maintained excellence across all subjects with 85+ average",
                min_score=85.0,
            ),
            # Behavioral/Additional achievement (1)
            AchievementCategory(
                name="Outstanding effort and participation",
                description="Exceptional classroom engagement and effort",
            ),
        ]
        db.add_all(achievement_categories)
        db.commit()

        # Generate comprehensive grade history (144 grades total)
        # Using module-level grade_patterns and pattern_assignment for testing consistency

        # Get all students, subjects, and terms from database
        all_students = db.query(Student).all()
        # English, Math, Science, Chinese (ordered by ID)
        all_subjects = db.query(Subject).order_by(Subject.id).all()

        # Create grades for each student across all terms and subjects
        for student_idx, student in enumerate(all_students):
            pattern_name = pattern_assignment[student_idx]
            pattern = grade_patterns[pattern_name]

            # Get terms for this student's school (ordered by term_number)
            school_terms = (
                db.query(Term)
                .filter(Term.school_id == student.school_id)
                .order_by(Term.term_number)
                .all()
            )

            # Create grades for each term
            for term_idx, term in enumerate(school_terms):
                term_key = f"term_{term_idx + 1}"
                term_grades = pattern[term_key]

                # Create grade for each subject
                for subject_idx, subject in enumerate(all_subjects):
                    grade = Grade(
                        score=Decimal(str(term_grades[subject_idx])),
                        student_id=student.id,
                        term_id=term.id,
                        subject_id=subject.id,
                        modified_by_id=None,  # System generated
                    )
                    db.add(grade)

        db.commit()

        # Print summary of created data
        print("Database seeded successfully!")
        print(f"Created: {db.query(School).count()} schools")
        print(f"Created: {db.query(Class).count()} classes (2 per school)")
        print(f"Created: {db.query(Student).count()} students (8 per school, 4 per class)")
        print(f"Created: {db.query(Grade).count()} grades")
        print(f"Created: {db.query(AchievementCategory).count()} achievement categories")
        print("RBAC structure:")
        print("- Form teachers: See only their assigned class (4A)")
        print("- Year heads: See all classes in their school (4A + 4B)")
        print("Grade patterns implemented for achievement trigger testing")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
