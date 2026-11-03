"""
app/services/credibility_scorer.py — Multi-factor evidence-based credibility scoring & abstention logic.
"""

import re
from typing import Dict, Any, List, Tuple


SENSATIONAL_PATTERNS = [
    r"\b(?:shocking|mind-blowing|doctors don't want you to know|miracle cure|magic pill)\b",
    r"\b(?:share before it gets deleted|media will not show this|hidden truth exposed)\b",
    r"\b(?:100% guaranteed|free recharge|free laptop|lottery winner|click here now)\b",
    r"\b(?:urgent warning|secret leaked|beware of this|forward to everyone)\b",
]

CLICKBAIT_PATTERNS = [
    r"\b(?:you won't believe|this will happen next|number \d+ will shock you)\b",
    r"!{2,}|\?{2,}",
]


def detect_linguistic_manipulation(text: str, title: str = "") -> List[Dict[str, str]]:
    """Analyzes text for emotional manipulation, sensationalism, and clickbait patterns."""
    warnings = []
    combined = f"{title} {text}".strip()

    # 1. Emotional Urgency / Viral Forward Coercion
    urgency_matches = []
    for pattern in SENSATIONAL_PATTERNS:
        found = re.findall(pattern, combined, re.IGNORECASE)
        if found:
            urgency_matches.extend(found)

    if urgency_matches:
        warnings.append({
            "category": "emotional_manipulation",
            "level": "warning",
            "message": f"Contains emotional urgency or sensational phrases designed to provoke uncritical sharing: '{', '.join(set(urgency_matches[:3]))}'",
        })

    # 2. Clickbait Patterns
    clickbait_matches = []
    for pattern in CLICKBAIT_PATTERNS:
        found = re.findall(pattern, title if title else combined[:300], re.IGNORECASE)
        if found:
            clickbait_matches.extend(found)

    if clickbait_matches:
        warnings.append({
            "category": "clickbait",
            "level": "alert",
            "message": "Headline exhibits clickbait formatting or exaggerated punctuation to inflate curiosity.",
        })

    # 3. Excessive Capitalization
    words = combined.split()
    caps_words = [w for w in words if len(w) > 3 and w.isupper() and w.isalpha()]
    if len(caps_words) >= 4:
        warnings.append({
            "category": "sensationalism",
            "level": "info",
            "message": f"Contains multiple all-capitalized emphasis words ({', '.join(caps_words[:4])}), common in inflammatory messaging.",
        })

    return warnings


def compute_credibility(
    supporting_evidence: List[Dict[str, Any]],
    contradicting_evidence: List[Dict[str, Any]],
    source_reputation: float,
    match_confidence: float,
    warnings: List[Dict[str, str]],
    is_official_domain: bool = False,
) -> Tuple[float, str, float]:
    """
    Computes evidence-backed credibility score (0 - 100), verdict, and assessment confidence.
    Enforces abstention when evidence is insufficient!

    Verdicts:
    - 'Supported by evidence' (score >= 80)
    - 'Likely accurate' (score 65 - 79)
    - 'Misleading' (score 35 - 64)
    - 'Contradicted by evidence' (score < 35)
    - 'Unverified' (insufficient evidence to conclude)
    """
    total_supp = len(supporting_evidence)
    total_contra = len(contradicting_evidence)

    # 1. Abstention Check: If no external corroboration found and not an official domain
    if total_supp == 0 and total_contra == 0:
        if is_official_domain and source_reputation >= 90:
            # Official source with no counter claims
            score = round(min(88.0, source_reputation * 0.9), 1)
            verdict = "Supported by evidence"
            confidence = 82.0
            return score, verdict, confidence
        else:
            # Abstain from guessing
            score = 50.0
            verdict = "Unverified"
            confidence = 35.0
            return score, verdict, confidence

    # 2. Weighted Evidence Balance
    # Calculate evidence strength
    supp_weight = sum(item.get("credibility_rating", 70.0) for item in supporting_evidence)
    contra_weight = sum(item.get("credibility_rating", 70.0) for item in contradicting_evidence)

    # Base score centered on evidence proportion
    total_weight = supp_weight + contra_weight
    if total_weight > 0:
        evidence_ratio = supp_weight / total_weight
        base_score = 15.0 + (evidence_ratio * 75.0)
    else:
        base_score = 50.0

    # 3. Factor in source reputation (30% weight)
    blended_score = (base_score * 0.7) + (source_reputation * 0.3)

    # 4. Apply penalties for manipulation / warnings
    penalty = len(warnings) * 4.5
    final_score = max(5.0, min(98.0, blended_score - penalty))

    # 5. Assign Verdict
    if total_contra >= 1 and (total_contra > total_supp or total_supp == 0):
        if final_score > 40:
            final_score = min(final_score, 32.0)
        verdict = "Contradicted by evidence"
    elif total_supp > 0 and total_contra == 0:
        if final_score >= 80:
            verdict = "Supported by evidence"
        else:
            verdict = "Likely accurate"
    elif total_supp > 0 and total_contra > 0:
        verdict = "Misleading"
        final_score = max(38.0, min(62.0, final_score))
    else:
        verdict = "Unverified"

    confidence = round(min(96.0, max(50.0, (match_confidence * 100.0) + (len(supporting_evidence) + len(contradicting_evidence)) * 5)), 1)
    return round(final_score, 1), verdict, confidence
