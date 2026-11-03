"""
app/services/fact_checking_engine.py — Evidence retrieval and cross-source verification engine.
"""

import math
import re
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session

from app.models.db_models import FactCheckRecordDB
from app.services.source_verifier import evaluate_source


def compute_similarity(text_a: str, text_b: str) -> float:
    """
    Computes a composite semantic similarity score between two texts using:
    - Jaccard token overlap
    - Substring / phrase match bonus
    - Keyword containment
    """
    def tokenize(s: str) -> set:
        clean = re.sub(r"[^\w\s]", " ", s.lower())
        tokens = [w for w in clean.split() if len(w) > 2]
        return set(tokens)

    set_a = tokenize(text_a)
    set_b = tokenize(text_b)

    if not set_a or not set_b:
        return 0.0

    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    jaccard = len(intersection) / len(union)

    # Key entity matching bonus (e.g. acronyms or specific nouns)
    special_entities = [w for w in set_a if len(w) >= 4]
    entity_matches = sum(1 for w in special_entities if w in set_b)
    entity_ratio = (entity_matches / max(len(special_entities), 1)) if special_entities else 0.0

    score = (0.5 * jaccard) + (0.5 * entity_ratio)
    return min(1.0, score)


def retrieve_evidence_for_claim(
    claim_text: str,
    db: Session,
    threshold: float = 0.22,
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], float]:
    """
    Retrieves supporting and contradicting evidence for a given claim by searching
    cataloged fact checks and authoritative records.
    Returns: (supporting_evidence, contradicting_evidence, match_confidence)
    """
    supporting = []
    contradicting = []
    highest_similarity = 0.0

    # Query all indexed fact-checking records
    records = db.query(FactCheckRecordDB).all()

    for rec in records:
        sim_claim = compute_similarity(claim_text, rec.claim_reviewed)
        sim_keywords = compute_similarity(claim_text, rec.keywords + " " + rec.tags)
        sim = max(sim_claim, sim_keywords * 0.9)

        if sim > highest_similarity:
            highest_similarity = sim

        if sim >= threshold:
            domain_info = evaluate_source(rec.source_url)
            verdict_lower = rec.verdict.lower()

            evidence_item = {
                "source_name": rec.publisher,
                "source_url": rec.source_url,
                "domain": domain_info["domain"],
                "credibility_rating": domain_info["reputation_score"],
                "source_category": domain_info.get("publisher_tier", "Fact-Checker"),
                "is_ifcn_certified": domain_info["is_ifcn_fact_checker"],
                "quote_or_summary": rec.explanation,
                "publish_date": rec.review_date,
                "relevance_score": round(sim * 100, 1),
            }

            if any(term in verdict_lower for term in ["false", "fabricated", "misleading", "fake", "hoax", "altered"]):
                evidence_item["stance"] = "contradicts"
                contradicting.append(evidence_item)
            elif any(term in verdict_lower for term in ["true", "supported", "verified", "confirmed"]):
                evidence_item["stance"] = "supports"
                supporting.append(evidence_item)
            else:
                evidence_item["stance"] = "neutral"
                contradicting.append(evidence_item)

    # Sort evidence by relevance
    supporting.sort(key=lambda x: x["relevance_score"], reverse=True)
    contradicting.sort(key=lambda x: x["relevance_score"], reverse=True)

    return supporting[:4], contradicting[:4], highest_similarity
