"""Postgres repository and communication ledger for the internal Deal OS."""

from __future__ import annotations

import json
import os
from contextlib import contextmanager
from dataclasses import asdict
from typing import Iterator
from uuid import UUID, uuid4

from .core import AgentRun, Match

COMMUNICATION_STATES = (
    "not_contacted", "contact_approved", "contacted", "replied",
    "requirement_confirmed", "counterparty_qualified", "one_side_interested",
    "both_interested", "introduction_approved", "introduced", "negotiating",
    "commercially_progressing", "won", "lost", "dormant", "disqualified",
)


class PostgresRepository:
    def __init__(self, database_url: str | None = None):
        self.database_url = database_url or os.environ.get("DATABASE_URL", "")
        if not self.database_url:
            raise RuntimeError("DATABASE_URL is required for Postgres persistence")

    @contextmanager
    def connection(self) -> Iterator:
        import psycopg
        with psycopg.connect(self.database_url) as connection:
            yield connection

    def ensure_tenant(self, tenant_id: str, name: str = "PluggedIN Internal") -> None:
        UUID(tenant_id)
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("INSERT INTO tenants (id, name) VALUES (%s, %s) ON CONFLICT (id) DO NOTHING", (tenant_id, name))

    def save_match(self, tenant_id: str, match: Match, run: AgentRun) -> None:
        with self.connection() as connection, connection.cursor() as cursor:
            signal, counterparty = match.signal, match.counterparty
            source_id, company_id, need_id, offer_id = (str(uuid4()) for _ in range(4))
            cursor.execute("INSERT INTO agent_runs (id, tenant_id, desk, objective, status, log, started_at) VALUES (%s,%s,%s,%s,'running','[]',%s) ON CONFLICT (id) DO NOTHING", (run.id, tenant_id, run.desk, run.objective, run.started_at))
            cursor.execute("INSERT INTO sources (id, tenant_id, url, name, source_type, last_checked_at) VALUES (%s,%s,%s,%s,'explicit_signal',now()) ON CONFLICT (tenant_id,url) DO UPDATE SET last_checked_at=now() RETURNING id", (source_id, tenant_id, signal.source_url, signal.evidence[0].publisher or signal.evidence[0].title))
            source_id = str(cursor.fetchone()[0])
            cursor.execute("INSERT INTO signals (id,tenant_id,source_id,desk,intent,headline,market,source_url,published_at,raw) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (signal.id, tenant_id, source_id, signal.desk, signal.intent, signal.headline, signal.market, signal.source_url, signal.published_at or None, json.dumps(asdict(signal))))
            cursor.execute("INSERT INTO needs (id,tenant_id,signal_id,product_category,specification) VALUES (%s,%s,%s,%s,%s)", (need_id, tenant_id, signal.id, signal.requirement.product, json.dumps(asdict(signal.requirement))))
            cursor.execute("INSERT INTO companies (id,tenant_id,name,website,region,metadata) VALUES (%s,%s,%s,%s,%s,%s)", (company_id, tenant_id, counterparty.company_name, counterparty.website, counterparty.market, json.dumps({"role": counterparty.role})))
            cursor.execute("INSERT INTO offers (id,tenant_id,company_id,product_category,regions,capability) VALUES (%s,%s,%s,%s,%s,%s)", (offer_id, tenant_id, company_id, signal.requirement.product, json.dumps([counterparty.market]), json.dumps({"capabilities": counterparty.capabilities})))
            for subject_type, subject_id, verification in (("signal", signal.id, match.signal_verification), ("company", company_id, match.counterparty_verification)):
                cursor.execute("INSERT INTO verifications (tenant_id,subject_type,subject_id,status,checks,unknowns) VALUES (%s,%s,%s,%s,%s,%s)", (tenant_id, subject_type, subject_id, verification.status, json.dumps([asdict(item) for item in verification.checks]), json.dumps(verification.unknowns)))
            for subject_type, subject_id, items in (("signal", signal.id, signal.evidence), ("company", company_id, counterparty.evidence)):
                for item in items:
                    cursor.execute("INSERT INTO evidence (tenant_id,subject_type,subject_id,url,claim,observed_at) VALUES (%s,%s,%s,%s,%s,%s)", (tenant_id, subject_type, subject_id, item.url, item.claim, item.observed_at))
            cursor.execute("INSERT INTO matches (id,tenant_id,signal_id,need_id,offer_id,score,rationale,brief) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)", (match.id, tenant_id, signal.id, need_id, offer_id, match.score, json.dumps(match.rationale), match.brief))
            cursor.execute("INSERT INTO opportunities (tenant_id,match_id,stage) VALUES (%s,%s,'human_review')", (tenant_id, match.id))

    def request_approval(self, tenant_id: str, match_id: str, action_type: str) -> None:
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT id FROM opportunities WHERE tenant_id=%s AND match_id=%s", (tenant_id, match_id))
            opportunity = cursor.fetchone()
            if not opportunity:
                raise LookupError("Opportunity not found for match")
            cursor.execute("INSERT INTO approval_actions (tenant_id,opportunity_id,action_type,status,payload) VALUES (%s,%s,%s,'pending',%s)", (tenant_id, opportunity[0], action_type, json.dumps({"match_id": match_id})))

    def list_opportunities(self, tenant_id: str, limit: int = 50) -> list[dict]:
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT o.id,o.stage,o.both_interested,o.commercial_progression,m.score,m.brief,m.created_at FROM opportunities o JOIN matches m ON m.id=o.match_id WHERE o.tenant_id=%s ORDER BY m.created_at DESC LIMIT %s", (tenant_id, min(limit, 200)))
            return [dict(zip(("id","stage","both_interested","commercial_progression","score","brief","created_at"), row)) for row in cursor.fetchall()]

    def add_communication(self, tenant_id: str, opportunity_id: str, item: dict) -> dict:
        if item["state"] not in COMMUNICATION_STATES:
            raise ValueError("Invalid communication state")
        communication_id = str(uuid4())
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("INSERT INTO conversations (id,tenant_id,opportunity_id,party_side,channel,direction,state,external_ref,subject,summary,occurred_at,next_action,follow_up_at,approval_id,metadata) SELECT %s,%s,id,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s FROM opportunities WHERE id=%s AND tenant_id=%s", (communication_id, tenant_id, item["party_side"], item["channel"], item["direction"], item["state"], item.get("external_ref"), item.get("subject"), item["summary"], item["occurred_at"], item.get("next_action"), item.get("follow_up_at"), item.get("approval_id"), json.dumps(item.get("metadata", {})), opportunity_id, tenant_id))
            if cursor.rowcount != 1:
                raise LookupError("Opportunity not found")
            cursor.execute("UPDATE opportunities SET stage=%s, both_interested=(%s='both_interested' OR both_interested) WHERE id=%s AND tenant_id=%s", (item["state"], item["state"], opportunity_id, tenant_id))
        return {"id": communication_id, **item}

    def list_communications(self, tenant_id: str, opportunity_id: str) -> list[dict]:
        columns = ("id", "party_side", "channel", "direction", "state", "external_ref", "subject", "summary", "occurred_at", "next_action", "follow_up_at", "approval_id", "metadata")
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT id,party_side,channel,direction,state,external_ref,subject,summary,occurred_at,next_action,follow_up_at,approval_id,metadata FROM conversations WHERE tenant_id=%s AND opportunity_id=%s ORDER BY occurred_at,id", (tenant_id, opportunity_id))
            return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def decide_approval(self, tenant_id: str, approval_id: str, decision: str, reviewer: str) -> dict:
        status = {"approve": "approved", "reject": "rejected"}.get(decision)
        if not status:
            raise ValueError("Decision must be approve or reject")
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("UPDATE approval_actions SET status=%s,reviewed_by=%s,reviewed_at=now() WHERE id=%s AND tenant_id=%s AND status='pending' RETURNING id,status,action_type", (status, reviewer, approval_id, tenant_id))
            row = cursor.fetchone()
            if not row:
                raise LookupError("Pending approval not found")
            return {"id": str(row[0]), "status": row[1], "action_type": row[2]}

    def funnel_metrics(self, tenant_id: str) -> dict:
        with self.connection() as connection, connection.cursor() as cursor:
            cursor.execute("SELECT stage,count(*) FROM opportunities WHERE tenant_id=%s GROUP BY stage", (tenant_id,))
            return {stage: count for stage, count in cursor.fetchall()}
