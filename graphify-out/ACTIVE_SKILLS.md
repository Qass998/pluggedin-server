# ACTIVE SKILLS INDEX
# Auto-loaded every session. Maps every task type → skill to read first.
# 29 skills across 7 categories. Updated: 2026-06-04

---

## HOW TO USE THIS FILE
Before writing any code or plan, scan the TRIGGER column.
If the task matches a trigger → read that SKILL.md before doing anything.
Skills marked ⚡ are MANDATORY for that task type — no exceptions.

---

## VISUAL & UI (13 skills)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `pluggedin-design` | any UI, dashboard, portal, HTML, CSS, design, layout, component, typography, redesign | Premium visual output — font bans, color tokens, spacing, quality gate | ⚡ ALWAYS FIRST |
| `dashboard` | build dashboard, demo dashboard, KPI tracker, client demo | Standalone HTML dashboard with Airtable data | After pluggedin-design |
| `client-portal` | client portal, SME portal, business portal, operator portal | Full agentic portal with industry templates | After pluggedin-design |
| `redesign-skill` | redesign, upgrade UI, fix UI, looks AI, looks cheap, generic | Audit + premium redesign | After pluggedin-design |
| `antigravity-design-expert` | glassmorphism, spatial UI, floating cards, 3D CSS, GSAP motion, immersive | Spatial weightless UI with GSAP + 3D CSS | After pluggedin-design |
| `baseline-ui` | UI audit, anti-slop, check UI, accessibility, Tailwind review | Violations list + concrete fixes | Quality gate |
| `soft-skill` | high-end agency, luxury UI, Awwwards, expensive feel, premium CSS | Premium font/shadow/card/animation system | After pluggedin-design |
| `huashu-design` | hi-fi prototype, HTML demo, interactive mockup, app prototype, iOS mockup | High-fidelity HTML prototypes with interactions | Standalone |
| `ui-ux-pro-max` | brand identity, logo, banner, icon design, social media image | Brand assets — logos, banners, icons, social images | Standalone |
| `ui-styling` | shadcn, radix UI, tailwind components, dark mode, accessible components | Production UI with shadcn/Tailwind/accessibility | Standalone |
| `canvas-design` | data visualisation, charts, visual design philosophy | Data viz + visual design files | Standalone |
| `open-design` | inline SVG charts, pure HTML dashboard, no Chart.js | HTML/CSS dashboard with inline SVG charts | After pluggedin-design |
| `taste-skill` | override AI defaults, metric-based UI, enforce design rules | Anti-default UI enforcement | Quality gate |

---

## ENGINEERING (8 skills)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `senior-fullstack` | architecture decision, system design, tech stack, scalability | Senior architecture + implementation plan | First for complex builds |
| `react-nextjs-development` | React component, Next.js, App Router, Server/Client Component, TypeScript | Production React/Next.js code | After nextjs-best-practices |
| `nextjs-best-practices` | Next.js, App Router, Server Components, data fetching, static page, ISR | Correct patterns — avoids Server/Client mistakes | ⚡ Every Next.js task |
| `full-stack-orchestration` | full feature build, end-to-end feature, frontend + backend together | Coordinated full-stack feature delivery | After senior-fullstack |
| `frontend-ui-engineering` | production UI, component build, layout, state management | Production-quality frontend | After pluggedin-design |
| `app-builder` | build app, new project, MVP, prototype, from scratch | Full-stack app from natural language | First for new apps |
| `css-animations` | CSS keyframes, animation-delay, fill-mode, CSS-only motion | CSS animation patterns | Standalone |
| `gsap` | GSAP, gsap.to, gsap.timeline, ScrollTrigger, stagger | GSAP animation code | Standalone |

---

