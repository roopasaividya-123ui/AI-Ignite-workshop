"""
app/services/source_verifier.py — Domain and publisher authenticity evaluator.
"""

from typing import Dict, Any, List


# Known high-trust official government and multilateral domains
GOV_AND_HEALTH_DOMAINS = {
    "pib.gov.in": ("Press Information Bureau (Govt of India)", 99.0, "government", True),
    "factcheck.pib.gov.in": ("PIB Fact Check Unit", 100.0, "government", True),
    "india.gov.in": ("National Portal of India", 98.0, "government", True),
    "mygov.in": ("MyGov Citizen Engagement Platform", 98.0, "government", True),
    "who.int": ("World Health Organization (WHO)", 98.0, "health_authority", True),
    "un.org": ("United Nations", 98.0, "multilateral", True),
    "unicef.org": ("UNICEF", 98.0, "multilateral", True),
    "cdc.gov": ("Centers for Disease Control and Prevention", 96.0, "health_authority", True),
    "mohfw.gov.in": ("Ministry of Health & Family Welfare", 98.0, "government", True),
    "rbi.org.in": ("Reserve Bank of India", 99.0, "government", True),
    "isro.gov.in": ("Indian Space Research Organisation", 99.0, "government", True),
    "sci.gov.in": ("Supreme Court of India", 99.0, "government", True),
}

# Certified IFCN Fact-Checking Organizations
FACT_CHECKER_DOMAINS = {
    "altnews.in": ("Alt News India", 95.0, "fact_checker", True),
    "boomlive.in": ("BOOM Live", 95.0, "fact_checker", True),
    "factly.in": ("Factly", 95.0, "fact_checker", True),
    "vishvasnews.com": ("Vishvas News", 94.0, "fact_checker", True),
    "snopes.com": ("Snopes", 94.0, "fact_checker", True),
    "politifact.com": ("PolitiFact", 94.0, "fact_checker", True),
    "fullfact.org": ("Full Fact UK", 95.0, "fact_checker", True),
    "thequint.com": ("The Quint - WebQoof", 90.0, "fact_checker", True),
}

# Reputed Global & National News Agencies
NEWS_AGENCIES = {
    "reuters.com": ("Reuters International News", 94.0, "news_agency", False),
    "apnews.com": ("Associated Press (AP)", 94.0, "news_agency", False),
    "bbc.com": ("BBC News", 92.0, "news_agency", False),
    "thehindu.com": ("The Hindu", 90.0, "news_agency", False),
    "indianexpress.com": ("The Indian Express", 89.0, "news_agency", False),
    "ptinews.com": ("Press Trust of India (PTI)", 93.0, "news_agency", False),
    "hindustantimes.com": ("Hindustan Times", 88.0, "news_agency", False),
    "ndtv.com": ("NDTV", 87.0, "news_agency", False),
    "timesofindia.indiatimes.com": ("Times of India", 85.0, "news_agency", False),
}

# Known Suspicious or Fake News Outlets / Scam Domains
SUSPICIOUS_DOMAINS = {
    "freelaptop-yojana.online": ("Fake Scheme Phishing Domain", 5.0, "phishing"),
    "gov-recharge-free.xyz": ("Fake Telecom Subsidy Scam", 4.0, "phishing"),
    "breaking-secret-news.blog": ("Unverified Clickbait Blog", 15.0, "clickbait"),
    "dailybuzz24.info": ("Ad-farm Misinformation Site", 12.0, "clickbait"),
    "whatsapp-forward.site": ("Unverified Viral Rumor Host", 10.0, "rumor_host"),
}


