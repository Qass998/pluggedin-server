"""Authenticated internal API for PluggedInOS deal origination."""

from __future__ import annotations

import hmac
import os
from datetime import datetime
from typing import Literal

from fastapi import Depends, FastAPI, Header, HTTPException, Query
from pydantic import BaseModel, Field

from deal_os.core import AcceptanceFixtureProvider, DESKS, Prime
from deal_os.repository import COMMUNICATION_STATES, PostgresRepository

app = FastAPI(title="PluggedInOS Deal API", version="1.0.0")


class RunRequest(BaseModel):
    desk: Literal["agri_food", "industrial_distribution", "construction_supply"]
    signal_limit: int = Field(default=1, ge=1, le=100)
    candidates_per_signal: int = Field(default=1, ge=1, le=20)


class CommunicationRequest(BaseModel):
    party_side: Literal["buyer", "supplier", "internal"]
    channel: Literal["email", "linkedin", "phone", "meeting", "manual_note"]
    direction: Literal["inbound", "outbound", "internal"]
    state: str
    summary: str = Field(min_length=1, max_length=4000)
    occurred_at: datetime
    subject: str | None = Field(default=None, max_length=500)
    external_ref: str | None = Field(default=None, max_length=1000)
    next_action: str | None = Field(default=None, max_length=1000)
    follow_up_at: datetime | None = None
    approval_id: str | None = None
    metadata: dict = Field(default_factory=dict)


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]
    reviewer: str = Field(min_length=1, max_length=200)


def identity(
    authorization: str = Header(default=""),
    tenant_id: str = Header(alias="X-PluggedIn-Tenant", default=""),
) -> str:
    configured = os.environ.get("PLUGGEDIN_INTERNAL_API_KEY", "")
    if not configured:
        raise HTTPException(503, "Internal API key is not configured")
    supplied = authorization.removeprefix("Bearer ")
    if not hmac.compare_digest(configured, supplied):
        raise HTTPException(401, "Invalid internal API credentials")
    if not tenant_id:
        raise HTTPException(400, "X-PluggedIn-Tenant is required")
    return tenant_id


def repository() -> PostgresRepository:
    return PostgresRepository()


@app.get("/health")
def health():
    return {"status": "ok", "service": "pluggedin-deal-api"}


@app.get("/api/v1/desks")
def list_desks(_: str = Depends(identity)):
    return {"desks": DESKS, "explicit_signal_target": 300}


@app.post("/api/v1/acceptance-runs", status_code=201)
def acceptance_run(body: RunRequest, tenant_id: str = Depends(identity), repo: PostgresRepository = Depends(repository)):
    if os.environ.get("ALLOW_ACCEPTANCE_FIXTURES", "false").lower() != "true":
        raise HTTPException(403, "Acceptance fixtures are disabled")
    repo.ensure_tenant(tenant_id)
    provider = AcceptanceFixtureProvider()
    return Prime(provider, provider, provider, repo).run(tenant_id, body.desk, body.signal_limit, body.candidates_per_signal)


@app.get("/api/v1/opportunities")
def opportunities(limit: int = Query(default=50, ge=1, le=200), tenant_id: str = Depends(identity), repo: PostgresRepository = Depends(repository)):
    return {"opportunities": repo.list_opportunities(tenant_id, limit)}


@app.post("/api/v1/opportunities/{opportunity_id}/communications", status_code=201)
def add_communication(opportunity_id: str, body: CommunicationRequest, tenant_id: str = Depends(identity), repo: PostgresRepository = Depends(repository)):
    if body.state not in COMMUNICATION_STATES:
        raise HTTPException(422, f"state must be one of: {', '.join(COMMUNICATION_STATES)}")
    try:
        return repo.add_communication(tenant_id, opportunity_id, body.model_dump(mode="json"))
    except LookupError as error:
        raise HTTPException(404, str(error)) from error


@app.get("/api/v1/opportunities/{opportunity_id}/communications")
def communication_timeline(opportunity_id: str, tenant_id: str = Depends(identity), repo: PostgresRepository = Depends(repository)):
    return {"communications": repo.list_communications(tenant_id, opportunity_id)}


@app.patch("/api/v1/approvals/{approval_id}")
def decide_approval(approval_id: str, body: ApprovalDecision, tenant_id: str = Depends(identity), repo: PostgresRepository = Depends(repository)):
    try:
        return repo.decide_approval(tenant_id, approval_id, body.decision, body.reviewer)
    except LookupError as error:
        raise HTTPException(404, str(error)) from error


@app.get("/api/v1/metrics/funnel")
def funnel(tenant_id: str = Depends(identity), repo: PostgresRepository = Depends(repository)):
    return {"funnel": repo.funnel_metrics(tenant_id)}
