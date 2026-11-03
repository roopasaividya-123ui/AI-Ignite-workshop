"""002_add_users_table.py

Revision ID: 002
Revises: 001
Create Date: 2026-10-31

Adds the ``users`` table for JWT-based authentication.
Every registered student and admin gets one row here.
Student accounts link back to the ``students`` table via ``student_id``.
Admin accounts have ``student_id = NULL``.
"""

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: str = "001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False, server_default="student"),
        sa.Column("student_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("user_id"),
    )
    op.create_index(op.f("ix_users_user_id"), "users", ["user_id"])
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_user_id"), table_name="users")
    op.drop_table("users")

