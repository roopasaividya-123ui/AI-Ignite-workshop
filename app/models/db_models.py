"""
app/models/db_models.py — SQLAlchemy database models for TruthGuard AI.
"""

from datetime import datetime
import json
import uuid
from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.database import Base


class UserDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(512), nullable=False)
    role = Column(String(50), default="user", nullable=False)  # user, analyst, admin
    awareness_score = Column(Integer, default=0, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    analyses = relationship("AnalysisDB", back_populates="user", cascade="all, delete-orphan")
    quiz_attempts = relationship("UserQuizAttemptDB", back_populates="user", cascade="all, delete-orphan")


class AnalysisDB(Base):
    __tablename__ = "analyses"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    
    title = Column(String(500), nullable=False)
    input_type = Column(String(50), nullable=False)  # url, text, document
    input_content = Column(Text, nullable=False)
    
    extracted_domain = Column(String(255), nullable=True)
    source_url = Column(String(1000), nullable=True)
    author = Column(String(255), nullable=True)
    publish_date = Column(String(100), nullable=True)
    
    # Verdict & Scores
    overall_credibility_score = Column(Float, nullable=False)  # 0.0 - 100.0
    verdict = Column(String(100), nullable=False)  
    # Verdicts: 'Supported by evidence', 'Likely accurate', 'Misleading', 'Contradicted by evidence', 'Unverified'
    confidence_score = Column(Float, default=85.0, nullable=False)
    
    # Detailed Evidence & Breakdown stored as JSON strings
    claims_json = Column(Text, default="[]", nullable=False)
    supporting_evidence_json = Column(Text, default="[]", nullable=False)
    contradicting_evidence_json = Column(Text, default="[]", nullable=False)
    source_credibility_json = Column(Text, default="{}", nullable=False)
    warnings_json = Column(Text, default="[]", nullable=False)
    
    # AI Explanations
    ai_explanation_standard = Column(Text, nullable=False)
    ai_explanation_beginner = Column(Text, nullable=False)
    
    # Sharing & Status
    is_saved = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    share_token = Column(String(64), unique=True, default=lambda: uuid.uuid4().hex[:16], index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("UserDB", back_populates="analyses")

    @property
    def claims(self):
        return json.loads(self.claims_json) if self.claims_json else []

    @property
    def supporting_evidence(self):
        return json.loads(self.supporting_evidence_json) if self.supporting_evidence_json else []

    @property
    def contradicting_evidence(self):
        return json.loads(self.contradicting_evidence_json) if self.contradicting_evidence_json else []

    @property
    def source_credibility(self):
        return json.loads(self.source_credibility_json) if self.source_credibility_json else {}

    @property
    def warnings(self):
        return json.loads(self.warnings_json) if self.warnings_json else []


class TrustedSourceDB(Base):
    __tablename__ = "trusted_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    category = Column(String(100), nullable=False)  # government, fact_checker, health_authority, news_agency
    credibility_rating = Column(Float, nullable=False)  # 0.0 - 100.0
    country = Column(String(100), default="Global", nullable=False)
    is_ifcn_certified = Column(Boolean, default=False, nullable=False)
    description = Column(Text, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class FactCheckRecordDB(Base):
    """Real, verified fact checks cataloged from PIB Fact Check, Alt News, BOOM, Factly, WHO, etc."""
    __tablename__ = "fact_check_records"

    id = Column(Integer, primary_key=True, index=True)
    claim_reviewed = Column(Text, nullable=False, index=True)
    verdict = Column(String(100), nullable=False)  # False, Misleading, True, Altered Media, Unproven
    publisher = Column(String(255), nullable=False)
    source_url = Column(String(1000), nullable=False)
    review_date = Column(String(100), nullable=False)
    explanation = Column(Text, nullable=False)
    keywords = Column(String(500), nullable=False)
    tags = Column(String(255), default="misinformation", nullable=False)


class QuizModuleDB(Base):
    __tablename__ = "quiz_modules"

    id = Column(String(64), primary_key=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(50), default="Beginner", nullable=False)
    summary = Column(Text, nullable=False)
    content = Column(Text, nullable=False)
    questions_json = Column(Text, nullable=False)  # JSON list of questions
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class UserQuizAttemptDB(Base):
    __tablename__ = "user_quiz_attempts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    module_id = Column(String(64), nullable=False)
    score = Column(Integer, nullable=False)
    max_score = Column(Integer, nullable=False)
    completed_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    user = relationship("UserDB", back_populates="quiz_attempts")
