# PluggedInOS V1 — internal deal origination

## Frozen boundary

PluggedInOS is an internal deal-origination operating system. It is not a generic CRM, client SaaS, messaging product, GHL clone, or AI-automation agency platform. V1 starts from explicit commercial intent, finds the opposite side, independently verifies public evidence, scores the match, and surfaces only credible opportunities for human review.

## Runtime

```text
permitted sources -> Scout -> Signal + Need
                                  |
                         Matcher -> Offer + Match
                                  |
                         Verifier -> Evidence + unknowns
                                  |
                           Prime -> Deal brief
                                  |
                       human approval boundary
```

`deal_os/core.py` is a dependency-free orchestration core with narrow provider and repository protocols. Existing `market_intel`, `b2b_scanner`, Apify, and TinyFish code can become adapters after their network/cost/error behavior is normalized. They are not called by the acceptance test and retain no authority to contact anyone.

Postgres is the intended intelligence system of record. `deal_os/schema.sql` models tenant-scoped companies, people, sources, signals, needs, offers, relationships, evidence, verifications, matches, opportunities, conversations, deals, agent runs, and approvals. The Source Registry learns using verified-opportunity and completed-deal counts. Agents receive scoped tools, never raw SQL credentials.

## Experiment

The three desks are agri/food trade, industrial manufacturers/distributors, and construction/project supply. Each is capped at 100 explicit signals. The locked funnel is signal → real requirement → counterparty candidate → verification → response → both interested → introduction → commercial progression.

Initial intent patterns include RFQ, tender, seeking distributor, seeking supplier, seeking buyer/importer, sourcing request, and offtake/partner request. Expansion, project awards, disruptions, regulation, and hiring remain inferred-signal work for a later phase.

## Acceptance test

Run:

```bash
python -m unittest tests.test_deal_os -v
python -m deal_os
```

The deterministic case begins with a dated public UAE request for 10 MT of organic avocado to Dubai. No companies are supplied to Prime. Scout returns the explicit requirement; Matcher independently returns Keitt Exporters in Kenya; Verifier uses Keitt's export page and Kenya Trade Portal corroboration; Prime explains the possible value and states every unresolved item.

This is a genuine evidence fixture, not a claim of current availability. Buyer identity, requirement freshness, funds, current organic certification, 10 MT availability, quote, and recent shipments remain unverified.

## Locked and human-controlled surfaces

The score threshold and acceptance assertions are locked during a run. Contacting either party, changing evidence status, publishing, spending, merging, and deploying require human approval. The core creates a pending `contact_counterparties` approval and contains no sender. Smartlead or another channel may later be an approved adapter; GHL may consume selected records but never owns the intelligence graph.

## Production next slice

Implement the Postgres repository, authenticated internal endpoints, source queue with terms/robots compliance, content snapshots/hashes, idempotency, and one browser/search adapter per desk. Preserve rejected candidates in append-only run logs and measure source yield against the locked funnel.
