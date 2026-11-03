"""
app/services/ai_explainer.py — Natural language reasoning, beginner explanations, and transparency generator.
"""

from typing import List, Dict, Any


def generate_explanations(
    title: str,
    claims: List[Dict[str, Any]],
    supporting_evidence: List[Dict[str, Any]],
    contradicting_evidence: List[Dict[str, Any]],
    source_info: Dict[str, Any],
    verdict: str,
    credibility_score: float,
    warnings: List[Dict[str, str]],
) -> Dict[str, str]:
    """
    Generates standard structured reasoning and an accessible 'Beginner Mode' explanation.
    """
    supp_names = [e["source_name"] for e in supporting_evidence]
    contra_names = [e["source_name"] for e in contradicting_evidence]

    # ── Standard Analysis Explanation ─────────────────────────────────────────
    standard_sections = []
    
    # 1. Overview & Verdict Reasoning
    standard_sections.append(
        f"### Credibility Assessment: {verdict} (Score: {credibility_score}/100)\n"
        f"TruthGuard AI evaluated the submitted content across {len(claims)} primary factual assertion(s), "
        f"corroborating statements against indexed records from verified fact-checkers, government bureaus, "
        f"and established press registries."
    )

    # 2. Key Claims & Discovered Evidence
    standard_sections.append("#### Claim & Evidence Synthesis:")
    if contradicting_evidence:
        top_contra = contradicting_evidence[0]
        standard_sections.append(
            f"- **Contradicting Evidence Discovered**: Authoritative fact-checking verification from "
            f"**{top_contra['source_name']}** indicates this claim is unsubstantiated or debunked. "
            f"Summary from investigation: *\"{top_contra['quote_or_summary']}\"*"
        )
    if supporting_evidence:
        top_supp = supporting_evidence[0]
        standard_sections.append(
            f"- **Supporting Evidence Discovered**: Corroboration identified from "
            f"**{top_supp['source_name']}** (*\"{top_supp['quote_or_summary']}\"*)."
        )

    # 3. What is Missing or Misrepresented
    standard_sections.append("#### Contextual Integrity & Missing Information:")
    if verdict == "Contradicted by evidence":
        standard_sections.append(
            "This item lacks verifiable documentation from designated nodal authorities. "
            "Key operational details (official press releases, gazette notifications, or verifiable primary spokespersons) "
            "are completely absent."
        )
    elif verdict == "Misleading":
        standard_sections.append(
            "The content presents genuine elements but omits critical context, caveats, or timelines, "
            "leading readers to an erroneous conclusion."
        )
    elif verdict == "Unverified":
        standard_sections.append(
            "TruthGuard's verification pipeline found **insufficient external evidence** to substantiate or refute "
            "these assertions at this time. Per our strict non-fabrication doctrine, we abstain from drawing an unproven conclusion."
        )
    else:
        standard_sections.append(
            "Assertions align with public statements and documented announcements from established primary channels."
        )

    # 4. Source Transparency & Warning Flags
    if warnings:
        warn_bullets = "\n".join([f"- **{w['category'].replace('_', ' ').title()}**: {w['message']}" for w in warnings])
        standard_sections.append(f"#### Behavioral & Content Flags:\n{warn_bullets}")

    standard_explanation = "\n\n".join(standard_sections)

    # ── Beginner Mode Explanation ("Explain Like I'm 10 / Beginner") ────────────
    beginner_sections = []
    beginner_sections.append(
        f"👋 **In Simple Words:**\n"
        f"We checked the story **\"{title[:80]}...\"** to see if you can trust it."
    )

    if verdict == "Contradicted by evidence":
        beginner_sections.append(
            f"❌ **Verdict:** This story is **NOT TRUE**.\n\n"
            f"• **What it claimed:** Someone shared a message claiming this news happened.\n"
            f"• **What the facts show:** Real checkers at **{', '.join(contra_names[:2]) or 'PIB Fact Check'}** looked into this and found it was fabricated or a scam.\n"
            f"• **Why you should care:** Sharing false news causes panic or tricks people into clicking dangerous links. Please do not forward this!"
        )
    elif verdict == "Misleading":
        beginner_sections.append(
            f"⚠️ **Verdict:** This story is **MISLEADING (Half-True)**.\n\n"
            f"• **What it claimed:** The headline sounds dramatic or exciting.\n"
            f"• **What the facts show:** While a small part might be real, important facts were left out or twisted to make people angry or curious.\n"
            f"• **Tip:** Always read the full story and check if official departments actually confirmed it."
        )
    elif verdict == "Supported by evidence" or verdict == "Likely accurate":
        beginner_sections.append(
            f"✅ **Verdict:** This story is **VERIFIED & SUPPORTED**.\n\n"
            f"• **What it claimed:** A factual event or official government announcement.\n"
            f"• **What the facts show:** Trustworthy agencies like **{', '.join(supp_names[:2]) or 'official news'}** have confirmed this information.\n"
            f"• **Tip:** This information is safe and supported by reliable evidence."
        )
    else:
        beginner_sections.append(
            f"🔍 **Verdict:** **UNVERIFIED (We Need More Proof)**.\n\n"
            f"• **What happened:** We searched trusted databases and could not find enough solid proof either way.\n"
            f"• **Our Rule:** We never guess! If we don't have enough clear facts, we will tell you honestly that it is unverified rather than giving you a fake answer.\n"
            f"• **Tip:** Be careful and wait for official updates before believing or sharing this."
        )

    beginner_explanation = "\n\n".join(beginner_sections)

    return {
        "standard": standard_explanation,
        "beginner": beginner_explanation,
    }
