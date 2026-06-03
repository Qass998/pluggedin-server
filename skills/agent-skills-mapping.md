# agent-skills → PluggedIN Mapping
# Which skills to use, when, and how

---

## Active Skills (4 installed)

### code-review-and-quality
**When:** After any implementation step. After DeepSeek generates code. Before merging or deploying.
**How:** Five-axis review (correctness, readability, architecture, security, performance).
Label findings: Critical, Important, Nit, Optional, FYI.
**PluggedIN context:** Gate between Claude (design) and DeepSeek (build). Claude reviews what DeepSeek produced.
**Key anti-rationalization:** "AI-generated code is probably fine" → AI code needs MORE scrutiny, not less.

### frontend-ui-engineering
**When:** Building dashboards, portals, or any HTML/CSS output. Use alongside pluggedin-design.
**How:** pluggedin-design handles visual quality (colors, spacing, animation). frontend-ui-engineering handles component architecture, accessibility, state management, loading states.
**PluggedIN context:** SEGGUINÉE dashboard, client portals, demo systems.
**Key rule:** Every component must handle: loading, empty, error, and edge cases.

### planning-and-task-breakdown
**When:** Any multi-step task before execution. Enhances existing Plan Mode.
**How:** Vertical slicing (one feature end-to-end before next). Task sizing: XS (<1h), S (1-3h), M (3-8h), L (1-2d). Never above L — split.
**PluggedIN context:** Replaces generic "plan it" with structured task breakdown.
**Key rule:** Task sizes above L are a red flag. Force splitting.

### security-and-hardening
**When:** Any code handling API keys, client data, auth, or external input.
**How:** OWASP Top 10 checks. Secrets scanning. Input validation. Auth verification.
**PluggedIN context:** Client portals with Airtable tokens. WhatsApp API keys. Production deployments.
**Key rule:** Secrets in .env only. Never in markdown. Never in git.

---

## Skills NOT Installed (and why)

| Skill | Why skipped |
|-------|-------------|
| test-driven-development | Overkill for static HTML dashboards. No backend test suite. |
| ci-cd-and-automation | We deploy static HTML to Vercel. No pipeline needed. |
| deprecation-and-migration | No APIs or SDK to version yet. |
| shipping-and-launch | Vercel deploy = one command. Overhead irrelevant. |
| documentation-and-adrs | ADRs are for engineering teams. We use memory/ files. |
| browser-testing-with-devtools | Manual browser testing is sufficient for dashboards. |
| api-and-interface-design | No backend APIs being built yet. |
| doubt-driven-development | Covered by code-review-and-quality. |

---

## The Anti-Rationalization Pattern

Every agent-skills file has a "Common Rationalizations" table.
This is the single biggest quality upgrade. Copy this pattern into all custom PluggedIN skills.

Format:
```
| Rationalization | Reality |
|-----------------|---------|
| "Excuse the agent makes" | Why it's wrong |
```

Example for our dashboard skill:
```
| "It looks fine on my screen" | Test at 375px, 768px, and 1440px. Government users have old monitors. |
| "Chart.js handles the data" | Charts fail silently on hidden canvases. We dropped Chart.js for this reason. |
```

---

## References (installed)

skills/agent-skills-references/
├── security-checklist.md
├── performance-checklist.md
├── testing-patterns.md
├── accessibility-checklist.md
└── orchestration-patterns.md

Reference these from any skill that needs them.
