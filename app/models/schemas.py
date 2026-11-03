"""
app/models/schemas.py — Pydantic schemas for TruthGuard AI request/response validation.
"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field


# ── Auth Schemas ──────────────────────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=8)
    role: Optional[str] = "user"  # 'user', 'analyst', 'admin'
    admin_secret: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    role: str
    awareness_score: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ProfileUpdateRequest(BaseModel):
    full_name: Optional[str] = None


# ── News Analysis Schemas ────────────────────────────────────────────────────

class AnalyzeRequest(BaseModel):
    input_type: str = Field("text", description="One of: 'url', 'text', 'document'")
    content: Optional[str] = Field(None, description="Direct text, headline, or message")
    url: Optional[str] = Field(None, description="News article URL")
    document_text: Optional[str] = Field(None, description="Text extracted from uploaded document")
    title: Optional[str] = None


class ClaimItem(BaseModel):
    claim_id: int
    claim_text: str
    verdict: str  # Supported by evidence, Likely accurate, Misleading, Contradicted by evidence, Unverified
    confidence: float  # 0.0 - 100.0
    explanation: str
    supporting_sources_count: int
    contradicting_sources_count: int
    citations: List[Dict[str, Any]] = []


class EvidenceItem(BaseModel):
    source_name: str
    source_url: str
    domain: str
    credibility_rating: float
    source_category: str  # government, fact_checker, news_agency, health_authority
    is_ifcn_certified: bool
    stance: str  # supports, contradicts, neutral
    quote_or_summary: str
    publish_date: Optional[str] = None


class SourceCredibilityBreakdown(BaseModel):
    domain: Optional[str] = "Unknown"
    reputation_score: float = 50.0
    is_trusted_publisher: bool = False
    is_official_government: bool = False
    is_ifcn_fact_checker: bool = False
    author_transparency: str = "Moderate"
    publisher_tier: str = "Tier 3"
    notes: List[str] = []


class WarningItem(BaseModel):
    category: str  # clickbait, emotional_manipulation, unverified_sources, outdated, anonymous_author
    level: str  # warning, alert, info
    message: str


class CredibilityReportResponse(BaseModel):
    id: str
    title: str
    input_type: str
    input_content: str
    extracted_domain: Optional[str] = None
    source_url: Optional[str] = None
    author: Optional[str] = None
    publish_date: Optional[str] = None
    
    overall_credibility_score: float  # 0 - 100
    verdict: str  # Supported by evidence, Likely accurate, Misleading, Contradicted by evidence, Unverified
    confidence_score: float
    
    claims: List[ClaimItem] = []
    supporting_evidence: List[EvidenceItem] = []
    contradicting_evidence: List[EvidenceItem] = []
    source_credibility: SourceCredibilityBreakdown
    warnings: List[WarningItem] = []
    
    ai_explanation_standard: str
    ai_explanation_beginner: str
    
    is_saved: bool = False
    is_public: bool = True
    share_token: str
    created_at: datetime


# ── Trusted Sources Schemas ──────────────────────────────────────────────────

class TrustedSourceCreate(BaseModel):
    name: str
    domain: str
    category: str
    credibility_rating: float = Field(..., ge=0.0, le=100.0)
    country: str = "India"
    is_ifcn_certified: bool = False
    description: str


class TrustedSourceResponse(BaseModel):
    id: int
    name: str
    domain: str
    category: str
    credibility_rating: float
    country: str
    is_ifcn_certified: bool
    description: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Awareness & Quiz Schemas ─────────────────────────────────────────────────

class QuizQuestion(BaseModel):
    question_id: int
    question: str
    options: List[str]
    correct_index: int
    explanation: str


class QuizModuleResponse(BaseModel):
    id: str
    title: str
    category: str
    difficulty: str
    summary: str
    content: str
    questions: List[QuizQuestion]
    total_questions: int


class QuizSubmitRequest(BaseModel):
    answers: Dict[int, int]  # question_id -> selected_option_index


class QuizSubmitResponse(BaseModel):
    module_id: str
    score: int
    max_score: int
    percentage: float
    passed: bool
    feedback: List[Dict[str, Any]]
    new_user_awareness_score: int


# ── Dashboard & Admin Schemas ────────────────────────────────────────────────

class DashboardStatsResponse(BaseModel):
    total_analyses: int
    verified_claims: int
    misleading_claims: int
    unverified_claims: int
    contradicted_claims: int
    average_credibility_score: float
    total_trusted_sources: int
    accuracy_rate: float


class CredibilityDistributionItem(BaseModel):
    name: str
    count: int
    percentage: float
    color: str


class WeeklyActivityItem(BaseModel):
    day: str
    date: str
    analyses_count: int
    verified_count: int
    misleading_count: int


class AdminMetricsResponse(BaseModel):
    total_users: int
    total_analyses: int
    verified_percentage: float
    flagged_misinformation_count: int
    total_sources: int
    active_analyses_today: int
    cache_hit_rate: float
    avg_ai_latency_ms: int