## QUALITY (4 skills)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `code-review-and-quality` | code review, review this, quality check, before merge, assess code | Five-axis review: correctness, readability, architecture, security, performance | ⚡ Before every deploy |
| `security-and-hardening` | auth, user input, session, SQL injection, XSS, API keys, security | Vulnerability assessment + hardened code | ⚡ Any auth/input task |
| `planning-and-task-breakdown` | plan this, break down, estimate scope, too large, parallel work | Ordered task list with estimates | ⚡ Any multi-step task |
| `output-skill` | full output, no truncation, complete code, generate everything | Enforces complete unabridged output | When output gets cut |

---

## DEPLOYMENT (1 skill)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `vercel-deployment` | deploy, vercel, production, env vars, edge function, serverless, CORS, timeout | Correct Vercel config + deployment patterns | ⚡ Before every deploy |

---

## DATA (1 skill)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `airtable-automation` | airtable, create record, list records, filter formula, schema, batch | Airtable patterns — pagination, formulas, batch limits (10 max) | Every Airtable operation |

---

## INTELLIGENCE (1 skill)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `graphify` | map codebase, knowledge graph, what connects, dependency map, understand repo | Persistent knowledge graph + HTML viz | On new codebases |

---

## LEAD GENERATION & SCRAPING (5 consolidated + 1 signal, v2.0)

**Consolidated June 2026:** Removed 7 → 5 unified (apify-ultimate-scraper merged, cold-email+email-sequence unified, sales-automator replaced)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `lead-discovery` | find leads, bulk prospecting, LinkedIn scraping, Google Maps, Instagram | Bulk leads from 55+ Apify actors (LinkedIn, Maps, Instagram, TikTok, Google) | ⚡ Primary discovery |
| `lead-enrichment` | enrich leads, decision maker, contact info, activity signals, accuracy | Name, email, phone, LinkedIn, decision-maker scoring, signals (posts/comments/intent), accuracy score. Multi-source: ScrapeGraphAI + Vibe MCP + Apify LinkedIn + Signal Detection | ⚡ For decision makers |
| `lead-qualification` | score leads, ICP fit, prospect quality | Leads with fit scores (hot/warm/cold) + reasoning. Enhanced: Vibe Prospecting MCP | After discovery + enrichment |
| `outreach-engine` | write outreach, cold email, sequences, LinkedIn messages, WhatsApp | Multi-channel sequences (email, LinkedIn, WhatsApp), personalization, templates, follow-ups | ⚡ For campaigns |
| `sales-pipeline` | sales automation, booking, deal tracking, nurture sequences | Cal.com booking, Airtable pipeline tracking, automated nurture, stage progression | Conversion layer |
| `linkedin-presence` | LinkedIn posting, content, profile optimization | LinkedIn posts via Rube MCP, profile updates, content calendar | Secondary (presence only) |
| `signal-detection` | buying signals, intent detection, hiring, funding, news | Buyers showing active signals (job posts, funding, tech changes, engagement) | Triggers outreach |

---

## OUTREACH (1 skill)

| Skill | Triggers | Produces | Priority |
|-------|----------|----------|----------|
| `open-outreach` | outreach pipeline, email sequence, LinkedIn, cold outreach | Outreach pipeline patterns | Outreach tasks |

---

## MANDATORY CHAINS (load these together)

| Task | Chain |
|------|-------|
| Build any UI | `pluggedin-design` → domain skill |
| Build Next.js feature | `nextjs-best-practices` → `react-nextjs-development` |
| Deploy to Vercel | `code-review-and-quality` → `vercel-deployment` |
| New full-stack feature | `planning-and-task-breakdown` → `senior-fullstack` → `full-stack-orchestration` |
| Any auth/security feature | `security-and-hardening` → `code-review-and-quality` |
| Client portal build | `pluggedin-design` → `client-portal` → `vercel-deployment` |
| Airtable integration | `airtable-automation` → `nextjs-best-practices` |

---

## SKILLS GRAPH
Machine-readable: `graphify-out/skills_graph.json`
29 nodes · 14 dependency edges
