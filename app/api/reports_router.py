"""
app/api/reports_router.py — Analysis history, report viewing, sharing, bookmarking, and export.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import AnalysisDB
from app.models.schemas import (
    CredibilityReportResponse,
    ClaimItem,
    EvidenceItem,
    SourceCredibilityBreakdown,
    WarningItem,
)
from app.auth import get_optional_current_user, get_current_user, CurrentUser

router = APIRouter(prefix="/api/reports", tags=["Reports & History"])


def _to_response(rec: AnalysisDB) -> CredibilityReportResponse:
    domain_dict = rec.source_credibility
    return CredibilityReportResponse(
        id=rec.id,
        title=rec.title,
        input_type=rec.input_type,
        input_content=rec.input_content,
        extracted_domain=rec.extracted_domain,
        source_url=rec.source_url,
        author=rec.author,
        publish_date=rec.publish_date,
        overall_credibility_score=rec.overall_credibility_score,
        verdict=rec.verdict,
        confidence_score=rec.confidence_score,
        claims=[ClaimItem(**c) for c in rec.claims],
        supporting_evidence=[EvidenceItem(**e) for e in rec.supporting_evidence],
        contradicting_evidence=[EvidenceItem(**e) for e in rec.contradicting_evidence],
        source_credibility=SourceCredibilityBreakdown(**domain_dict),
        warnings=[WarningItem(**w) for w in rec.warnings],
        ai_explanation_standard=rec.ai_explanation_standard,
        ai_explanation_beginner=rec.ai_explanation_beginner,
        is_saved=rec.is_saved,
        is_public=rec.is_public,
        share_token=rec.share_token,
        created_at=rec.created_at,
    )


@router.get("", response_model=List[CredibilityReportResponse])
def get_reports(
    q: Optional[str] = Query(None, description="Search keyword in title or content"),
    verdict: Optional[str] = Query(None, description="Filter by verdict"),
    saved_only: Optional[bool] = Query(False, description="Filter saved only"),
    limit: int = Query(30, ge=1, le=100),
    current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """Retrieves analyses with search and verdict filtering."""
    query = db.query(AnalysisDB)

    if current_user and not current_user.is_admin:
        # User sees their own analyses plus public analyses
        query = query.filter((AnalysisDB.user_id == current_user.id) | (AnalysisDB.user_id == None))
    
    if q:
        query = query.filter(AnalysisDB.title.ilike(f"%{q}%") | AnalysisDB.input_content.ilike(f"%{q}%"))
    
    if verdict:
        query = query.filter(AnalysisDB.verdict.ilike(f"%{verdict}%"))
        
    if saved_only:
        query = query.filter(AnalysisDB.is_saved == True)

    results = query.order_by(AnalysisDB.created_at.desc()).limit(limit).all()
    return [_to_response(r) for r in results]


@router.get("/{report_id}", response_model=CredibilityReportResponse)
def get_single_report(report_id: str, db: Session = Depends(get_db)):
    """Retrieves a single credibility report by ID."""
    report = db.query(AnalysisDB).filter(AnalysisDB.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Credibility report not found.")
    return _to_response(report)


@router.get("/share/{token}", response_model=CredibilityReportResponse)
def get_shared_report(token: str, db: Session = Depends(get_db)):
    """Public read-only access for shared credibility reports."""
    report = db.query(AnalysisDB).filter(AnalysisDB.share_token == token).first()
    if not report or not report.is_public:
        raise HTTPException(status_code=404, detail="Shared report not found or private.")
    return _to_response(report)


@router.post("/{report_id}/save")
def toggle_save_report(
    report_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Toggles bookmark / save status for a report."""
    report = db.query(AnalysisDB).filter(AnalysisDB.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    
    report.is_saved = not report.is_saved
    db.commit()
    return {"id": report.id, "is_saved": report.is_saved}


@router.delete("/{report_id}")
def delete_report(
    report_id: str,
    current_user: CurrentUser = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Deletes an analysis report."""
    report = db.query(AnalysisDB).filter(AnalysisDB.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    if not current_user.is_admin and report.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this report.")

    db.delete(report)
    db.commit()
    return {"message": "Report deleted successfully."}
