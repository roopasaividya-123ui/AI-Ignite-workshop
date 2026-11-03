# TruthGuard AI – Advanced Fake News Detection & Awareness Platform

> **"Think Before You Believe. Verify Before You Share."**

TruthGuard AI is a production-grade, AI-powered misinformation detection, claim verification, and digital media awareness platform. It helps citizens, journalists, and researchers evaluate the credibility of online news articles, viral WhatsApp/Telegram messages, headlines, and uploaded documents against authoritative registries, sovereign government gazettes, and certified fact-checking archives.

---

## 🛡️ Core Philosophy: Strict Evidence Verification & Abstention

1. **Non-Hallucination Guarantee**: TruthGuard AI never declares information real or fake without supporting or contradicting factual evidence.
2. **Abstention Doctrine**: When external evidence is unavailable or insufficient, TruthGuard explicitly returns **"Unverified / Insufficient Evidence"** rather than hallucinating or guessing a verdict.
3. **Assessment Indicator**: The 0–100 credibility score is an **evidence-based assessment indicator**, not a mathematically proven probability that an article is true.

---

## 🚀 Key Platform Features

### 1. Multi-Input AI News Analyzer
- **News Article URL**: Automatically scrapes article content, publication date, author byline, and domain reputation.
- **Text & Headlines**: Direct submission of headlines, social media posts, or viral forwarded messages (WhatsApp, Telegram, X). Automatically cleans viral forward headers.
- **Document Upload**: Supports `.txt`, `.md`, `.json`, `.csv` documents for offline document fact-checking.
- **1-Click Demo Scenarios**: Pre-configured test cases (Phishing Scheme Hoax, Verified ISRO Launch, Misleading Health Cure, Unverified Rumor) for instant demonstration.

### 2. 8-Step Verification Pipeline
```
[1] Content & Metadata Extraction
       ↓
[2] Atomic Claim Decomposition (NLP)
       ↓
[3] Search Query Generation
       ↓
[4] Authoritative Registry Retrieval (PIB, WHO, Alt News, BOOM, Factly)
       ↓
[5] Evidence Ranking (Supporting vs Contradicting)
       ↓
[6] Multi-Factor Credibility Scoring with Abstention Logic
       ↓
[7] Dual-Mode AI Explanation Synthesis (Technical & Beginner Mode)
       ↓
[8] Structured Credibility Report Generation
```

### 3. Comprehensive Credibility Reports
- **Dynamic Circular Score Gauge (0–100)**: Visual color-coded gauge (Green for Verified, Amber for Misleading, Red for Contradicted, Slate for Unverified).
- **Claim-by-Claim Breakdown**: Isolates individual testable assertions and pairs each with supporting/contradicting citation links.
- **Dual-Mode AI Reasoning**:
  - **Standard Analysis**: Structured, rigorous breakdown for analysts and journalists.
  - **"Explain Like I'm a Beginner"**: Plain, accessible English for everyday citizens, explaining what was claimed, what facts prove, and why not to forward hoaxes.
- **Behavioral & Content Flags**: Clickbait detection, emotional manipulation warnings, urgent forward coercion flags, and uncredited author alerts.
- **Public Report Sharing**: Unique secure public share links (`/#/report/:shareToken`) with 1-click clipboard copying.
- **Print / PDF Export**: Formatted printable styling for compliance reports and investigations.

### 4. Authoritative Source Registry
- Prioritizes sovereign government websites (`.gov.in`, `.nic.in`), Press Information Bureau (PIB Fact Check), World Health Organization (WHO), UNICEF, United Nations, and IFCN-certified Indian fact-checkers:
  - **PIB Fact Check Unit** (Govt of India)
  - **Alt News** (IFCN Certified)
  - **BOOM Live** (IFCN Certified)
  - **Factly** (IFCN Certified)
  - **Reuters & Associated Press Fact Check**
- **Instant Domain Scanner**: Live inspection of any web domain to verify government authenticity, publisher reputation, and IFCN credentials.

### 5. Misinformation Awareness Center
- 4 In-depth digital literacy modules:
  1. *Anatomy of Fake News: The 7 Forms of Information Disorder*
  2. *Deepfakes & AI Synthetic Media Detection*
  3. *Verifying Viral WhatsApp & Social Media Forwards*
  4. *Manipulated Images & Reverse Image Search Techniques*
- **Interactive Quizzes**: Multiple-choice assessments with immediate feedback and pedagogical explanations for every answer.
- **Digital Media Awareness Score**: Dedicated literacy metric (0–100 pts) tracked in the user's profile, distinct from news credibility scores.

### 6. Main Operations Dashboard
- Live database-backed metrics: Total analyses, Verified claims, Misleading claims, Contradicted claims.
- Interactive SVG Donut chart displaying verdict distribution.
- 7-Day verification volume timeline chart.
- Recent analyses quick-inspect table.

