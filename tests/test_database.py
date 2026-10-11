
from app.database import SessionLocal, create_db_tables
from app.models.student import StudentProfile
from app.services.student_service import (
    create_student,
    get_student,
)


def test_create_and_get_student():
    create_db_tables()

    with SessionLocal() as db:
        profile = StudentProfile(
            name="Test Student",
            email="test.student@example.com",
            degree="B.Tech",
            branch="CSE-AI",
            graduation_year=2028,
            cgpa=9.23,
            skills=["Python", "Machine Learning"],
            interests=["AI internships"],
            preferred_location="India",
            career_goal="AI Developer",
        )

        student = create_student(db, profile)

        assert student.student_id is not None
        saved_id = student.student_id

        retrieved = get_student(db, saved_id)

        assert retrieved is not None
        assert retrieved.name == "Test Student"
        assert retrieved.cgpa == 9.23
        assert "Python" in retrieved.skills

        db.delete(retrieved)
        db.commit()
