
from pydantic import ValidationError
import pytest

from app.models.student import StudentProfile


def test_valid_student_profile():
    student = StudentProfile(
        name="Test Student",
        email="student@example.com",
        degree="B.Tech",
        branch="Computer Science and Artificial Intelligence",
        graduation_year=2028,
        cgpa=9.23,
        skills=["Python", "Machine Learning"],
        interests=["AI internships", "Research"],
        preferred_location="India",
        career_goal="AI Developer",
    )

    assert student.cgpa == 9.23
    assert "Python" in student.skills


def test_invalid_cgpa():
    with pytest.raises(ValidationError):
        StudentProfile(
            name="Test Student",
            email="student@example.com",
            degree="B.Tech",
            branch="CSE",
            graduation_year=2028,
            cgpa=12,
        )
