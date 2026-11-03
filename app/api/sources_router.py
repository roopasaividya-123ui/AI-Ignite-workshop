"""
app/api/sources_router.py — Trusted source directory & domain reputation evaluator.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import TrustedSourceDB
from app.models.schemas import TrustedSourceResponse
from app.services.source_verifier import evaluate_source

router = APIRouter(prefix="/api/sources", tags=["Source Verification Engine"])


@router.get("", response_model=List[TrustedSourceResponse])
def list_trusted_sources(
    category: Optional[str] = Query(None, description="Filter: government, fact_checker, health_authority, news_agency"),
    q: Optional[str] = Query(None, description="Search by name or domain"),
    db: Session = Depends(get_db),
):
    """Returns directory of authoritative verification sources with trust rankings."""
    query = db.query(TrustedSourceDB).filter(TrustedSourceDB.is_active == True)
    if category:
        query = query.filter(TrustedSourceDB.category == category)
    if q:
        query = query.filter(TrustedSourceDB.name.ilike(f"%{q}%") | TrustedSourceDB.domain.ilike(f"%{q}%"))
    return query.order_by(TrustedSourceDB.credibility_rating.desc()).all()


@router.get("/verify-domain")
def verify_domain_reputation(domain: str = Query(..., description="Domain name to inspect")):
    """Inspects any web domain for authenticity, IFCN certification, and safety score."""
    return evaluate_source(domain)
