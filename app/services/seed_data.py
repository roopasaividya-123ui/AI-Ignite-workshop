"""
app/services/seed_data.py — Initial seed data for TruthGuard AI.
Seeds trusted sources, real fact check records, educational modules, and accounts.
"""

import json
from sqlalchemy.orm import Session

from app.models.db_models import (
    UserDB,
    TrustedSourceDB,
    FactCheckRecordDB,
    QuizModuleDB,
    AnalysisDB,
)
from app.auth import hash_password


def seed_database(db: Session):
    """Populates database with initial foundational data if tables are empty."""
    
    # ── 1. Seed Users ─────────────────────────────────────────────────────────
    if db.query(UserDB).count() == 0:
        admin_user = UserDB(
            email="admin@truthguard.ai",
            full_name="TruthGuard Administrator",
            hashed_password=hash_password("Admin@123456"),
            role="admin",
            awareness_score=95,
            is_active=True,
        )
        analyst_user = UserDB(
            email="analyst@truthguard.ai",
            full_name="Senior Verification Analyst",
            hashed_password=hash_password("Analyst@123456"),
            role="analyst",
            awareness_score=88,
            is_active=True,
        )
        regular_user = UserDB(
            email="citizen@truthguard.ai",
            full_name="Aarav Sharma",
            hashed_password=hash_password("User@123456"),
            role="user",
            awareness_score=60,
            is_active=True,
        )
        db.add_all([admin_user, analyst_user, regular_user])
        db.commit()

    # ── 2. Seed Trusted Sources ───────────────────────────────────────────────
    if db.query(TrustedSourceDB).count() == 0:
        sources = [
            TrustedSourceDB(
                name="PIB Fact Check Unit",
                domain="factcheck.pib.gov.in",
                category="government",
                credibility_rating=99.0,
                country="India",
                is_ifcn_certified=True,
                description="Government of India's nodal fact-checking body under the Ministry of Information & Broadcasting.",
            ),
            TrustedSourceDB(
                name="Alt News",
                domain="altnews.in",
                category="fact_checker",
                credibility_rating=95.0,
                country="India",
                is_ifcn_certified=True,
                description="Independent, non-profit Indian fact-checking organisation certified by the International Fact-Checking Network.",
            ),
            TrustedSourceDB(
                name="BOOM Live",
                domain="boomlive.in",
                category="fact_checker",
                credibility_rating=95.0,
                country="India",
                is_ifcn_certified=True,
                description="IFCN-certified fact-checking initiative focused on digital literacy and debunking viral claims across social media.",
            ),
            TrustedSourceDB(
                name="Factly",
                domain="factly.in",
                category="fact_checker",
                credibility_rating=94.0,
                country="India",
                is_ifcn_certified=True,
                description="Data-driven journalism and verified fact-checking entity based in Hyderabad, India.",
            ),
            TrustedSourceDB(
                name="World Health Organization (WHO)",
                domain="who.int",
                category="health_authority",
                credibility_rating=98.0,
                country="Global",
                is_ifcn_certified=True,
                description="United Nations specialized health agency dedicated to international public health and myth-busting.",
            ),
            TrustedSourceDB(
                name="Reuters Fact Check",
                domain="reuters.com",
                category="news_agency",
                credibility_rating=94.0,
                country="Global",
                is_ifcn_certified=True,
                description="Global news wire fact-checking team inspecting international claims and social media assertions.",
            ),
            TrustedSourceDB(
                name="Associated Press Fact Check",
                domain="apnews.com",
                category="news_agency",
                credibility_rating=94.0,
                country="Global",
                is_ifcn_certified=True,
                description="Not-for-profit news cooperative with rigorous verification standards.",
            ),
            TrustedSourceDB(
                name="The Hindu",
                domain="thehindu.com",
                category="news_agency",
                credibility_rating=90.0,
                country="India",
                is_ifcn_certified=False,
                description="Reputed Indian national newspaper with strict editorial governance and transparent bylines.",
            ),
        ]
        db.add_all(sources)
        db.commit()

    # ── 3. Seed Fact Check Records ────────────────────────────────────────────
    if db.query(FactCheckRecordDB).count() == 0:
        records = [
            FactCheckRecordDB(
                claim_reviewed="Government is distributing free laptops to all college students under PM Free Laptop Yojana 2026. Click link to register.",
                verdict="False / Phishing Scam",
                publisher="PIB Fact Check",
                source_url="https://factcheck.pib.gov.in/pm-free-laptop-scheme-hoax",
                review_date="2026-03-15",
                explanation="PIB Fact Check confirmed no such scheme named 'PM Free Laptop Yojana' has been announced by the Government of India. The circulating link is a malicious phishing attempt to steal personal banking information.",
                keywords="laptop free yojana students government pm scheme registration link scam",
                tags="phishing,government_schemes,fraud",
            ),
            FactCheckRecordDB(
                claim_reviewed="WHO declares new global emergency lockdown order for deadly disease outbreak across Asia and Europe.",
                verdict="False / Fabricated",
                publisher="World Health Organization (WHO)",
                source_url="https://who.int/emergencies/disease-rumor-debunk",
                review_date="2026-04-10",
                explanation="The World Health Organization confirmed it has issued no worldwide lockdown advisories or emergency closures. The text circulating on WhatsApp mimics official WHO memos without authorization.",
                keywords="who lockdown emergency disease virus outbreak travel ban quarantine",
                tags="health,pandemic_rumor,whatsapp_forward",
            ),
            FactCheckRecordDB(
                claim_reviewed="Reserve Bank of India (RBI) declared ₹500 currency notes with star (*) symbol invalid or counterfeit.",
                verdict="False / Misleading",
                publisher="BOOM Live",
                source_url="https://boomlive.in/fact-check/rbi-star-series-500-rupee-note-valid-22419",
                review_date="2026-01-22",
                explanation="RBI explicitly clarified that banknotes with a star symbol in the number panel are completely genuine and legal tender. The star indicates replacement notes issued in packets with defectively printed serials.",
                keywords="rbi reserve bank 500 currency note star symbol invalid fake legal tender",
                tags="finance,currency,rbi",
            ),
            FactCheckRecordDB(
                claim_reviewed="Eating raw garlic or ginger on empty stomach permanently cures virus infections and respiratory illnesses in 48 hours.",
                verdict="False / Unproven Medical Advice",
                publisher="Factly",
                source_url="https://factly.in/health-myths-raw-garlic-cures-viral-infections",
                review_date="2026-02-18",
                explanation="While garlic and ginger offer mild culinary and antioxidant properties, there is zero clinical or peer-reviewed scientific proof that they cure or eliminate active viral or respiratory infections.",
                keywords="garlic ginger cure viral infection respiratory medical remedy natural empty stomach",
                tags="health_misinformation,unverified_remedy",
            ),
            FactCheckRecordDB(
                claim_reviewed="ISRO successfully launches next-generation meteorological satellite INSAT-3DS aboard GSLV-F14.",
                verdict="True / Verified",
                publisher="Press Information Bureau (PIB)",
                source_url="https://pib.gov.in/PressReleasePage.aspx?PRID=2006789",
                review_date="2026-02-17",
                explanation="ISRO confirmed the precise orbit injection of INSAT-3DS meteorological satellite from Sriharikota, verified by the Ministry of Earth Sciences.",
                keywords="isro launch insat satellite gslv weather sriharikota earth sciences",
                tags="science,space,isro,official",
            ),
            FactCheckRecordDB(
                claim_reviewed="Ministry of Finance approves 4 percent hike in Dearness Allowance (DA) and Dearness Relief for central government employees and pensioners.",
                verdict="True / Verified",
                publisher="Ministry of Finance / PIB",
                source_url="https://pib.gov.in/PressReleasePage.aspx?PRID=2012345",
                review_date="2026-03-07",
                explanation="Union Cabinet chaired by Prime Minister approved a 4% increase in DA and DR for eligible central government employees and pensioners.",
                keywords="dearness allowance da hike 4 percent cabinet central government employees pensioners finance",
                tags="government,finance,cabinet_decision",
            ),
            FactCheckRecordDB(
                claim_reviewed="Viral video showing violent military border clash claimed to be from recent high-altitude standoff.",
                verdict="Misleading / Recycled Old Footage",
                publisher="Alt News",
                source_url="https://altnews.in/old-military-video-shared-as-recent-border-clash",
                review_date="2026-05-02",
                explanation="Alt News conducted a reverse video analysis and confirmed the clip is archival military exercise footage from 2020 in a different sector, falsely shared with misleading claims.",
                keywords="viral video border clash military soldiers recent confrontation standoff footage",
                tags="video_misinformation,recycled_footage,alt_news",
            ),
            FactCheckRecordDB(
                claim_reviewed="Department of Telecommunications offering 3 months free mobile internet recharge to all citizens. Click link before midnight.",
                verdict="False / Phishing Fraud",
                publisher="PIB Fact Check",
                source_url="https://factcheck.pib.gov.in/dot-free-recharge-scam",
                review_date="2026-04-28",
                explanation="PIB Fact Check and DoT confirmed the message is a fraudulent trap. DoT does not provide free mobile recharge coupons.",
                keywords="dot free recharge internet mobile 3 months department telecommunications click link",
                tags="phishing,cyber_fraud,dot",
            ),
        ]
        db.add_all(records)
        db.commit()

    # ── 4. Seed Educational Awareness Modules ─────────────────────────────────
    if db.query(QuizModuleDB).count() == 0:
        modules = [
            QuizModuleDB(
                id="anatomy-of-fake-news",
                title="The Anatomy of Fake News: 7 Forms of Misinformation",
                category="Foundational Literacy",
                difficulty="Beginner",
                summary="Learn how misinformation is categorized: from satire and false connections to manipulated and completely fabricated content.",
                content="""# The Anatomy of Fake News

Information disorder is generally classified into three distinct categories:
1. **Misinformation**: Inaccurate information shared without malicious intent (e.g. sharing an outdated traffic warning by mistake).
2. **Disinformation**: Deliberately manufactured false information designed to deceive, profit, or cause harm (e.g. fake election results, pump-and-dump financial schemes).
3. **Malinformation**: Genuine information used out of context with intent to inflict damage (e.g. leaking confidential medical data).

### The 7 Common Formats:
- **Satire / Parody**: No intention to cause harm, but has the potential to fool readers.
- **Misleading Content**: Misleading use of information to frame an issue or individual.
- **Imposter Content**: When genuine sources (like BBC or PIB logos) are impersonated.
- **Fabricated Content**: New content that is 100% false, designed to deceive and do harm.
- **False Connection**: When headlines, visuals, or captions do not support the article text.
- **False Context**: When genuine content is shared with false contextual framing.
- **Manipulated Content**: When genuine information or imagery is manipulated to deceive.
""",
                questions_json=json.dumps([
                    {
                        "question_id": 1,
                        "question": "What is the key difference between misinformation and disinformation?",
                        "options": [
                            "Misinformation is always online, while disinformation is printed on paper.",
                            "Disinformation is deliberately created to deceive, while misinformation is shared without harmful intent.",
                            "Misinformation is created by governments, while disinformation is created by corporations.",
                            "There is no difference between the two terms."
                        ],
                        "correct_index": 1,
                        "explanation": "Disinformation involves deliberate malice and intent to deceive, whereas misinformation is false info spread by people who mistakenly believe it to be true."
                    },
                    {
                        "question_id": 2,
                        "question": "A sensational headline says 'Celebrity Dies in Tragic Crash', but the article only discusses a movie stunt scene. What form of disorder is this?",
                        "options": [
                            "False Connection / Clickbait",
                            "Satire",
                            "Cyber Phishing",
                            "Malinformation"
                        ],
                        "correct_index": 0,
                        "explanation": "False Connection occurs when headlines, visuals, or captions deliberately do not support the real content of the article."
                    }
                ]),
            ),
            QuizModuleDB(
                id="deepfakes-synthetic-media",
                title="Deepfakes & AI Synthetic Media Detection",
                category="Advanced AI Literacy",
                difficulty="Intermediate",
                summary="Understand how generative AI creates synthetic faces, audio clones, and video deepfakes, and how to spot telltale artifacts.",
                content="""# Deepfakes and Synthetic Media

Generative AI enables hyper-realistic creation of synthetic human voices, faces, and video sequences.

### Common Deepfake Artifacts:
1. **Unnatural Eye Blinking**: Early deepfake models often fail to capture normal human blinking frequency or eye convergence.
2. **Boundary Inconsistencies**: Observe hair fringes, ears, and neck collars. Notice if borders flicker, blur, or distort when the person turns their head.
3. **Audio-Lip Desynchronization**: Subtle lags between phoneme pronunciation (especially plosive sounds like P, B, M) and mouth movements.
4. **Lighting & Reflection Mismatches**: Look closely at pupils. Reflections in the left and right eyes should match the environment's light sources.
5. **Teeth & Jewelry Glitches**: AI models often generate teeth as a single solid white block or blur intricate necklaces and earrings.
""",
                questions_json=json.dumps([
                    {
                        "question_id": 1,
                        "question": "Which of the following is a reliable visual cue when inspecting suspected AI video deepfakes?",
                        "options": [
                            "The video has background music.",
                            "Inconsistent reflections in pupils, blurred ear borders, and unnatural teeth rendering.",
                            "The video is less than 30 seconds long.",
                            "The speaker is wearing formal clothing."
                        ],
                        "correct_index": 1,
                        "explanation": "AI generation tools frequently struggle with bilateral corneal reflections, sharp teeth rendering, and smooth hair-edge blending."
                    },
                    {
                        "question_id": 2,
                        "question": "What is 'voice cloning' primarily used for in modern cyber scams?",
                        "options": [
                            "Impersonating relatives or executives to request urgent wire transfers.",
                            "Speeding up podcast listening.",
                            "Improving Wi-Fi signal strength.",
                            "Translating text to Braille."
                        ],
                        "correct_index": 0,
                        "explanation": "Voice cloning is heavily weaponized in emergency grandparent scams and CEO fraud to trick victims into sending funds under false panic."
                    }
                ]),
            ),
            QuizModuleDB(
                id="whatsapp-viral-verification",
                title="Verifying Viral WhatsApp & Social Media Forwards",
                category="Everyday Media Hygiene",
                difficulty="Beginner",
                summary="Practical toolkit to verify viral forwards before clicking 'Share' or causing panic in family and neighborhood groups.",
                content="""# Mastering Viral Message Verification

Viral messaging applications like WhatsApp, Telegram, and Facebook Groups are prime vectors for emotional manipulation.

### The 5-Second Verification Checklist:
1. **Notice the 'Forwarded many times' label**: If a message has circulated through dozens of groups, its probability of distortion is high.
2. **Check for Emotional Coercion**: Does it demand you 'Forward to 10 friends immediately'? Real alerts from government bodies never ask citizens to forward messages to avoid bad luck.
3. **Inspect the Link Destination**: Beware of domains ending in unusual extensions (.xyz, .top, .buzz) mimicking official portals (e.g. `pm-yojana.buzz` vs `india.gov.in`).
4. **Search Google Fact Check Explorer**: Type the core sentence into Google Fact Check Explorer (`toolbox.google.com/factcheck/explorer`) or TruthGuard AI.
5. **Cross-Check with PIB or Official Ministry Portals**: Never believe a national policy announcement unless it appears on official government websites (.gov.in).
""",
                questions_json=json.dumps([
                    {
                        "question_id": 1,
                        "question": "A message claims the government will shut down the internet tonight unless you forward the text to 15 people. What should you do?",
                        "options": [
                            "Immediately forward it to 15 people just to be safe.",
                            "Recognize it as an emotional forward chain hoax, refrain from sharing, and check PIB Fact Check.",
                            "Post it on Twitter with urgent tags.",
                            "Turn off your phone."
                        ],
                        "correct_index": 1,
                        "explanation": "Official emergency orders are released through gazette notifications and official press conferences, never via viral forwarding chains."
                    },
                    {
                        "question_id": 2,
                        "question": "Why do cyber fraudsters use typosquatting domains like 'www-sbi-banking.xyz'?",
                        "options": [
                            "Because .xyz domains are faster.",
                            "To deceive users into believing they are accessing the genuine banking portal.",
                            "To comply with international web standards.",
                            "Because authentic banks prefer 3-letter extensions."
                        ],
                        "correct_index": 1,
                        "explanation": "Typosquatting mimics legitimate brands to fool unsuspecting visitors into typing login credentials or OTPs on spoofed websites."
                    }
                ]),
            ),
            QuizModuleDB(
                id="manipulated-images-reverse-search",
                title="Manipulated Images & Reverse Image Search",
                category="Forensics & Fact-Checking",
                difficulty="Intermediate",
                summary="How to use Google Lens, TinEye, and EXIF metadata to discover the original date, location, and context of viral photos.",
                content="""# Image Verification & Reverse Search Techniques

One of the most widespread forms of misinformation is taking an authentic photograph from an old crisis and claiming it depicts an event from today.

### Step-by-Step Image Verification:
1. **Reverse Image Search**: Upload the image to Google Images, TinEye, or Yandex. Look for the earliest published date of the photo.
2. **Examine Weather and Foliage**: Check shadows, vehicle license plates, road signage, and clothing seasons.
3. **EXIF Metadata Inspection**: Digital cameras record timestamp, aperture, and GPS coordinates (unless stripped by social networks).
4. **Look for Cloning Artifacts**: Photoshops often duplicate crowds or smoke plumes using the clone stamp tool.
""",
                questions_json=json.dumps([
                    {
                        "question_id": 1,
                        "question": "What is the primary purpose of conducting a reverse image search on a viral photo?",
                        "options": [
                            "To increase the image resolution.",
                            "To trace the earliest appearance of the photo and verify its authentic date and location.",
                            "To delete the photo from the internet.",
                            "To convert the file format from PNG to JPG."
                        ],
                        "correct_index": 1,
                        "explanation": "Reverse image searching allows you to discover where and when a photo was originally published, exposing out-of-context reuse."
                    }
                ]),
            ),
        ]
        db.add_all(modules)
        db.commit()

    # ── 5. Seed Pre-analyzed Sample Reports for Live Stats & History ─────────
    if db.query(AnalysisDB).count() == 0:
        demo_reports = [
            AnalysisDB(
                id="demo-analysis-01",
                title="PIB Fact Check: PM Free Laptop Yojana 2026 Registration Link",
                input_type="text",
                input_content="Forwarded: All college students across India will receive free laptops from Ministry of Education under PM Free Laptop Yojana 2026. Register immediately on http://freelaptop-yojana.online before midnight.",
                extracted_domain="freelaptop-yojana.online",
                source_url="http://freelaptop-yojana.online",
                author="Anonymous Viral Forward",
                publish_date="2026-03-15",
                overall_credibility_score=12.0,
                verdict="Contradicted by evidence",
                confidence_score=95.0,
                claims_json=json.dumps([
                    {
                        "claim_id": 1,
                        "claim_text": "Government is giving free laptops to all college students under PM Free Laptop Yojana 2026.",
                        "verdict": "Contradicted by evidence",
                        "confidence": 98.0,
                        "explanation": "Debunked directly by PIB Fact Check Unit. No such official scheme exists.",
                        "supporting_sources_count": 0,
                        "contradicting_sources_count": 1,
                        "citations": [{"source": "PIB Fact Check", "url": "https://factcheck.pib.gov.in"}]
                    }
                ]),
                supporting_evidence_json="[]",
                contradicting_evidence_json=json.dumps([
                    {
                        "source_name": "PIB Fact Check",
                        "source_url": "https://factcheck.pib.gov.in/pm-free-laptop-scheme-hoax",
                        "domain": "factcheck.pib.gov.in",
                        "credibility_rating": 100.0,
                        "source_category": "Tier 1 - Sovereign & Official Record",
                        "is_ifcn_certified": True,
                        "stance": "contradicts",
                        "quote_or_summary": "PIB Fact Check confirmed no such scheme has been announced. The link is a malicious phishing attempt.",
                        "publish_date": "2026-03-15"
                    }
                ]),
                source_credibility_json=json.dumps({
                    "domain": "freelaptop-yojana.online",
                    "reputation_score": 5.0,
                    "is_trusted_publisher": False,
                    "is_official_government": False,
                    "is_ifcn_fact_checker": False,
                    "author_transparency": "Low / Anonymous",
                    "publisher_tier": "Unverified - High Risk of Misinformation",
                    "notes": ["Flagged phishing domain on national cyber awareness registers."]
                }),
                warnings_json=json.dumps([
                    {"category": "clickbait", "level": "alert", "message": "Urgency coercion: 'Register immediately before midnight'"},
                    {"category": "phishing", "level": "warning", "message": "Suspicious non-government TLD (.online) impersonating welfare program"}
                ]),
                ai_explanation_standard="This claim is completely contradicted by official government verification from the PIB Fact Check Unit.",
                ai_explanation_beginner="This is a scam designed to steal your information. The government is not giving away free laptops through this link. Do not open the link or share it.",
                is_saved=True,
                is_public=True,
                share_token="laptop-scam-demo",
            ),
            AnalysisDB(
                id="demo-analysis-02",
                title="ISRO Launches INSAT-3DS Satellite Aboard GSLV-F14",
                input_type="url",
                input_content="ISRO has successfully injected the INSAT-3DS meteorological satellite into designated orbit to enhance climate and weather forecasting.",
                extracted_domain="pib.gov.in",
                source_url="https://pib.gov.in/PressReleasePage.aspx?PRID=2006789",
                author="Ministry of Space / PIB",
                publish_date="2026-02-17",
                overall_credibility_score=98.0,
                verdict="Supported by evidence",
                confidence_score=96.0,
                claims_json=json.dumps([
                    {
                        "claim_id": 1,
                        "claim_text": "ISRO successfully launched INSAT-3DS satellite into orbit.",
                        "verdict": "Supported by evidence",
                        "confidence": 99.0,
                        "explanation": "Confirmed by ISRO and Press Information Bureau press bulletin.",
                        "supporting_sources_count": 2,
                        "contradicting_sources_count": 0,
                        "citations": [{"source": "PIB", "url": "https://pib.gov.in"}]
                    }
                ]),
                supporting_evidence_json=json.dumps([
                    {
                        "source_name": "Press Information Bureau (PIB)",
                        "source_url": "https://pib.gov.in/PressReleasePage.aspx?PRID=2006789",
                        "domain": "pib.gov.in",
                        "credibility_rating": 99.0,
                        "source_category": "Tier 1 - Sovereign & Official Record",
                        "is_ifcn_certified": True,
                        "stance": "supports",
                        "quote_or_summary": "ISRO confirmed the precise orbit injection of INSAT-3DS meteorological satellite from Sriharikota.",
                        "publish_date": "2026-02-17"
                    }
                ]),
                contradicting_evidence_json="[]",
                source_credibility_json=json.dumps({
                    "domain": "pib.gov.in",
                    "reputation_score": 99.0,
                    "is_trusted_publisher": True,
                    "is_official_government": True,
                    "is_ifcn_fact_checker": True,
                    "author_transparency": "High (Official Government Release)",
                    "publisher_tier": "Tier 1 - Sovereign & Official Record",
                    "notes": ["Verified official nodal agency."]
                }),
                warnings_json="[]",
                ai_explanation_standard="The report is fully substantiated by primary official space agency releases and government gazettes.",
                ai_explanation_beginner="This news is 100% true and verified. The Indian space agency confirmed that the satellite was successfully launched.",
                is_saved=True,
                is_public=True,
                share_token="isro-insat-demo",
            )
        ]
        db.add_all(demo_reports)
        db.commit()
