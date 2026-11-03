"""
tests/test_truthguard.py — Comprehensive test suite for TruthGuard AI platform.
"""

import pytest


class TestHealthAndAuth:
    def test_health_check(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        assert resp.json()["status"] == "healthy"

    def test_user_registration(self, client):
        payload = {
            "email": "testuser@truthguard.ai",
            "full_name": "Test Citizen",
            "password": "Password@123",
            "role": "user",
        }
        resp = client.post("/api/auth/register", json=payload)
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "testuser@truthguard.ai"

    def test_user_login_success(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "admin@truthguard.ai",
            "password": "Admin@123456",
        })
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_user_login_invalid_credentials(self, client):
        resp = client.post("/api/auth/login", json={
            "email": "admin@truthguard.ai",
            "password": "WrongPassword999",
        })
        assert resp.status_code == 401

    def test_demo_login(self, client):
        resp = client.post("/api/auth/demo-login/analyst")
        assert resp.status_code == 200
        assert resp.json()["user"]["role"] == "analyst"


class TestAINewsAnalyzer:
    def test_analyze_debunked_phishing_claim(self, client):
        # A claim matching pre-seeded PIB fact check record
        payload = {
            "input_type": "text",
            "title": "PM Free Laptop Yojana",
            "content": "All students get free laptops from government under PM Free Laptop Yojana 2026. Register on http://freelaptop-yojana.online immediately!",
        }
        resp = client.post("/api/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] == "Contradicted by evidence"
        assert data["overall_credibility_score"] < 40.0
        assert len(data["contradicting_evidence"]) >= 1
        assert "PIB Fact Check" in [e["source_name"] for e in data["contradicting_evidence"]]
        assert len(data["claims"]) >= 1
        assert "beginner" in data["ai_explanation_beginner"].lower() or len(data["ai_explanation_beginner"]) > 10

    def test_analyze_verified_news_claim(self, client):
        # A claim matching pre-seeded verified ISRO announcement
        payload = {
            "input_type": "text",
            "title": "ISRO Satellite Launch",
            "content": "ISRO successfully launches next-generation meteorological satellite INSAT-3DS aboard GSLV-F14 from Sriharikota.",
        }
        resp = client.post("/api/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["verdict"] in ["Supported by evidence", "Likely accurate"]
        assert data["overall_credibility_score"] >= 65.0
        assert len(data["supporting_evidence"]) >= 1

    def test_abstention_on_unverified_claim(self, client):
        # Completely unknown claim with no matching evidence
        payload = {
            "input_type": "text",
            "title": "Random obscure local statement",
            "content": "A small purple bicycle was discovered behind the old library gate yesterday evening.",
        }
        resp = client.post("/api/analyze", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        # Per design guidelines: System must abstain and return Unverified rather than guess
        assert data["verdict"] == "Unverified"
        assert len(data["supporting_evidence"]) == 0
        assert len(data["contradicting_evidence"]) == 0

    def test_demo_examples_list(self, client):
        resp = client.get("/api/analyze/demo-examples")
        assert resp.status_code == 200
        examples = resp.json()
        assert len(examples) >= 3


class TestSourceVerification:
    def test_list_trusted_sources(self, client):
        resp = client.get("/api/sources")
        assert resp.status_code == 200
        sources = resp.json()
        assert len(sources) >= 5
        domains = [s["domain"] for s in sources]
        assert "factcheck.pib.gov.in" in domains
        assert "altnews.in" in domains
        assert "who.int" in domains

    def test_verify_gov_domain(self, client):
        resp = client.get("/api/sources/verify-domain?domain=isro.gov.in")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_official_government"] is True
        assert data["reputation_score"] >= 95.0

    def test_verify_suspicious_domain(self, client):
        resp = client.get("/api/sources/verify-domain?domain=free-recharge-now.xyz")
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_trusted_publisher"] is False
        assert data["reputation_score"] <= 30.0


class TestAwarenessCenter:
    def test_get_awareness_modules(self, client):
        resp = client.get("/api/awareness/modules")
        assert resp.status_code == 200
        modules = resp.json()
        assert len(modules) >= 3
        assert any(m["id"] == "deepfakes-synthetic-media" for m in modules)

    def test_submit_quiz_answers(self, client, user_headers):
        # Submit correct answers for anatomy-of-fake-news module (q1: 1, q2: 0)
        resp = client.post(
            "/api/awareness/modules/anatomy-of-fake-news/submit",
            headers=user_headers,
            json={"answers": {1: 1, 2: 0}},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["passed"] is True
        assert data["score"] == 2
        assert data["percentage"] == 100.0


class TestDashboardAndReports:
    def test_dashboard_stats(self, client):
        resp = client.get("/api/dashboard/stats")
        assert resp.status_code == 200
        data = resp.json()
        assert data["total_analyses"] >= 2
        assert data["total_trusted_sources"] >= 5

    def test_reports_history_and_share(self, client):
        resp = client.get("/api/reports")
        assert resp.status_code == 200
        reports = resp.json()
        assert len(reports) >= 2
        
        # Test share link
        share_token = reports[0]["share_token"]
        share_resp = client.get(f"/api/reports/share/{share_token}")
        assert share_resp.status_code == 200
        assert share_resp.json()["id"] == reports[0]["id"]


class TestAdminRBAC:
    def test_admin_metrics_forbidden_for_regular_user(self, client, user_headers):
        resp = client.get("/api/admin/metrics", headers=user_headers)
        assert resp.status_code == 403

    def test_admin_metrics_allowed_for_admin(self, client, admin_headers):
        resp = client.get("/api/admin/metrics", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "active_analyses_today" in data
