"""
app/api/analyze_router.py — Core AI News Analyzer pipeline & verification endpoints.
"""

import json
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import AnalysisDB
from app.models.schemas import (
    AnalyzeRequest,
    CredibilityReportResponse,
    ClaimItem,
    EvidenceItem,
    SourceCredibilityBreakdown,
    WarningItem,
)
from app.auth import get_optional_current_user, CurrentUser
from app.services.extractor import extract_from_url, extract_from_document, sanitize_text, extract_domain
from app.services.claim_extractor import extract_claims
from app.services.source_verifier import evaluate_source
from app.services.fact_checking_engine import retrieve_evidence_for_claim
from app.services.credibility_scorer import compute_credibility, detect_linguistic_manipulation
from app.services.ai_explainer import generate_explanations

router = APIRouter(prefix="/api/analyze", tags=["AI News Analyzer"])


@router.post("", response_model=CredibilityReportResponse)
def analyze_news(
    req: AnalyzeRequest,
    current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
    db: Session = Depends(get_db),
):
    """
    Executes the 8-step AI verification pipeline:
    1. Content extraction & normalization
    2. Atomic claim decomposition
    3. Query generation
    4. Authoritative source retrieval
    5. Evidence ranking (supporting vs contradicting)
    6. Multi-factor credibility scoring with abstention
    7. Dual-mode AI explanation synthesis
    8. Structured credibility report generation
    """
    input_type = req.input_type.lower()
    title = req.title or ""
    content = ""
    author = "Uncredited / Anonymous"
    publish_date = None
    source_url = None
    domain = "unspecified"

    # Step 1: Content Extraction
    if input_type == "url":
        if not req.url:
            raise HTTPException(status_code=400, detail="URL is required for URL analysis.")
        source_url = req.url
        extracted = extract_from_url(req.url)
        title = title or extracted["title"]
        content = extracted["content"]
        author = extracted.get("author") or "Editorial Staff"
        publish_date = extracted.get("publish_date")
        domain = extracted["domain"]
    elif input_type == "document":
        doc_text = req.document_text or req.content or ""
        if not doc_text.strip():
            raise HTTPException(status_code=400, detail="Document content cannot be empty.")
        extracted = extract_from_document(doc_text, title)
        title = title or extracted["title"]
        content = extracted["content"]
        domain = "document.upload"
    else:  # 'text'
        content = sanitize_text(req.content or "")
        if not content:
            raise HTTPException(status_code=400, detail="Text content or headline cannot be empty.")
        if not title:
            # First sentence as title
            first_sent = content.split("\n")[0].split(".")[0]
            title = first_sent[:120] if len(first_sent) > 10 else "Submitted Claim Analysis"
        domain = "text.submission"

    # Step 2 & 3: Atomic Claim Decomposition & Search Query Generation
    raw_claims = extract_claims(content, title)
    
    # Step 4 & 5: Evidence Retrieval & Domain Evaluation
    domain_info = evaluate_source(domain if domain not in ("document.upload", "text.submission") else "")
    all_supporting: List[dict] = []
    all_contradicting: List[dict] = []
    max_claim_sim = 0.0

    structured_claims: List[ClaimItem] = []

    for c in raw_claims:
        supp, contra, sim = retrieve_evidence_for_claim(c["claim_text"], db)
        if sim > max_claim_sim:
            max_claim_sim = sim
            
        all_supporting.extend(supp)
        all_contradicting.extend(contra)

        # Claim-level verdict
        if contra:
            claim_verdict = "Contradicted by evidence"
            confidence = 90.0
            explanation = f"Contradicted by fact-check investigation from {contra[0]['source_name']}."
        elif supp:
            claim_verdict = "Supported by evidence"
            confidence = 88.0
            explanation = f"Substantiated by public record from {supp[0]['source_name']}."
        else:
            claim_verdict = "Unverified"
            confidence = 35.0
            explanation = "No authoritative fact-check or nodal evidence found to verify this specific sentence."

        structured_claims.append(ClaimItem(
            claim_id=c["claim_id"],
            claim_text=c["claim_text"],
            verdict=claim_verdict,
            confidence=confidence,
            explanation=explanation,
            supporting_sources_count=len(supp),
            contradicting_sources_count=len(contra),
            citations=[{"source": s["source_name"], "url": s["source_url"]} for s in (supp + contra)[:3]]
        ))

    # Deduplicate aggregated evidence
    seen_urls = set()
    dedup_supporting = []
    for s in all_supporting:
        if s["source_url"] not in seen_urls:
            seen_urls.add(s["source_url"])
            dedup_supporting.append(s)

    seen_urls = set()
    dedup_contradicting = []
    for c in all_contradicting:
        if c["source_url"] not in seen_urls:
            seen_urls.add(c["source_url"])
            dedup_contradicting.append(c)

    # Detect Linguistic and Emotional Manipulation
    warnings_raw = detect_linguistic_manipulation(content, title)

    # Step 6: Multi-Factor Credibility Scoring with Abstention Logic
    overall_score, verdict, confidence_score = compute_credibility(
        supporting_evidence=dedup_supporting,
        contradicting_evidence=dedup_contradicting,
        source_reputation=domain_info["reputation_score"],
        match_confidence=max_claim_sim,
        warnings=warnings_raw,
        is_official_domain=domain_info["is_official_government"],
    )

    # Step 7: Dual-Mode AI Explanation Synthesis
    explanations = generate_explanations(
        title=title,
        claims=[c.model_dump() for c in structured_claims],
        supporting_evidence=dedup_supporting,
        contradicting_evidence=dedup_contradicting,
        source_info=domain_info,
        verdict=verdict,
        credibility_score=overall_score,
        warnings=warnings_raw,
    )

    # Step 8: Persist Analysis in DB
    analysis_record = AnalysisDB(
        user_id=current_user.id if current_user else None,
        title=title,
        input_type=input_type,
        input_content=content,
        extracted_domain=domain,
        source_url=source_url,
        author=author,
        publish_date=publish_date,
        overall_credibility_score=overall_score,
        verdict=verdict,
        confidence_score=confidence_score,
        claims_json=json.dumps([c.model_dump() for c in structured_claims]),
        supporting_evidence_json=json.dumps(dedup_supporting),
        contradicting_evidence_json=json.dumps(dedup_contradicting),
        source_credibility_json=json.dumps(domain_info),
        warnings_json=json.dumps(warnings_raw),
        ai_explanation_standard=explanations["standard"],
        ai_explanation_beginner=explanations["beginner"],
        is_saved=False,
        is_public=True,
    )
    db.add(analysis_record)
    db.commit()
    db.refresh(analysis_record)

    return CredibilityReportResponse(
        id=analysis_record.id,
        title=analysis_record.title,
        input_type=analysis_record.input_type,
        input_content=analysis_record.input_content,
        extracted_domain=analysis_record.extracted_domain,
        source_url=analysis_record.source_url,
        author=analysis_record.author,
        publish_date=analysis_record.publish_date,
        overall_credibility_score=analysis_record.overall_credibility_score,
        verdict=analysis_record.verdict,
        confidence_score=analysis_record.confidence_score,
        claims=structured_claims,
        supporting_evidence=[EvidenceItem(**e) for e in dedup_supporting],
        contradicting_evidence=[EvidenceItem(**e) for e in dedup_contradicting],
        source_credibility=SourceCredibilityBreakdown(**domain_info),
        warnings=[WarningItem(**w) for w in warnings_raw],
        ai_explanation_standard=analysis_record.ai_explanation_standard,
        ai_explanation_beginner=analysis_record.ai_explanation_beginner,
        is_saved=analysis_record.is_saved,
        is_public=analysis_record.is_public,
        share_token=analysis_record.share_token,
        created_at=analysis_record.created_at,
    )


