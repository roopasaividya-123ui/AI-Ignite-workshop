"""
app/services/claim_extractor.py — NLP-driven atomic claim extraction and query generation.
"""

import re
from typing import List, Dict, Any


def extract_claims(text: str, title: str = "") -> List[Dict[str, Any]]:
    """
    Decomposes an article or message into distinct, verifiable factual claims.
    Filters out opinions, rhetorical questions, and salutations.
    """
    claims = []
    
    # Pre-clean
    full_text = f"{title}. {text}" if title and title not in text else text
    sentences = re.split(r"(?<=[.!?])\s+", full_text.strip())
    
    # Filter candidates with verifiable predicates
    verifiable_indicators = [
        r"\b(?:announced|approved|launched|reported|claimed|discovered|banned|confirmed)\b",
        r"\b(?:increased|decreased|allocated|invested|signed|declared|warned|issued)\b",
        r"\b(?:government|ministry|who|isro|rbi|pib|court|police|prime minister|president)\b",
        r"\b(?:percent|%|crore|lakh|million|billion|rupees|dollar|\$|rs\.?)\b",
        r"\b(?:cause|cures|prevents|deadly|fatal|secret|free|subsidy|scheme)\b",
    ]
    pattern = re.compile("|".join(verifiable_indicators), re.IGNORECASE)

    claim_idx = 1
    seen_normalized = set()

    # If title exists and is substantial, consider it primary claim 1
    if title and len(title.strip()) > 15:
        norm_title = re.sub(r"[^\w\s]", "", title.lower())
        claims.append({
            "claim_id": claim_idx,
            "claim_text": title.strip(),
            "query": generate_search_query(title),
            "claim_type": "Headline Claim",
        })
        seen_normalized.add(norm_title)
        claim_idx += 1

    for sentence in sentences:
        s = sentence.strip()
        if len(s) < 25 or len(s) > 250:
            continue
        # Avoid questions or greeting chatter
        if s.endswith("?") or s.lower().startswith(("hello", "hi ", "dear friends", "please share")):
            continue

        norm = re.sub(r"[^\w\s]", "", s.lower())
        if norm in seen_normalized:
            continue

        # Check if sentence has factual claim indicators
        if pattern.search(s) or any(char.isdigit() for char in s):
            seen_normalized.add(norm)
            claims.append({
                "claim_id": claim_idx,
                "claim_text": s,
                "query": generate_search_query(s),
                "claim_type": "Factual Assertion",
            })
            claim_idx += 1
            if len(claims) >= 5:
                break

    # If no claims matched the regex, fall back to the first non-trivial sentences
    if not claims:
        candidates = [s.strip() for s in sentences if len(s.strip()) > 20 and not s.endswith("?")]
        for s in candidates[:3]:
            claims.append({
                "claim_id": claim_idx,
                "claim_text": s,
                "query": generate_search_query(s),
                "claim_type": "General Assertion",
            })
            claim_idx += 1

    return claims


def generate_search_query(claim_text: str) -> str:
    """
    Generates an optimized search query from claim text by extracting key entities,
    action verbs, and removing stop words.
    """
    stop_words = {
        "a", "an", "the", "in", "on", "at", "to", "for", "of", "with", "is", "are",
        "was", "were", "and", "or", "that", "this", "it", "as", "by", "from", "be",
        "has", "have", "had", "will", "would", "can", "could", "should", "all", "please"
    }
    words = re.findall(r"\b[A-Za-z0-9_-]+\b", claim_text)
    filtered = [w for w in words if w.lower() not in stop_words]
    
    # Keep top 6-8 relevant keywords
    query_terms = filtered[:8]
    return " ".join(query_terms)
