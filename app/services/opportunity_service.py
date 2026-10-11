
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.db_models import OpportunityDB
from app.models.opportunity import Opportunity


def create_opportunity(
    db: Session, opportunity: Opportunity
) -> OpportunityDB:
    data = opportunity.model_dump(
        exclude={"opportunity_id"}
    )

    record = OpportunityDB(**data)

    db.add(record)
    db.commit()
    db.refresh(record)

    return record


def get_opportunities(
    db: Session,
    category: str | None = None,
    location: str | None = None,
) -> list[OpportunityDB]:
    statement = select(OpportunityDB)

    if category:
        statement = statement.where(
            OpportunityDB.category.ilike(f"%{category}%")
        )

    if location:
        statement = statement.where(
            OpportunityDB.location.ilike(f"%{location}%")
        )

    statement = statement.order_by(
        OpportunityDB.opportunity_id.desc()
    )

    return list(db.scalars(statement).all())


def get_opportunity(
    db: Session, opportunity_id: int
) -> OpportunityDB | None:
    return db.get(OpportunityDB, opportunity_id)
