from sqlalchemy import Boolean, Date
from datetime import date
from sqlalchemy import String, Float, Integer, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StudentDB(Base):
    __tablename__ = "students"

    student_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), unique=True, index=True, nullable=False
    )

    degree: Mapped[str] = mapped_column(String(100), nullable=False)
    branch: Mapped[str] = mapped_column(String(150), nullable=False)
    graduation_year: Mapped[int] = mapped_column(
        Integer, nullable=False
    )
    cgpa: Mapped[float] = mapped_column(Float, nullable=False)

    skills: Mapped[list] = mapped_column(JSON, default=list)
    interests: Mapped[list] = mapped_column(JSON, default=list)

    preferred_location: Mapped[str] = mapped_column(
        String(100), default="India"
    )
    career_goal: Mapped[str] = mapped_column(
        String(200), default=""
    )

class OpportunityDB(Base):
    __tablename__ = "opportunities"

    opportunity_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, index=True
    )

    title: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    organization: Mapped[str] = mapped_column(
        String(200), nullable=False
    )
    category: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    description: Mapped[str] = mapped_column(
        String(5000), nullable=False
    )

    eligibility: Mapped[str] = mapped_column(
        String(2000), default=""
    )
    required_skills: Mapped[list] = mapped_column(
        JSON, default=list
    )

    location: Mapped[str] = mapped_column(
        String(200), default="India", index=True
    )
    is_paid: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    stipend: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )

    deadline: Mapped[date | None] = mapped_column(
        Date, nullable=True
    )
    source_url: Mapped[str] = mapped_column(
        String(2000), unique=True, nullable=False
    )

