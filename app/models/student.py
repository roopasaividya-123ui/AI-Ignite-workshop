
from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class StudentProfile(BaseModel):
    student_id: Optional[int] = None

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr

    degree: str
    branch: str
    graduation_year: int = Field(ge=2026, le=2100)

    cgpa: float = Field(ge=0, le=10)

    skills: List[str] = Field(default_factory=list)
    interests: List[str] = Field(default_factory=list)

    preferred_location: str = "India"
    career_goal: str = ""
