# PluggedIN Skills Registry
# THE SINGLE SOURCE OF TRUTH — read before every plan
# Every task type → its skill chain. Plan phase scans this file automatically.

---

## How it works

When Qassim describes a task, the plan phase:
1. Scans this registry for matching task types
2. Loads the listed SKILL.md files in order
3. Builds the plan using those skills
4. Presents: STEPS, SKILLS USED, FILES AFFECTED, RISKS

---

## AGENT ARCHITECTURE & CONTEXT ENGINEERING

> Skills from muratcankoylan/Agent-Skills-for-Context-Engineering — installed 2026-06-02.
> Load these whenever designing agents, memory systems, or multi-agent pipelines.

| Task | Skills to Load (in order) |
|------|---------------------------|
| Design agent memory / cross-session state | memory-systems |
| Build multi-agent pipeline (orchestrator/CEO/sub-agents) | multi-agent-patterns |
| Long session compaction / context window management | context-compression |
| Design autonomous agent harness / cron / approval loops | harness-engineering |
| Use files as agent context (today.md, pipeline.md) | filesystem-context |
| Any agent build involving memory + multi-agent + files | memory-systems → multi-agent-patterns → filesystem-context |
| Full autonomous agent system | memory-systems → multi-agent-patterns → filesystem-context → harness-engineering → context-compression |

---

## VISUAL & UI

> **All visual chains now start with `pluggedin-design` (v4.0 unified authority — 17 source skills absorbed).**
> Domain skills (dashboard, client-portal) add their specific logic after the unified base.
> The old multi-skill chains are dead. No more `taste-skill`, `frontend-ui-engineering`, `huashu-design`, `soft-skill`, `gsap`, `css-animations` as separate loads — they're all absorbed into `pluggedin-design`.

| Task | Skills to Load (in order) |
|------|---------------------------|
| Build dashboard / demo | pluggedin-design → dashboard |
| Build client portal | pluggedin-design → client-portal |
| Improve existing UI | pluggedin-design → redesign-skill |
| Redesign existing dashboard | pluggedin-design → redesign-skill → dashboard |
| Premium/soft UI (calm, luxury) | pluggedin-design (use MODE=soft_structural) |
| Add animations | pluggedin-design (use MOTION_INTENSITY dial, §8-§10) |
| Design system work | pluggedin-design (§14 Token Presets for quick start) |
| Accessibility audit | pluggedin-design (§7 Accessibility — WCAG 2.1 AA enforced) |
| Full output enforcement (no truncation) | pluggedin-design (§13 Full Output Protocol enforced automatically) |
| Anti-slop audit | pluggedin-design (§12 Quality Gate — 7-category checklist) |

## LEAD GENERATION & SCRAPING (Consolidated v2.0)

> **Restructured June 2026:** 7 scattered skills → 5 unified + consolidated chains.
> Removed overlaps: apify-ultimate-scraper (merged), web-scraper→lead-enrichment,
> cold-email+email-sequence→outreach-engine, sales-automator→sales-pipeline.
> linkedin-automation→linkedin-presence (posting only, clear scope).

| Task | Skills to Load (in order) |
|------|---------------------------|
| **DISCOVERY** | |
| Find bulk leads (LinkedIn, Maps, Instagram, etc) | lead-discovery |
| Find leads for a client | lead-discovery → lead-qualification |
| **ENRICHMENT** | |
| Enrich leads: name, phone, email, decision-maker, signals | lead-enrichment |
| Deep website scraping (AI-powered) | lead-enrichment (ScrapeGraphAI layer) |
| Detect buying signals / intent | signal-detection |
| **QUALIFICATION** | |
| Score lead fit to ICP | lead-qualification |
| **OUTREACH** | |
| Write cold email + sequences (email, LinkedIn, WhatsApp) | outreach-engine |
| Full outbound campaign (discovery → enrichment → outreach) | lead-discovery → lead-enrichment → lead-qualification → outreach-engine |
| **CONVERSION** | |
| Sales pipeline automation (booking, deal tracking, nurture) | sales-pipeline |
| **PRESENCE** | |
| LinkedIn posting + profile optimization | linkedin-presence |

---

## CLIENT ONBOARDING & RESEARCH

| Task | Skills to Load (in order) |
|------|---------------------------|
| New client intake | interview-me → spec-driven-development |
| Define ICP / buyer profile | icp-identification |
| Prospect research / enrichment | company-contact-finder → icp-website-audit |
| Lead qualification | lead-qualification → icp-website-audit |
| Find leads for a client | apollo-lead-finder OR vibe-prospecting → lead-qualification |
| Build TAM / market size | tam-builder |
| Competitor research | competitor-intel → competitive-pricing-intel |
| Competitor ads / marketing | competitor-ad-intelligence → ad-angle-miner → trending-ad-hook-spotter |
| Industry scan | industry-scanner → signal-scanner |

## OUTREACH & PIPELINE

| Task | Skills to Load (in order) |
|------|---------------------------|
| Draft outreach email | email-drafting → pain-language-engagers |
| Full outreach campaign | cold-email-outreach → linkedin-outreach |
| LinkedIn message only | linkedin-message-writer |
| Full outbound engine | outbound-prospecting-engine |
| Pipeline review | pipeline-review → lead-qualification |
| Sales call prep | sales-call-prep → meeting-brief |
| Sales coaching | sales-coaching → pipeline-review |

