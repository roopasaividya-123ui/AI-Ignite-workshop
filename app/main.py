"""
app/main.py — TruthGuard AI application entry point, routing, and SPA mounting.
"""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.config import settings
from app.database import create_db_tables
from app.api.auth_router import router as auth_router
from app.api.analyze_router import router as analyze_router
from app.api.reports_router import router as reports_router
from app.api.dashboard_router import router as dashboard_router
from app.api.sources_router import router as sources_router
from app.api.awareness_router import router as awareness_router
from app.api.admin_router import router as admin_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initializes database tables and foundational data seeds
    create_db_tables()
    yield


app = FastAPI(
    title="TruthGuard AI API",
    description="Advanced Fake News Detection, Source Verification & Media Awareness Platform",
    version=settings.app_version,
    lifespan=lifespan,
)

# ── CORS ──────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Include Routers ───────────────────────────────────────────────────────────
app.include_router(auth_router)
app.include_router(analyze_router)
app.include_router(reports_router)
app.include_router(dashboard_router)
app.include_router(sources_router)
app.include_router(awareness_router)
app.include_router(admin_router)

# ── Static Files & Single Page Application ────────────────────────────────────
os.makedirs("app/static", exist_ok=True)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def serve_index():
    index_path = os.path.join("app", "static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {
        "app": "TruthGuard AI",
        "status": "online",
        "docs": "/docs",
    }


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": "TruthGuard AI",
        "version": settings.app_version,
    }
