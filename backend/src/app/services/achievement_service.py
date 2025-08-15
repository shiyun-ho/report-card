from typing import Dict, List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models import AchievementCategory, Student, Subject, Term, User
from app.services.grade_service import GradeService


class AchievementService:
    """
    Service for generating achievement suggestions based on student performance patterns.

    Implements role-based access control:
    - Form teachers: Can get suggestions for assigned students only
    - Year heads: Can get suggestions for all students in their school
    - Admins: Can get suggestions for all students in their school

    Uses mathematical analysis of grade improvement patterns to match
    existing achievement categories and provide relevance-scored suggestions.
    """

    def __init__(self, db: Session):
        self.db = db
        self.grade_service = GradeService(db)

    def can_access_student_achievements(self, user: User, student_id: int) -> bool:
        """
        Check if user can access achievement suggestions for specific student.

        Args:
            user: Current authenticated user
            student_id: ID of the student

        Returns:
            True if user can access student's achievement suggestions, False otherwise
        """
        # Reuse the grade service's permission checking logic
        # Achievement suggestions follow same access rules as grade access
        return self.grade_service.can_edit_student_grades(user, student_id)

    def get_achievement_suggestions(
        self, student_id: int, term_id: int, user: User
    ) -> Optional[Dict]:
        """
        Get achievement suggestions for a student in a specific term.

        Args:
            student_id: ID of the student
            term_id: ID of the term
            user: Current authenticated user

        Returns:
            Dictionary with suggestion data or None if access denied/insufficient data
        """
        # Verify RBAC access
        if not self.can_access_student_achievements(user, student_id):
            return None

        # Get student and term information
        student = (
            self.db.query(Student)
            .options(joinedload(Student.class_obj))
            .filter(Student.id == student_id, Student.school_id == user.school_id)
            .first()
        )

        if not student:
            return None

        term = (
            self.db.query(Term).filter(Term.id == term_id, Term.school_id == user.school_id).first()
        )

        if not term:
            return None

        # Get all subjects and achievement categories
        subjects = self.db.query(Subject).all()
        achievement_categories = self.db.query(AchievementCategory).all()

        suggestions = []

        # 1. Subject-specific achievement matching
        subject_suggestions = self._get_subject_specific_suggestions(
            student_id, term_id, subjects, achievement_categories, user
        )
        suggestions.extend(subject_suggestions)

        # 2. Overall achievement matching
        overall_suggestions = self._get_overall_achievement_suggestions(
            student_id, term_id, subjects, achievement_categories, user
        )
        suggestions.extend(overall_suggestions)

        # Calculate average relevance
        if suggestions:
            average_relevance = sum(s["relevance_score"] for s in suggestions) / len(suggestions)
        else:
            average_relevance = 0.0

        return {
            "student_id": student_id,
            "term_id": term_id,
            "student_name": student.full_name,
            "term_name": term.name,
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "average_relevance": average_relevance,
        }

    def _get_subject_specific_suggestions(
        self,
        student_id: int,
        term_id: int,
        subjects: List[Subject],
        achievement_categories: List[AchievementCategory],
        user: User,
    ) -> List[Dict]:
        """
        Generate subject-specific achievement suggestions based on improvement patterns.

        Args:
            student_id: ID of the student
            term_id: ID of the term
            subjects: List of all subjects
            achievement_categories: List of all achievement categories
            user: Current authenticated user

        Returns:
            List of suggestion dictionaries
        """
        suggestions = []

        for subject in subjects:
            # Calculate improvement for this subject
            improvement_data = self.grade_service.calculate_improvement(
                student_id, subject.id, user
            )

            if not improvement_data:
                continue  # Skip if insufficient data

            # Get current term grade for excellence checking
            current_grade = self.grade_service.get_student_grades(student_id, term_id, user)
            subject_current_score = None

            for grade in current_grade:
                if grade.subject_id == subject.id:
                    subject_current_score = float(grade.score)
                    break

            # Match against achievement categories for this subject
            for category in achievement_categories:
                suggestion = self._check_subject_category_match(
                    subject, category, improvement_data, subject_current_score
                )
                if suggestion:
                    suggestions.append(suggestion)

        # Sort by relevance score (highest first)
        suggestions.sort(key=lambda x: x["relevance_score"], reverse=True)

        return suggestions

    def _check_subject_category_match(
        self,
        subject: Subject,
        category: AchievementCategory,
        improvement_data: Dict,
        current_score: Optional[float],
    ) -> Optional[Dict]:
        """
        Check if a subject's performance matches an achievement category.

        Args:
            subject: The subject being evaluated
            category: Achievement category to check against
            improvement_data: Improvement statistics from GradeService
            current_score: Current term score for the subject

        Returns:
            Suggestion dictionary if match found, None otherwise
        """
        # Check if this category is for this subject
        subject_name_lower = subject.name.lower()
        category_name_lower = category.name.lower()

        if subject_name_lower not in category_name_lower:
            return None  # Category not for this subject

        relevance_score = 0.0
        explanation = ""
        supporting_data = {}

        # Check improvement-based achievements
        if category.min_improvement_percent is not None:
            improvement_percent = improvement_data["improvement_percentage"]

            if "significant improvement" in category_name_lower:
                # Significant improvement: ≥20%
                if improvement_percent >= 20.0:
                    relevance_score = self._calculate_improvement_relevance_score(
                        improvement_percent, 20.0, improvement_data["total_terms"]
                    )
                    explanation = (
                        f"Improved {improvement_percent:.1f}% in {subject.name} "
                        f"from {improvement_data['first_score']:.0f} to {improvement_data['latest_score']:.0f}"
                    )
                    supporting_data = {
                        "improvement_percentage": improvement_percent,
                        "score_change": f"{improvement_data['first_score']:.0f} → {improvement_data['latest_score']:.0f}",
                        "terms_analyzed": improvement_data["total_terms"],
                    }

            elif "steady progress" in category_name_lower:
                # Steady progress: 10-19%
                if 10.0 <= improvement_percent < 20.0:
                    relevance_score = self._calculate_improvement_relevance_score(
                        improvement_percent, 10.0, improvement_data["total_terms"]
                    )
                    explanation = f"Showed steady progress with {improvement_percent:.1f}% improvement in {subject.name}"
                    supporting_data = {
                        "improvement_percentage": improvement_percent,
                        "score_change": f"{improvement_data['first_score']:.0f} → {improvement_data['latest_score']:.0f}",
                        "terms_analyzed": improvement_data["total_terms"],
                    }

        # Check score-based achievements (excellence)
        if category.min_score is not None and current_score is not None:
            if "excellence" in category_name_lower and current_score >= 90.0:
                relevance_score = self._calculate_score_relevance_score(current_score, 90.0)
                explanation = f"Achieved excellence with {current_score:.0f}% in {subject.name}"
                supporting_data = {"current_score": current_score, "excellence_threshold": 90.0}

        # Return suggestion if relevant
        if relevance_score > 0.0:
            return {
                "title": category.name,
                "description": category.description,
                "category_name": category.name,
                "relevance_score": relevance_score,
                "explanation": explanation,
                "supporting_data": supporting_data,
            }

        return None

    def _calculate_improvement_relevance_score(
        self, improvement_percent: float, threshold: float, data_points: int
    ) -> float:
        """
        Calculate relevance score for improvement-based achievements.

        Args:
            improvement_percent: Actual improvement percentage
            threshold: Required threshold for the achievement
            data_points: Number of terms with data

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if improvement_percent >= threshold:
            base_score = 0.9  # Strong match
        elif improvement_percent >= threshold * 0.8:
            base_score = 0.7  # Good match
        else:
            base_score = 0.3  # Weak match

        # Adjust for data quality (more terms = more reliable)
        reliability_factor = min(data_points / 3.0, 1.0)
        return base_score * reliability_factor

    def _calculate_score_relevance_score(self, current_score: float, threshold: float) -> float:
        """
        Calculate relevance score for score-based achievements.

        Args:
            current_score: Current score achieved
            threshold: Required threshold for the achievement

        Returns:
            Relevance score between 0.0 and 1.0
        """
        if current_score >= threshold:
            # Score achievement - higher scores get higher relevance
            if current_score >= 95.0:
                return 0.95  # Exceptional performance
            elif current_score >= 90.0:
                return 0.9  # Strong achievement
            else:
                return 0.8  # Good achievement
        else:
            return 0.0  # Didn't meet threshold

    def _get_overall_achievement_suggestions(
        self,
        student_id: int,
        term_id: int,
        subjects: List[Subject],
        achievement_categories: List[AchievementCategory],
        user: User,
    ) -> List[Dict]:
        """
        Generate overall achievement suggestions based on cross-subject performance.

        Args:
            student_id: ID of the student
            term_id: ID of the term
            subjects: List of all subjects
            achievement_categories: List of all achievement categories
            user: Current authenticated user

        Returns:
            List of overall achievement suggestion dictionaries
        """
        suggestions = []

        # Collect improvement data for all subjects
        subject_improvements = []
        current_scores = []

        for subject in subjects:
            improvement_data = self.grade_service.calculate_improvement(
                student_id, subject.id, user
            )
            if improvement_data:
                subject_improvements.append(improvement_data["improvement_percentage"])

            # Get current term scores
            current_grades = self.grade_service.get_student_grades(student_id, term_id, user)
            for grade in current_grades:
                if grade.subject_id == subject.id:
                    current_scores.append(float(grade.score))
                    break

        # Calculate overall metrics if we have sufficient data
        if len(subject_improvements) >= 2:  # Need at least 2 subjects for overall calculation
            overall_improvement = sum(subject_improvements) / len(subject_improvements)

            # Check for "Overall academic improvement" (≥15%)
            for category in achievement_categories:
                if (
                    "overall academic improvement" in category.name.lower()
                    and category.min_improvement_percent is not None
                ):
                    if overall_improvement >= 15.0:
                        relevance_score = self._calculate_improvement_relevance_score(
                            overall_improvement,
                            15.0,
                            3,  # Assume 3 terms for overall calculation
                        )
                        suggestions.append(
                            {
                                "title": category.name,
                                "description": category.description,
                                "category_name": category.name,
                                "relevance_score": relevance_score,
                                "explanation": f"Achieved {overall_improvement:.1f}% overall improvement across all subjects",
                                "supporting_data": {
                                    "overall_improvement_percentage": overall_improvement,
                                    "subjects_analyzed": len(subject_improvements),
                                    "individual_improvements": subject_improvements,
                                },
                            }
                        )
                    break

        # Calculate overall average if we have current scores
        if len(current_scores) >= 2:  # Need at least 2 subjects for average
            overall_average = sum(current_scores) / len(current_scores)

            # Check for "Consistent high performance" (≥85 average)
            for category in achievement_categories:
                if (
                    "consistent high performance" in category.name.lower()
                    and category.min_score is not None
                ):
                    if overall_average >= 85.0:
                        relevance_score = self._calculate_score_relevance_score(
                            overall_average, 85.0
                        )
                        suggestions.append(
                            {
                                "title": category.name,
                                "description": category.description,
                                "category_name": category.name,
                                "relevance_score": relevance_score,
                                "explanation": f"Maintained consistent high performance with {overall_average:.1f}% average across all subjects",
                                "supporting_data": {
                                    "overall_average": overall_average,
                                    "subjects_analyzed": len(current_scores),
                                    "individual_scores": current_scores,
                                },
                            }
                        )
                    break

        return suggestions

    def _calculate_relevance_score(
        self, improvement_data: Dict, achievement_category: AchievementCategory
    ) -> float:
        """
        Calculate relevance score for an achievement category based on student performance data.

        Args:
            improvement_data: Dictionary containing improvement metrics
            achievement_category: Achievement category to evaluate

        Returns:
            Relevance score between 0.0 and 1.0
        """
        # TODO: Implement relevance scoring algorithm
        # This will be implemented in Task 3.3.3d
        return 0.0