@router.post("/upload-document")
async def upload_document(file: UploadFile = File(...)):
    """Uploads a document file (.txt, .md, .json) and extracts text for analysis."""
    contents = await file.read()
    try:
        text = contents.decode("utf-8")
    except UnicodeDecodeError:
        text = contents.decode("latin-1", errors="ignore")
    return {
        "filename": file.filename,
        "content": text[:30000],
        "size_bytes": len(contents),
    }


@router.get("/demo-examples")
def get_demo_examples():
    """Returns real-world demonstration examples for one-click testing."""
    return [
        {
            "id": "ex-phishing",
            "title": "PM Free Laptop Yojana 2026 Registration Link",
            "type": "text",
            "content": "URGENT WARNING: Prime Minister Free Laptop Yojana 2026 has been launched! All students in India are eligible to receive free high-end laptops. Register immediately on http://freelaptop-yojana.online before midnight. Share with 10 friends!",
            "expected_verdict": "Contradicted by evidence",
            "tag": "Phishing / Cyber Fraud",
        },
        {
            "id": "ex-verified-isro",
            "title": "ISRO Launches Meteorological Satellite INSAT-3DS",
            "type": "text",
            "content": "The Indian Space Research Organisation (ISRO) successfully launched the INSAT-3DS meteorological satellite aboard GSLV-F14 from Sriharikota, enhancing weather forecasting and disaster warning capabilities.",
            "expected_verdict": "Supported by evidence",
            "tag": "Verified Science News",
        },
        {
            "id": "ex-misleading-health",
            "title": "Raw Garlic Cures All Viral Infections in 48 Hours",
            "type": "text",
            "content": "SHOCKING TRUTH: Doctors and pharmaceutical companies don't want you to know this! Eating raw garlic on an empty stomach completely destroys all viruses, cures viral flu and respiratory diseases within 48 hours guaranteed. Forward to everyone!",
            "expected_verdict": "Contradicted / Misleading",
            "tag": "Health Misinformation",
        },
        {
            "id": "ex-unverified-rumor",
            "title": "Unverified City Underground Metro Secret Expansion Rumor",
            "type": "text",
            "content": "A new subterranean railway line is secretly being constructed under the old district clock tower without any public municipal council notification.",
            "expected_verdict": "Unverified (Abstention Mode)",
            "tag": "Unverified Rumor",
        },
    ]
