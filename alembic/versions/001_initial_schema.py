"""001_initial_schema.py

Revision ID: 001
Revises:
Create Date: 2026-10-31

Represents the schema that existed before Alembic was introduced:
  - students   table
  - opportunities table

For databases that already have these tables, stamp at this revision
WITHOUT running the migration:

    alembic stamp 001

Then run the next migration to add the users table:

    alembic upgrade head
"""

from alembic import op
import sqlalchemy as sa

# Revision identifiers used by Alembic.
revision: str = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create the original students and opportunities tables.

    If these tables already exist (pre-Alembic database), stamp the database
    at this revision instead of running this migration:

        alembic stamp 001
    """
    op.create_table(
        "students",
        sa.Column("student_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("degree", sa.String(length=100), nullable=False),
        sa.Column("branch", sa.String(length=150), nullable=False),
        sa.Column("graduation_year", sa.Integer(), nullable=False),
        sa.Column("cgpa", sa.Float(), nullable=False),
        sa.Column("skills", sa.JSON(), nullable=True),
        sa.Column("interests", sa.JSON(), nullable=True),
        sa.Column("preferred_location", sa.String(length=100), nullable=True),
        sa.Column("career_goal", sa.String(length=200), nullable=True),
        sa.PrimaryKeyConstraint("student_id"),
    )
    op.create_index(op.f("ix_students_student_id"), "students", ["student_id"])
    op.create_index(op.f("ix_students_email"), "students", ["email"], unique=True)

    op.create_table(
        "opportunities",
        sa.Column("opportunity_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("organization", sa.String(length=200), nullable=False),
        sa.Column("category", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=5000), nullable=False),
        sa.Column("eligibility", sa.String(length=2000), nullable=True),
        sa.Column("required_skills", sa.JSON(), nullable=True),
        sa.Column("location", sa.String(length=200), nullable=True),
        sa.Column("is_paid", sa.Boolean(), nullable=True),
        sa.Column("stipend", sa.String(length=100), nullable=True),
        sa.Column("deadline", sa.Date(), nullable=True),
        sa.Column("source_url", sa.String(length=2000), nullable=False),
        sa.PrimaryKeyConstraint("opportunity_id"),
        sa.UniqueConstraint("source_url"),
    )
    op.create_index(
        op.f("ix_opportunities_opportunity_id"), "opportunities", ["opportunity_id"]
    )
    op.create_index(
        op.f("ix_opportunities_category"), "opportunities", ["category"]
    )
    op.create_index(
        op.f("ix_opportunities_location"), "opportunities", ["location"]
    )


def downgrade() -> None:
    op.drop_table("opportunities")
    op.drop_table("students")

