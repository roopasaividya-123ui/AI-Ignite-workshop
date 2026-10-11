
from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import SessionLocal, create_db_tables
from app.models.student import StudentProfile
from app.services.student_service import create_student, get_student


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_tables()
    yield


app = FastAPI(
    title="OpportunityOS API",
    description="Student Opportunity Agent backend",
    version="0.1.0",
    lifespan=lifespan,
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
def home():
    return {
        "message": "Welcome to OpportunityOS!",
        "status": "running",
    }


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/students", response_model=StudentProfile, status_code=201)
def register_student(
    profile: StudentProfile,
    db: Session = Depends(get_db),
):
    try:
        return create_student(db, profile)
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="A student with this email already exists.",
        )


@app.get("/students/{student_id}", response_model=StudentProfile)
def read_student(
    student_id: int,
    db: Session = Depends(get_db),
):
    student = get_student(db, student_id)

    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Student not found.",
        )

    return student