## SIGNALS & MONITORING

| Task | Skills to Load (in order) |
|------|---------------------------|
| Detect buying signals | signal-scanner → signal-detection-pipeline |
| Job posting / hiring signal | job-posting-intent → hiring-signal-outreach |
| Funding signal | funding-signal-monitor → funding-signal-outreach |
| News signal | news-signal-outreach |
| Event prospecting | event-prospecting-pipeline → luma-event-attendees |
| Champion tracking | champion-tracker → champion-move-outreach |
| Review monitoring | review-intelligence-digest |

## CONTENT & SEO

| Task | Skills to Load (in order) |
|------|---------------------------|
| Create content assets | content-asset-creator |
| Content strategy / briefs | content-brief-factory |
| SEO audit | seo-content-audit → seo-opportunity-finder |
| Domain SEO analysis | seo-domain-analyzer → seo-traffic-analyzer |
| Programmatic SEO | programmatic-seo-planner → programmatic-seo-spy |
| Campaign brief | campaign-brief-generator |

## ADS & CAMPAIGNS

| Task | Skills to Load (in order) |
|------|---------------------------|
| Meta ads campaign | meta-ads-campaign-builder → messaging-ab-tester |
| Google ads | google-search-ads-builder |
| Ad analysis | ad-campaign-analyzer → ad-to-landing-page-auditor |
| Launch positioning | launch-positioning-builder |

## BRAND & CREATIVE

| Task | Skills to Load (in order) |
|------|---------------------------|
| Brand voice extraction | brand-voice-extractor |
| Visual brand extraction | visual-brand-extractor |
| Battlecards | battlecard-generator |
| HTML carousel | create-html-carousel |
| Presentation / slides | create-html-slides |

## CODE QUALITY (agent-skills)

| Task | Skills to Load (in order) |
|------|---------------------------|
| Code review | code-review-and-quality → security-and-hardening |
| Simplify code | code-simplification |
| Plan complex task | planning-and-task-breakdown |
| Debug / fix bug | debugging-and-error-recovery |
| Performance optimization | performance-optimization |
| Security audit | security-and-hardening |
| UI component build | frontend-ui-engineering |
| Git / versioning | git-workflow-and-versioning |

## PLUGGEDIN INTERNAL

| Task | Skills to Load (in order) |
|------|---------------------------|
| Morning briefing | morning |
| Revenue audit | revenue |
| Update memory / log | (no skill — internal protocol) |
| Graph codebase | graphify |
| Skill discovery (find new skills) | skills |
| Log a mistake | mistake |
| Deploy to Vercel | vercel-deployment |
| Airtable records / schema | airtable-automation |
| Next.js App Router | nextjs-best-practices → react-nextjs-development |
| UI slop prevention / audit | baseline-ui |
| Spatial / glassmorphism UI | antigravity-design-expert |
| Full-stack feature build | full-stack-orchestration-full-stack-feature → senior-fullstack |
| Rapid app prototype | app-builder |
| Data visualisation | canvas-design |

---

## PROMPTING TECHNIQUE PER TASK TYPE

| Complexity | Technique Stack | Task Examples |
|-----------|----------------|---------------|
| **Simple** | Zero-shot | Read files, log to memory, single lookup |
| **Medium** | CoT + Few-shot | Build dashboard, draft outreach, plan feature, client research |
| **Complex** | CoT + Few-shot + Role | Multi-screen portal, full outreach campaign, competitor analysis |
| **Critical** | CoT + Few-shot + Role + Self-Consistency + Adversarial | Deploy to production, send outreach, financial report, security audit |

**Technique definitions** (from DAIR.AI Prompt Engineering Guide):
- **Zero-shot:** Direct instruction, no examples needed
- **CoT (Chain-of-Thought):** "Think through this step by step" before acting
- **Few-shot:** Provide 1-3 examples of target output in the skill file
- **Role:** Activate domain expert persona before executing
- **Self-Consistency:** Generate 2-3 reasoning paths, use majority result
- **Adversarial:** "What would break this? What would an adversary find wrong?"
- **Generated Knowledge:** "Before answering, list 3 key facts about this domain"

**Loading rule:** The plan phase auto-selects technique stack based on task complexity.
Simple tasks don't need CoT overhead. Critical tasks need the full stack.

---

## LOADING RULES

1. **Before any plan:** scan this registry for matching task types
2. **Multiple matches:** load all relevant chains, deduplicate, present in logical order
3. **No match found:** flag it — "No existing skill chain for this. Recommend: [best guess]."
4. **Custom skills override Goose skills** when both apply (e.g., pluggedin-design over frontend-ui-engineering alone)
5. **References auto-include:** if a skill references a checklist (security-checklist.md, accessibility-checklist.md), include it
6. **Skill files are in:**
   - `skills/` — PluggedIN custom skills + agent-skills
   - `~/.claude/skills/` — Goose GTM skills
   - `skills/agent-skills-references/` — Checklists and references
