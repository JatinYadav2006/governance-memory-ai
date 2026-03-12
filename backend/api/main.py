from __future__ import annotations

from fastapi import FastAPI
from pydantic import BaseModel, Field


# NOTE:
# This file intentionally contains only the minimal API skeleton.
# Future modules will be added as the project grows:
# - `backend/api/routes/` for versioned routers (e.g., /v1/issues, /v1/analytics)
# - `backend/models/` for domain models and schemas
# - `backend/logic/` for governance intelligence pipelines (analysis/prioritization)
# - `backend/database/` for persistence and governance memory storage layers


class IssueInput(BaseModel):
    """
    Placeholder schema for citizen-reported issues/complaints.

    This will be expanded later (e.g., category, location, priority signals,
    attachments, metadata, language, and consent fields).
    """

    text: str = Field(..., min_length=1, description="Citizen complaint text.")


app = FastAPI(title="Governance Memory AI API")


@app.get("/", tags=["meta"])
def root() -> dict[str, str]:
    return {"message": "Governance Memory AI API is running."}


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    return {"status": "healthy"}


# Entry-point note:
# Run locally with: `uvicorn backend.api.main:app --reload`
