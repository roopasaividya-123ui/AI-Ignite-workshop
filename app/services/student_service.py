
from sqlalchemy.orm import Session

from app.models.db_models import StudentDB
from app.models.student import StudentProfile


def create_student(
    db: Session, profile: StudentProfile
) -> StudentDB:
    student_data = profile.model_dump(exclude={"student_id"})

    student = StudentDB(**student_data)

    db.add(student)
    db.commit()
    db.refresh(student)

    return student


def get_student(
    db: Session, student_id: int
) -> StudentDB | None:
    return db.get(StudentDB, student_id)
