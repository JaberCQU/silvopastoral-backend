# ============================================================
# CQ Silvopastoral Dashboard -- FastAPI Backend
# Phase 2: API + PostgreSQL + user accounts
# ============================================================
# Run locally:
#   uvicorn app.main:app --reload
# Then visit http://127.0.0.1:8000/docs for interactive API docs.
# ============================================================

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.database import Base, engine
from app.routers import auth, stations, scenarios, reference

settings = get_settings()

# Creates all tables defined in models.py if they don't already
# exist. Safe to run every startup -- it never drops or alters
# existing tables. For real schema changes later, switch to Alembic
# migrations instead of relying on this.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CQ Silvopastoral Dashboard API",
    description="Backend for the Central Queensland silvopastoral decision-support tool. "
                 "Provides user accounts, saved station/scenario storage, and species/region "
                 "reference data for the GitHub Pages frontend.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(stations.router)
app.include_router(scenarios.router)
app.include_router(reference.router)


@app.get("/", tags=["health"])
def health_check():
    """Simple endpoint to confirm the API is running -- useful for
    Render/Railway health checks and for a quick manual sanity check."""
    return {"status": "ok", "service": "cq-silvopastoral-api", "version": "2.0.0"}
