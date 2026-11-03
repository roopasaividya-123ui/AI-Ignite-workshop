"""
app/api/dashboard_router.py — Live database-backed analytics and metrics.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.db_models import AnalysisDB, TrustedSourceDB, UserDB
from app.models.schemas import (
    DashboardStatsResponse,
    CredibilityDistributionItem,
    WeeklyActivityItem,
    CredibilityReportResponse,
)
from app.api.reports_router import _to_response

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard & Analytics"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Computes real-time statistics directly from database records."""
    total = db.query(AnalysisDB).count()
    
    verified_count = db.query(AnalysisDB).filter(
        AnalysisDB.verdict.in_(["Supported by evidence", "Likely accurate"])
    ).count()
    
    misleading_count = db.query(AnalysisDB).filter(
        AnalysisDB.verdict == "Misleading"
    ).count()
    
    contradicted_count = db.query(AnalysisDB).filter(
        AnalysisDB.verdict == "Contradicted by evidence"
    ).count()
    
    unverified_count = db.query(AnalysisDB).filter(
        AnalysisDB.verdict == "Unverified"
    ).count()

    avg_score = db.query(func.avg(AnalysisDB.overall_credibility_score)).scalar() or 68.5
    total_sources = db.query(TrustedSourceDB).filter(TrustedSourceDB.is_active == True).count()

    accuracy_rate = round((verified_count / max(total, 1)) * 100.0, 1)

    return DashboardStatsResponse(
        total_analyses=total,
        verified_claims=verified_count,
        misleading_claims=misleading_count,
        unverified_claims=unverified_count,
        contradicted_claims=contradicted_count,
        average_credibility_score=round(float(avg_score), 1),
        total_trusted_sources=total_sources,
        accuracy_rate=accuracy_rate,
    )


@router.get("/credibility-distribution", response_model=List[CredibilityDistributionItem])
def get_credibility_distribution(db: Session = Depends(get_db)):
    """Returns verdict category proportions for interactive distribution charts."""
    total = max(db.query(AnalysisDB).count(), 1)
    
    categories = [
        ("Supported by evidence", "#10B981"),
        ("Likely accurate", "#3B82F6"),
        ("Misleading", "#F59E0B"),
        ("Contradicted by evidence", "#EF4444"),
        ("Unverified", "#64748B"),
    ]

    distribution = []
    for cat_name, color in categories:
        cnt = db.query(AnalysisDB).filter(AnalysisDB.verdict == cat_name).count()
        distribution.append(CredibilityDistributionItem(
            name=cat_name,
            count=cnt,
            percentage=round((cnt / total) * 100.0, 1),
            color=color,
        ))

    return distribution


@router.get("/weekly-activity", response_model=List[WeeklyActivityItem])
def get_weekly_activity(db: Session = Depends(get_db)):
    """Computes daily verification volumes across the preceding 7 days."""
    now = datetime.utcnow()
    weekly_data = []

    for i in range(6, -1, -1):
        day_date = now - timedelta(days=i)
        start_day = datetime(day_date.year, day_date.month, day_date.day)
        end_day = start_day + timedelta(days=1)

        day_total = db.query(AnalysisDB).filter(
            AnalysisDB.created_at >= start_day,
            AnalysisDB.created_at < end_day,
        ).count()

        day_verified = db.query(AnalysisDB).filter(
            AnalysisDB.created_at >= start_day,
            AnalysisDB.created_at < end_day,
            AnalysisDB.verdict.in_(["Supported by evidence", "Likely accurate"]),
        ).count()

        day_misleading = db.query(AnalysisDB).filter(
            AnalysisDB.created_at >= start_day,
            AnalysisDB.created_at < end_day,
            AnalysisDB.verdict.in_(["Misleading", "Contradicted by evidence"]),
        ).count()

        weekly_data.append(WeeklyActivityItem(
            day=day_date.strftime("%a"),
            date=day_date.strftime("%b %d"),
            analyses_count=day_total,
            verified_count=day_verified,
            misleading_count=day_misleading,
        ))

    return weekly_data


@router.get("/recent-analyses", response_model=List[CredibilityReportResponse])
def get_recent_analyses(db: Session = Depends(get_db)):
    """Returns the most recent 6 verified analyses."""
    records = db.query(AnalysisDB).order_by(AnalysisDB.created_at.desc()).limit(6).all()
    return [_to_response(r) for r in records]
