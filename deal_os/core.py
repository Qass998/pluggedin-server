"""Evidence-first orchestration for PluggedInOS deal origination.

Agents receive narrow provider/repository contracts. They never receive raw database
access and this module deliberately contains no email, WhatsApp, spend, or publishing
executor.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Literal, Protocol
from uuid import uuid4

Desk = Literal["agri_food", "industrial_distribution", "construction_supply"]
VerificationStatus = Literal["plausible", "verified", "rejected"]

DESKS = {
    "agri_food": {"label": "Agri / food trade", "explicit_signal_target": 100},
    "industrial_distribution": {"label": "Industrial manufacturers / distributors", "explicit_signal_target": 100},
    "construction_supply": {"label": "Construction / project supply", "explicit_signal_target": 100},
}


@dataclass(frozen=True)
class Evidence:
    url: str
    title: str
    claim: str
    observed_at: str
    publisher: str = ""


@dataclass(frozen=True)
class Requirement:
    product: str
    quantity: str = ""
    destination: str = ""
    terms: tuple[str, ...] = ()
    required_attributes: tuple[str, ...] = ()


@dataclass(frozen=True)
class Signal:
    id: str
    desk: Desk
    intent: Literal["demand", "supply", "partner"]
    headline: str
    market: str
    source_url: str
    requirement: Requirement
    evidence: tuple[Evidence, ...]
    company_name: str = ""
    published_at: str = ""


@dataclass(frozen=True)
class Counterparty:
    id: str
    company_name: str
    market: str
    website: str
    role: Literal["buyer", "supplier", "distributor"]
    capabilities: tuple[str, ...]
    evidence: tuple[Evidence, ...]


@dataclass(frozen=True)
class Check:
    name: str
    result: Literal["pass", "partial", "fail"]
    note: str
    evidence_url: str = ""


@dataclass(frozen=True)
class Verification:
    subject_id: str
    status: VerificationStatus
    checks: tuple[Check, ...]
    unknowns: tuple[str, ...]


@dataclass(frozen=True)
class Match:
    id: str
    signal: Signal
    counterparty: Counterparty
    score: int
    rationale: tuple[str, ...]
    signal_verification: Verification
    counterparty_verification: Verification
    brief: str
    stage: Literal["human_review"] = "human_review"


@dataclass(frozen=True)
class AgentRun:
    id: str
    tenant_id: str
    desk: Desk
    objective: str
    started_at: str
    agents: tuple[str, ...] = ("Scout", "Matcher", "Verifier", "Prime")


class SignalSource(Protocol):
    def find_explicit_signals(self, desk: Desk, limit: int) -> list[Signal]: ...


class CounterpartySource(Protocol):
    def find_opposite_side(self, signal: Signal, limit: int) -> list[Counterparty]: ...


class EvidenceVerifier(Protocol):
    def verify_signal(self, signal: Signal) -> Verification: ...
    def verify_counterparty(self, counterparty: Counterparty, signal: Signal) -> Verification: ...


class DealRepository(Protocol):
    def save_match(self, tenant_id: str, match: Match, run: AgentRun) -> None: ...
    def request_approval(self, tenant_id: str, match_id: str, action_type: str) -> None: ...


@dataclass
class InMemoryRepository:
    """Honest local adapter; production must use the Postgres schema."""

    matches: list[dict] = field(default_factory=list)
    approvals: list[dict] = field(default_factory=list)

    def save_match(self, tenant_id: str, match: Match, run: AgentRun) -> None:
        self.matches.append({"tenant_id": tenant_id, "run_id": run.id, **asdict(match)})

    def request_approval(self, tenant_id: str, match_id: str, action_type: str) -> None:
        self.approvals.append({
            "id": str(uuid4()), "tenant_id": tenant_id, "match_id": match_id,
            "action_type": action_type, "status": "pending",
            "note": "No outreach executor exists in the V1 core.",
        })


class Prime:
    def __init__(self, source: SignalSource, matcher: CounterpartySource, verifier: EvidenceVerifier, repository: DealRepository):
        self.source, self.matcher, self.verifier, self.repository = source, matcher, verifier, repository

    def run(self, tenant_id: str, desk: Desk, signal_limit: int = 10, candidates_per_signal: int = 3) -> dict:
        if desk not in DESKS:
            raise ValueError(f"Unknown deal desk: {desk}")
        run = AgentRun(str(uuid4()), tenant_id, desk, "Explicit intent -> opposite side -> independent verification -> human review", _now())
        results: list[Match] = []
        for signal in self.source.find_explicit_signals(desk, min(max(signal_limit, 1), 100)):
            for candidate in self.matcher.find_opposite_side(signal, min(max(candidates_per_signal, 1), 20)):
                signal_check = self.verifier.verify_signal(signal)
                candidate_check = self.verifier.verify_counterparty(candidate, signal)
                if "rejected" in (signal_check.status, candidate_check.status):
                    continue
                score = _score(signal, candidate, signal_check, candidate_check)
                if score < 60:
                    continue
                rationale = _rationale(signal, candidate)
                unknowns = signal_check.unknowns + candidate_check.unknowns
                brief = (
                    f"{signal.headline}. {candidate.company_name} is a plausible {candidate.role} in {candidate.market}. "
                    f"{' '.join(rationale)} Still unverified: {'; '.join(unknowns)}. "
                    "Recommendation: human review before either party is contacted."
                )
                match = Match(str(uuid4()), signal, candidate, score, rationale, signal_check, candidate_check, brief)
                self.repository.save_match(tenant_id, match, run)
                self.repository.request_approval(tenant_id, match.id, "contact_counterparties")
                results.append(match)
        return {"run": asdict(run), "results": [asdict(item) for item in results]}


def _score(signal: Signal, candidate: Counterparty, *verifications: Verification) -> int:
    score = 35 + (10 if signal.requirement.quantity else 0) + (10 if signal.requirement.destination else 0)
    if any(signal.requirement.product.lower() in capability.lower() for capability in candidate.capabilities):
        score += 20
    score += 5 * sum(check.result == "pass" for verification in verifications for check in verification.checks)
    return min(score, 100)


def _rationale(signal: Signal, candidate: Counterparty) -> tuple[str, ...]:
    fit = any(signal.requirement.product.lower() in capability.lower() for capability in candidate.capabilities)
    return (
        f"Product fit: published capability {'includes' if fit else 'does not yet confirm'} {signal.requirement.product}.",
        f"Cross-market value: {candidate.market} supply could serve {signal.market} demand.",
    )


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class AcceptanceFixtureProvider:
    """Dated public evidence, frozen for a repeatable no-credentials acceptance run."""

    observed_at = "2026-08-24T00:00:00+00:00"

    def find_explicit_signals(self, desk: Desk, limit: int) -> list[Signal]:
        return ([BUYER_SIGNAL] if desk == "agri_food" else [])[:limit]

    def find_opposite_side(self, signal: Signal, limit: int) -> list[Counterparty]:
        return ([SUPPLIER_CANDIDATE] if signal.requirement.product.lower() == "avocado" else [])[:limit]

    def verify_signal(self, signal: Signal) -> Verification:
        return Verification(signal.id, "plausible", (
            Check("explicit requirement", "pass", "Listing specifies product, quantity, destination and delivery terms.", signal.source_url),
            Check("buyer identity", "partial", "Marketplace reports account checks, but the public preview masks the legal buyer identity.", signal.source_url),
        ), ("legal buyer identity", "requirement still open", "proof of funds"))

    def verify_counterparty(self, counterparty: Counterparty, signal: Signal) -> Verification:
        return Verification(counterparty.id, "plausible", (
            Check("published capability", "pass", "Company publishes avocado export capability and organic categories.", counterparty.evidence[0].url),
            Check("independent company record", "pass", "Kenya Trade Portal corroborates the agribusiness and website.", counterparty.evidence[1].url),
            Check("specific shipment readiness", "partial", "Current documents and availability are not established by public pages.", counterparty.website),
        ), ("current organic certificate", "10 MT availability", "CIF/CPT Dubai quote", "recent shipment references"))


BUYER_SIGNAL = Signal(
    "signal-freshdi-2026-05-25-avocado-uae", "agri_food", "demand",
    "UAE wholesale buyer requests 10 MT organic avocado", "Dubai, UAE",
    "https://freshdi.com/request/Avocado-LjC1Qh",
    Requirement("Avocado", "10 MT", "Dubai, UAE", ("CIF", "CPT", "T/T"), ("organic", "unripe", "export quality")),
    (Evidence("https://freshdi.com/request/Avocado-LjC1Qh", "Buyer Looking For Avocado", "Public request states 10 MT, Dubai destination, CIF/CPT and organic fruit.", AcceptanceFixtureProvider.observed_at, "Freshdi"),),
    published_at="2026-05-25",
)

SUPPLIER_CANDIDATE = Counterparty(
    "company-keitt-exporters-kenya", "Keitt Exporters Limited", "Kenya", "https://keitt.co.ke/", "supplier",
    ("Avocado", "fresh produce export", "packaging and logistics"),
    (
        Evidence("https://keitt.co.ke/fruit-export/", "Fruit Export", "Company publishes Kenyan avocado exports, including organic categories.", AcceptanceFixtureProvider.observed_at, "Keitt Group"),
        Evidence("https://www.kenyatradeportal.go.ke/content/keitt-exporters-ltd", "Keitt Exporters Ltd", "Government trade portal lists the agribusiness and matching website.", AcceptanceFixtureProvider.observed_at, "Kenya Trade Portal"),
    ),
)


def run_acceptance_test() -> dict:
    provider, repository = AcceptanceFixtureProvider(), InMemoryRepository()
    result = Prime(provider, provider, provider, repository).run("pluggedin-internal", "agri_food", 1, 1)
    return {**result, "approvals": repository.approvals}
