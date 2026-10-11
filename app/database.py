
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./data/opportunityos.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def create_db_tables():
    # Import the model so SQLAlchemy knows which tables to create.
    from app.models.db_models import StudentDB

    Base.metadata.create_all(bind=engine)