### 7. Role-Based Access Control (RBAC) & Governance Panel
- Protected admin endpoints enforcing `require_admin`.
- User management table with active/suspend account toggles.
- Trusted source management with Create and Delete operations.
- Real-time system monitoring (cache hit rates, DB health, index counts).

---

## 🛠️ Technology Stack

| Component | Technology |
|---|---|
| **Backend Framework** | Python 3.13 + FastAPI (Asynchronous REST API) |
| **Database & ORM** | SQLite / PostgreSQL compatible + SQLAlchemy 2.0 |
| **Authentication** | PBKDF2-HMAC-SHA256 (600,000 iterations) + HS256 JWT (Standard Library) |
| **NLP & Claim Extraction** | Custom Rule-Based NLP + Token Set Cosine Matching + Jaccard Scoring |
| **Web Scraping & Normalization** | BeautifulSoup4 + Requests + Urllib |
| **Frontend UI/UX** | Responsive SPA, Tailwind CSS, SVG Interactive Charts, Glassmorphism |
| **Testing** | Pytest + FastAPI TestClient (StaticPool in-memory isolation) |

---

## ⚡ Quickstart Guide

### 1. Activate Environment & Run Development Server
```bash
# Ensure dependencies are installed in virtual environment
source .venv/bin/activate

# Launch the FastAPI application
uvicorn app.main:app --reload --port 8000
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

### 2. Run Test Suite
```bash
.venv/bin/pytest tests/
```
All 18 unit and integration tests run in under 7 seconds with 100% pass rate.

### 3. Interactive API Documentation (Swagger / OpenAPI)
Visit `http://127.0.0.1:8000/docs` to test endpoints via Swagger UI.

---

## 🔑 Pre-Seeded Demonstration Accounts

For convenient evaluation, the platform includes pre-seeded accounts accessible via the **1-Click Demo Buttons** in the UI:

| Role | Email | Password | Permissions |
|---|---|---|---|
| **Administrator** | `admin@truthguard.ai` | `Admin@123456` | Full governance, source registry CRUD, user moderation |
| **Fact-Check Analyst**| `analyst@truthguard.ai` | `Analyst@123456`| Verification inspection, evidence review |
| **Citizen / User** | `citizen@truthguard.ai` | `User@123456` | Analysis history, bookmarking, awareness quizzes |

---

## 📁 Repository Structure
```
├── app/
│   ├── api/                      # FastAPI Routers
│   │   ├── admin_router.py       # RBAC admin metrics and source management
│   │   ├── analyze_router.py     # 8-step verification pipeline & demo scenarios
│   │   ├── auth_router.py        # Authentication, profile & demo sign-in
│   │   ├── awareness_router.py   # Educational modules & interactive quizzes
│   │   ├── dashboard_router.py   # DB-backed analytics & chart endpoints
│   │   ├── reports_router.py     # Analysis history, bookmarking, and sharing
│   │   └── sources_router.py     # Trusted source registry & domain inspector
│   ├── models/
│   │   ├── db_models.py          # SQLAlchemy ORM models
│   │   └── schemas.py            # Pydantic validation schemas
│   ├── services/
│   │   ├── ai_explainer.py       # Dual-mode explanation generator (Standard & Beginner)
│   │   ├── claim_extractor.py    # Atomic factual claim extraction & query builder
│   │   ├── credibility_scorer.py # Multi-factor scoring & abstention logic
│   │   ├── extractor.py          # URL scraping, document parser & text sanitizer
│   │   ├── fact_checking_engine.py # Evidence retrieval & semantic matching
│   │   ├── seed_data.py          # Initial verified fact checks, modules & accounts
│   │   └── source_verifier.py    # Domain reputation evaluator (.gov.in, IFCN)
│   ├── static/                   # Production-grade Single Page Application (SPA)
│   │   ├── app.js                # Frontend client controller
│   │   ├── index.html            # Main HTML interface & modals
│   │   └── style.css             # Glassmorphism, glow effects & custom themes
│   ├── auth.py                   # PBKDF2 password hashing & HS256 JWT tokens
│   ├── config.py                 # Central configuration
│   ├── database.py               # Engine, SessionLocal, and DB table creation
│   └── main.py                   # FastAPI application initialization & route mounting
├── data/
│   └── truthguard.db             # SQLite database file
├── tests/
│   ├── conftest.py               # Pytest in-memory database fixtures (StaticPool)
│   └── test_truthguard.py        # 18 comprehensive automated tests
├── .env                          # Local environment variables
└── README.md                     # Documentation manual
```

---

## 📜 Ethical Commitment

TruthGuard AI is built on transparency and neutrality. All source citations are accompanied by direct reference links to primary sources. The platform does not take political stances and operates solely on documented records from verified institutions.