def evaluate_source(domain: str) -> Dict[str, Any]:
    """
    Evaluates domain reputation, IFCN certification, government authenticity,
    and tier classification.
    """
    clean_domain = domain.lower().replace("www.", "").strip()
    notes: List[str] = []

    # Check Government / Health
    if clean_domain.endswith(".gov.in") or clean_domain.endswith(".nic.in") or clean_domain.endswith(".gov"):
        notes.append("Official government domain (.gov / .gov.in)")
        name = "Official Government Source"
        rating = 97.0
        category = "government"
        if clean_domain in GOV_AND_HEALTH_DOMAINS:
            name, rating, category, _ = GOV_AND_HEALTH_DOMAINS[clean_domain]
        return {
            "domain": clean_domain,
            "source_name": name,
            "reputation_score": rating,
            "is_trusted_publisher": True,
            "is_official_government": True,
            "is_ifcn_fact_checker": False,
            "author_transparency": "High (Official Spokesperson / Ministry)",
            "publisher_tier": "Tier 1 - Sovereign & Official Record",
            "notes": notes,
        }

    # Check WHO / UN
    if clean_domain in GOV_AND_HEALTH_DOMAINS:
        name, rating, category, is_ifcn = GOV_AND_HEALTH_DOMAINS[clean_domain]
        notes.append("Authoritative international body")
        return {
            "domain": clean_domain,
            "source_name": name,
            "reputation_score": rating,
            "is_trusted_publisher": True,
            "is_official_government": True,
            "is_ifcn_fact_checker": False,
            "author_transparency": "High",
            "publisher_tier": "Tier 1 - Authoritative Global Body",
            "notes": notes,
        }

    # Check Certified Fact Checkers
    if clean_domain in FACT_CHECKER_DOMAINS:
        name, rating, category, is_ifcn = FACT_CHECKER_DOMAINS[clean_domain]
        notes.append("International Fact-Checking Network (IFCN) signatory")
        return {
            "domain": clean_domain,
            "source_name": name,
            "reputation_score": rating,
            "is_trusted_publisher": True,
            "is_official_government": False,
            "is_ifcn_fact_checker": True,
            "author_transparency": "High (Editorial Byline & Corrections Policy)",
            "publisher_tier": "Tier 1 - Certified Fact-Checking Organization",
            "notes": notes,
        }

    # Check Established News Agencies
    if clean_domain in NEWS_AGENCIES:
        name, rating, category, _ = NEWS_AGENCIES[clean_domain]
        notes.append("Established mainstream news agency with editorial board")
        return {
            "domain": clean_domain,
            "source_name": name,
            "reputation_score": rating,
            "is_trusted_publisher": True,
            "is_official_government": False,
            "is_ifcn_fact_checker": False,
            "author_transparency": "High",
            "publisher_tier": "Tier 2 - Reputed News Organization",
            "notes": notes,
        }

    # Check Suspicious / Phishing
    if clean_domain in SUSPICIOUS_DOMAINS or any(ext in clean_domain for ext in [".xyz", ".top", ".buzz", ".click"]):
        name, rating, category = SUSPICIOUS_DOMAINS.get(
            clean_domain, ("Unverified / Low Reputation TLD Domain", 25.0, "suspicious")
        )
        notes.append("Domain exhibits suspicious TLD or is flagged on misinformation databases")
        return {
            "domain": clean_domain,
            "source_name": name,
            "reputation_score": rating,
            "is_trusted_publisher": False,
            "is_official_government": False,
            "is_ifcn_fact_checker": False,
            "author_transparency": "Low / Anonymous",
            "publisher_tier": "Unverified - High Risk of Misinformation",
            "notes": notes,
        }

    # Default / Unknown source
    return {
        "domain": clean_domain,
        "source_name": clean_domain.capitalize() if clean_domain else "Unidentified Source",
        "reputation_score": 52.0,
        "is_trusted_publisher": False,
        "is_official_government": False,
        "is_ifcn_fact_checker": False,
        "author_transparency": "Moderate / Unverified",
        "publisher_tier": "Tier 3 - Independent / Unverified Web Source",
        "notes": ["Domain is not in the certified registry; independent claim corroboration required."],
    }
