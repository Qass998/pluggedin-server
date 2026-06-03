---
name: pluggedin-design
description: "PluggedIN UNIFIED DESIGN AUTHORITY. 17 source skills absorbed into 14 sections with zero overlap. The single file that governs all visual output — typography, color, layout, motion, components, accessibility, mode overrides, quality gate, and token presets. Read this ONCE before any HTML/CSS/dashboard/portal/landing page."
version: 4.0
date: 2026-05-22
sources_absorbed:
  - huashu-design (3,100+ lines, 5-dim critique, Junior Designer mode, anti-slop blacklist)
  - taste-skill (design dials, Rules 1-6, AI tells, motion-engine bento, pre-flight check)
  - frontend-ui-engineering (component architecture, accessibility, semantic tokens)
  - redesign-skill (3-step audit, fix priority, 9-dimension scan)
  - dashboard (8 Design Philosophies, module templates, quality checklist)
  - client-portal (portal generation, advisory engine, CEO agent, dark design system)
  - output-skill (full output enforcement, banned placeholder patterns)
  - accessibility-checklist (WCAG 2.1 AA quick reference)
  - minimalist-skill (premium utilitarian minimalism, warm monochrome, editorial typography)
  - soft-skill (high-end visual design, double-bezel, fluid island, magnetic physics)
  - brutalist-skill (industrial brutalism, Swiss + CRT, 90° corners, scanlines)
  - gpt-tasteskill (Python RNG variance, AIDA, gapless bento, GSAP scroll)
  - image-to-code-skill (image-first, anti-nested-box, hero minimalism, section rhythm)
  - stitch-skill + DESIGN.md (DESIGN.md format, token values, anti-patterns)
  - design-brief (8-dimension I-Lang, closed vocabulary, symbolic-to-concrete)
  - css-animations (keyframe patterns, stagger, HyperFrames contract)
  - gsap (timelines, position parameter, matchMedia, performance)
  - PencilPlaybook (7 presets, perceptual defaults, 9 scaffold archetypes)
  - open-design (dashboard builder, inline SVG charts, data-od-id convention)
---

# PluggedIN Unified Design Authority
**Version:** 4.0 | **Date:** 2026-05-22
**Status:** SINGLE SOURCE OF TRUTH — all visual output reads this file.

---

## WHAT THIS IS

One file. Fourteen sections. Seventeen source skills absorbed. Zero overlap.

Every design rule, perceptual default, component pattern, anti-slop directive, accessibility requirement, motion principle, and quality gate that PluggedIN enforces is in this file. Claude reads this ONCE before any visual output. No more loading 5+ skills and deduplicating conflicting rules on the fly.

---

## HOW TO USE

Before producing ANY HTML, CSS, dashboard, portal, landing page, or visual component:

1. **Read §12 (Quality Gate)** — the must-pass checklist
2. **Read §1-§5** — token schema, direction, typography, color, layout (the foundation)
3. **Read the sections matching your output type:**
   - Dashboard/portal → §6 (Information Design), §7 (Components), §8 (States)
   - Marketing/landing → §5 (Layout), §7 (Components), §9 (Motion)
   - Existing UI redesign → §2 (Direction), §12 (Quality Gate), §5 (Layout)
4. **Apply §11 (Mode Overrides)** if the project calls for a specific aesthetic
5. **Run §12 Quality Gate** before delivering ANY output

---

## §1 — DESIGN.md TOKEN SCHEMA

Every project MUST resolve these 9 sections before any pixel is placed. This is the portable design token file — the single source of truth that every agent, tool, and skill reads.

### 1.1 The 9-Section Convention

```markdown
# Design System: [Project Name]

## 1. Visual Theme & Atmosphere
- Mood: [professional_minimal | playful | brutalist | editorial]
- Density: [compact | balanced | spacious] (1-10 scale)
- Variance: [predictable | offset | artsy] (1-10 scale)
- Motion: [static | fluid | cinematic] (1-10 scale)
- Feel: [one evocative sentence]

## 2. Color Palette & Roles
- Background: #XXXXXX — [role]
- Surface: #XXXXXX — [role]
- Text Primary: #XXXXXX — [role]
- Text Secondary: #XXXXXX — [role]
- Text Muted: #XXXXXX — [role]
- Accent: #XXXXXX — [role]
- Accent Hover: #XXXXXX — [role]
- Border: #XXXXXX — [role]
- Success: #16A34A | Warning: #D97706 | Error: #DC2626

## 3. Typography Rules
- Display: [font], [weight], [scale], [tracking], [leading]
- Body: [font], [weight], [size]/[leading], [max-width]
- Mono: [font], [weight], [size]
- Banned fonts: [list]

## 4. Component Stylings
(Buttons, cards, inputs, modals, tables, loaders, empty states — each with shape, color, interaction behavior)

## 5. Layout Principles
- Max width: [px]
- Grid system: [single_column | two_column | asymmetric | bento]
- Section spacing: [px]
- Content padding: [px per breakpoint]

## 6. Depth & Elevation
- Shadows: [none | subtle | hard] (specific values)
- Borders: [width + color]
- Border radius: [default | cards | buttons | modals]

## 7. Do's and Don'ts
(Explicit anti-patterns for this project)

## 8. Responsive Behavior
- Breakpoints: 375 | 768 | 1024 | 1440
- Mobile rules, touch targets, typography scaling

## 9. Agent Prompt Guide
(Instructions for AI agents generating screens from this system)
```

### 1.2 Closed Vocabulary for Color Palettes

Only these palette values have concrete token mappings. Do not invent colors outside these:

| Symbolic | Background | Surface | Text | Secondary |
|----------|-----------|---------|------|-----------|
| `navy_and_white` | #0F172A | #1E293B | #F8FAFC | #94A3B8 |
| `monochrome_dark` | #09090B | #18181B | #FAFAFA | #A1A1AA |
| `light_clean` | #FFFFFF | #F8FAFC | #0F172A | #64748B |
| `earth_tones` | #FFFBEB | #FEF3C7 | #451A03 | #92400E |
| `warm_minimal` | #F7F6F3 | #FFFFFF | #111111 | #787774 |

### 1.3 Closed Vocabulary for Accents

| Accent | Hex | Hover |
|--------|-----|-------|
| `coral` | #F97316 | #EA580C |
| `electric_blue` | #3B82F6 | #2563EB |
| `emerald` | #10B981 | #059669 |
| `muted_sage` | #84A98C | #6B8F73 |
| `slate` | #64748B | #475569 |
| `rose` | #F43F5E | #E11D48 |
| `amber` | #F59E0B | #D97706 |
| `deep_navy` | #1E3A5F | #15294A |

### 1.4 Accent Rules (Non-Negotiable)

- Maximum **1 accent color** per project
- Accent saturation must stay **below 80%**
- Accent appears **maximum 3 times per viewport** (design-brief rule)
- Purple/blue neon gradients are **BANNED** — this is the "AI Purple" aesthetic and it is a hard failure
- Accent is for CTAs, focus rings, active states, and selected items ONLY — never for decorative backgrounds

---

## §2 — DESIGN DIRECTION SYSTEM

Before any visual decision, resolve the design direction. This prevents the "averaged internet aesthetic" that raw Claude defaults to.

### 2.1 The Five Schools

Pick ONE per project. Do not hybridize mid-project.

| # | School | Character | Best For |
|---|--------|-----------|----------|
| 1 | **Swiss Rational** | Grid-obsessed, monochrome, typography-first, invisible borders, Helvetica/Neue Haas Grotesk | Dashboards, data-heavy, enterprise |
| 2 | **Editorial Luxury** | Serif display, generous whitespace, warm off-white, film grain, massive type contrast | Portfolios, lifestyle, legal, real estate |
| 3 | **Soft Structural** | Diffused shadows, generous radius, muted pastels, airy spacing, spring physics | SaaS, health, consumer apps |
| 4 | **Industrial Brutalist** | 90° corners, visible grid lines, monospace data, CRT scanlines, black/red/white | Terminal apps, data-heavy dashboards, declassified blueprint aesthetic |
| 5 | **Neutral Baseline** | System fonts, grayscale, minimal opinion. Safe fallback. | Internal tools, quick prototypes, when the user brings their own system |

### 2.2 Junior Designer Mode (huashu-design core protocol)

Claude must operate as a "Junior Designer" under these constraints:

1. **Placeholder > bad implementation.** If you can't execute something well, use a deliberate placeholder with a clear label of what should go there. Never ship slop to fill space.
2. **System priority, don't fill.** Leave intentional negative space rather than adding elements just because space exists.
3. **One thousand no's for every yes.** Remove 10 elements for every 1 you add. The best designs are defined by what was rejected.
4. **Never the first idea.** The first layout AI generates is the statistical average of the internet. Reject it. Generate a second, deliberately different approach.
5. **text-wrap: pretty + CSS Grid as taste tax.** These two CSS decisions alone eliminate 40% of AI-looking output.

### 2.3 Design Direction Resolution (when user provides vague briefs)

When the user says "make it look professional" or "clean it up," resolve to concrete dimensions using this cascade:

1. **Infer industry** → map to appropriate school
2. **Infer density need** → data-heavy = Swiss/Industrial, marketing = Editorial/Soft
3. **Infer user sophistication** → technical users tolerate higher density and monospace
4. **Default fallback** → Neutral Baseline (School 5) with `professional_minimal` mood and `balanced` density

Never ask the user "what style do you want?" — they hired us to decide. If truly ambiguous, use the Neutral Baseline and note which dimensions were defaulted.

---

## §3 — TYPOGRAPHY

### 3.1 The Font Bans (Absolute, Non-Negotiable)

These fonts are banned across ALL PluggedIN output. They are the #1 AI-slop tell.

| Font | Why Banned | Exception |
|------|-----------|-----------|
| **Inter** | The single biggest AI-output fingerprint. Overused by every LLM. | Client portals where Inter is explicitly the brand font |
| **Roboto** | Google's default. Screams "I didn't choose a font." | Material Design 3 preset only |
| **Open Sans** | The old default. Same problem as Roboto. | Never |
| **Arial** | Browser fallback. Signals "I gave up on typography." | Never — use system-ui as fallback instead |
| **Helvetica** | Overplayed in AI design. Use Neue Haas Grotesk instead. | Only if explicitly requested |
| **Times New Roman, Georgia, Garamond, Palatino** | Generic serif defaults. BANNED in dashboards/software UIs. | Editorial mode only — and even then, use distinctive modern serifs |

### 3.2 Approved Font Stacks

**Display / Headings (pick one per project):**
- Geist, Satoshi, Cabinet Grotesk, Outfit, Plus Jakarta Sans, DM Sans, Space Grotesk, Clash Display, Neue Haas Grotesk, Archivo Black, Monument Extended

**Body (same family as display, weight 400):**
- Match display family. If display is Geist → body is Geist at 400 weight.

**Mono (for code, data, metadata, timestamps):**
- JetBrains Mono, Geist Mono, SF Mono, IBM Plex Mono, Space Mono

**Serif (editorial mode only — banned in dashboards):**
- Fraunces, Instrument Serif, Editorial New, Lyon Text, Newsreader, Playfair Display, Gambarino

### 3.3 Typographic Scale

| Level | Size | Weight | Tracking | Leading | Usage |
|-------|------|--------|----------|---------|-------|
| Display XL | clamp(3rem, 6vw, 5.5rem) | 700-900 | -0.03em | 0.95-1.1 | Hero headlines |
| Display | clamp(2rem, 5vw, 3.75rem) | 700 | -0.025em | 1.1 | Page titles |
| H1 | clamp(1.5rem, 3vw, 2.25rem) | 600-700 | -0.02em | 1.2 | Section headings |
| H2 | 1.25-1.5rem | 600 | -0.015em | 1.3 | Card titles |
| H3 | 1-1.125rem | 500-600 | 0 | 1.4 | Subheadings |
| Body | 1rem/16px | 400 | 0 | 1.5-1.65 | Main text |
| Body Small | 0.875rem/14px | 400 | 0 | 1.5 | Secondary text |
| Caption | 0.75-0.8125rem | 400-500 | 0.01em | 1.4 | Metadata, timestamps |
| Mono Data | 0.75-0.875rem | 400-500 | 0.02em | 1.3 | Numbers in tables, KPIs |
| Overline | 0.625-0.75rem | 600-700 | 0.05-0.1em | 1 | UPPERCASE labels, card headers |

### 3.4 Perceptual Typography Rules (PencilPlaybook + synthesis)

| Rule | Value | Source |
|------|-------|--------|
| Body text max width | 65 characters per line | Multiple sources converge here |
| Display letter-spacing at 56px+ | −0.03em (optical counters open up) | PencilPlaybook |
| Small text (10-12px) letter-spacing | +0.015em (prevents crowding) | PencilPlaybook |
| Body text on dark backgrounds | NEVER pure white (#FFFFFF). Use #E2E8F0 or #F1F5F9 — halation makes pure white harder to read | PencilPlaybook |
| Heading line limit | 2-3 lines MAX. 4+ lines is catastrophic failure | gpt-tasteskill |
| Hero headline | Ideally 1 line, maximum 3. Reduce words rather than forcing more lines | image-to-code |
| High-density override | When VISUAL_DENSITY > 7, ALL numbers must use monospace | stitch-skill |
| Body text minimum size | 1rem/16px (14px absolute floor on mobile) | WCAG + multiple |

### 3.5 Anti-Patterns

- NEVER use all-caps for body text or sentences (overlines and labels only)
- NEVER use generic gradient text on headlines
- NEVER allow 4+ line hero headlines — widen the container or reduce words
- NEVER use more than 2 typeface families (display/body + mono). Serif is a display face, not a third family.
- NEVER use `font-weight: 300` on dark backgrounds — thin strokes disappear

---

## §4 — COLOR CALIBRATION

### 4.1 The Absolute Bans

| Pattern | Reason |
|---------|--------|
| Pure black `#000000` | Causes halation on OLED, flattens depth. Use `#09090B`, `#0A0A0A`, or `#111111`. |
| Purple/blue neon gradients | The #1 AI aesthetic fingerprint. Banned everywhere. |
| Oversaturated accents (>80% saturation) | Screams "cheap SaaS template." Mute by 10-20%. |
| Mixed warm/cool grays in one project | Pick Zinc (cool) OR Slate (warm-neutral) — never mix. |
| Default Tailwind grays without customization | `gray-500` is not a design decision. |
| Neon outer glows on buttons | `box-shadow` with accent at >50% opacity. |

### 4.2 Palette Construction Rules

1. **Start from canvas, not accent.** Choose background first → surface → text → then accent.
2. **Text on dark backgrounds:** Primary `#E2E8F0` or `#F1F5F9`, not `#FFFFFF`. Secondary `#94A3B8`. Halation is real — white text on dark is harder to read than slightly-warm off-white.
3. **Borders:** Derived from text color at 6-8% opacity. `rgba(text, 0.06)` for light, `rgba(text, 0.08)` for dark.
4. **Surface layering:** Background → Surface → Card → Card Hover. Each layer is 2-4 lightness points apart. Enough to perceive, not enough to distract.
5. **Semantic colors:** Use the calibrated set — `#16A34A` (success), `#D97706` (warning), `#DC2626` (error), `#3B82F6` (info). Never invent semantic colors.

### 4.3 Perceptual Color Rules

| Rule | Value | Source |
|------|-------|--------|
| Disabled element opacity | 40% (not 50% — 50% creates visual competition with active elements) | PencilPlaybook (MD3 + Workday convergence) |
| Hover state lightness delta | Minimum 8% — below this, the state is imperceptible | PencilPlaybook |
| Focus ring offset | 2px from element edge | PencilPlaybook |
| Accent saturation ceiling | 80% max | stitch-skill + taste-skill |
| Color-only state indicators | BANNED — always pair color with icon or text | frontend-ui-engineering + WCAG |

### 4.4 Dark Mode Rules (Client Portal Baseline + Midnight preset)

```css
--bg:        #07090f;   /* Page background — deepest */
--surface:   #0c1018;   /* Sidebar + topbar */
--card:      #111622;   /* Card faces */
--card2:     #161d2b;   /* Card hover / footer */
--card3:     #1b2335;   /* Input backgrounds */
--border:    #1e2d42;   /* Subtle structural */
--border2:   #26384f;   /* Visible structural */
--text:      #e2eaf6;   /* Primary — NOT pure white */
--text2:     #8899b4;   /* Secondary */
--muted:     #3d4f68;   /* Tertiary / disabled */
```

Dark mode key principle: text is never pure white, surfaces have 3 distinct depth layers, borders are visible enough to separate regions without being decorative.

---

## §5 — LAYOUT ARCHITECTURE

### 5.1 Grid Systems

| Grid | CSS | Best For |
|------|-----|----------|
| Single Column | `max-width: [contentMax]; margin: auto` | Marketing pages, editorial |
| Two Column (sidebar) | `grid-template-columns: [sidebar] 1fr` | Dashboards, portals, apps |
| Asymmetric Bento | `grid-template-columns: 2fr 1fr 1fr` | Feature sections, galleries |
| Swiss Grid | `display: grid; gap: 1px;` with contrasting parent bg for razor lines | Data-heavy, brutalist |
| Gapless Bento | `grid-auto-flow: dense` — mathematically verify no empty cells | Feature grids |

### 5.2 Spacing Scale

| Token | Value | Usage |
|-------|-------|-------|
| `--space-xs` | 4px | Icon-to-label gap |
| `--space-sm` | 8px | Tight internal, inline gaps |
| `--space-md` | 16px | Standard internal padding, card gaps |
| `--space-lg` | 24px | Card padding, section internal |
| `--space-xl` | 32px | Major section gaps |
| `--space-2xl` | 48px | Hero-to-content, large section breaks |
| `--space-3xl` | 64-96px | Section vertical padding (generous) |
| `--space-4xl` | 120-160px | Hero section padding |

**Base unit: 8px.** All spacing must be multiples of 8px (4px allowed for tight icon gaps only). This is the single most important layout rule for visual consistency.

### 5.3 Content Width Rules

| Context | Max Width | Notes |
|---------|-----------|-------|
| Reading / body text | 65ch (~650px at 16px) | Longer lines harm readability |
| Dashboard content area | 1088-1280px | Depends on data density |
| Marketing page container | 1200-1400px | Centered, generous |
| Hero text | `max-w-5xl` to `max-w-6xl` | Widen container to keep headlines short |
| Card internal | 320-480px per card | Before grid wrapping |

### 5.4 Anti-Layout Patterns (Hard Bans)

| Pattern | Why Banned |
|---------|-----------|
| 3 equal cards in a horizontal row | The most AI-generic feature layout. Use 2-col zig-zag, asymmetric bento, or horizontal scroll. |
| Centered hero sections (variance > 4) | Use split screen, left-aligned, or asymmetric whitespace instead. |
| Cards inside cards inside cards | Maximum 2 levels of nesting. Flatten wherever possible. |
| Giant rounded section wrappers | Sections should not feel like "containers of containers." Use whitespace, not borders, to separate. |
| Flexbox `calc(33% - 1rem)` math | Use CSS Grid. Grid is mathematically correct; flexbox percentage math is approximate. |
| `h-screen` / `height: 100vh` | Use `min-h-[100dvh]` — iOS Safari address bar causes `100vh` to jump. |
| Horizontal scroll on mobile | Critical failure. Test at 375px. |
| Overlapping content elements | Every element must occupy its own clean spatial zone. No z-index stacking of content on content. |

### 5.5 Mobile Collapse Rules (< 768px)

1. ALL multi-column layouts collapse to single column. No exceptions.
2. Remove all rotations, negative-margin overlaps, and absolute-positioned content stacking.
3. Buttons go full-width on mobile (minimum 44px height).
4. Typography scales via `clamp()`. Body never below 14px.
5. Inline typography images stack below headline.
6. Section spacing reduces proportionally: `clamp(3rem, 8vw, 6rem)`.
7. Touch targets minimum 44×44px with generous spacing between interactive elements.

### 5.6 The Bento Grid Rule

When using bento grids:
- Apply `grid-auto-flow: dense` — prevents empty cells
- Mathematically verify that `col-span` and `row-span` values interlock without gaps
- 3-5 highly intentional cards beat 8 generic ones
- Vary card sizes: `col-span-8 row-span-2` next to stacked `col-span-4` cards
- Mobile: fall back to single column, reset all `col-span` overrides to `col-span-1`

---

## §6 — INFORMATION DESIGN & CLARITY (Cognitive Anti-Slop)

Visual slop is "this looks AI-generated." Cognitive slop is "I don't understand what I'm looking at." The second is more damaging because it can't be fixed with a font swap.

### 6.1 The 3-Question Framework

Every dashboard, portal, or data display MUST answer these three questions within 5 seconds of the user opening it:

1. **Are we OK?** — A single status signal. Green/yellow/red. The user knows instantly whether to relax or focus.
2. **What needs attention?** — 1-3 items that are outside normal range. Ranked by impact.
3. **What do I decide today?** — A specific, executable action. Never "review the data" — "Approve 3 outreach emails" or "Call the lead who visited pricing 4 times."

If the user cannot answer all three questions within 5 seconds of opening the page, the information design has failed — regardless of visual quality.

### 6.2 The 10 Cognitive Slop Patterns

| # | Pattern | What It Looks Like | The Fix |
|---|---------|-------------------|---------|
| 1 | **Mystery Metrics** | "Engagement Score: 72" — what does 72 mean? Is it good? | Every number needs context: label + target + delta + plain-language interpretation |
| 2 | **Equal Importance** | 12 KPI cards, all same size, same visual weight | Top 3 KPIs get 2x visual weight. Rank by financial impact. |
| 3 | **Data Dump** | Every metric the system can calculate, displayed because it can be | Show only what drives decisions. If showing it doesn't change behavior, hide it. |
| 4 | **False Precision** | "Conversion Rate: 3.742%" — implies accuracy the data doesn't have | Round to meaningful precision. 3.7%. "About 1 in 27." |
| 5 | **Contextless Deltas** | "▲ 12% this week" — from what? Is 12% significant? | Always show: baseline ("from 47 → 53"), direction ("▲ good, because revenue"), significance ("largest weekly move in 3 months") |
| 6 | **Jargon Without Translation** | "CAC:LTV ratio at 0.3" — the business owner might not know these terms | Translate: "You're spending £30 to acquire a customer worth £100. That's healthy." |
| 7 | **Alert Without Action** | "ALERT: Churn risk HIGH" — OK, what do I DO about it? | Every alert must include a specific action: "3 at-risk customers identified. Win-back messages drafted → Review and send." |
| 8 | **Narrative Void** | Numbers sit in isolation. No story connects them. | Write one sentence that connects the dots: "Revenue dipped because 3 large jobs completed and nothing new started. Pipeline has 4 replacements at quote stage." |
| 9 | **Flat Navigation** | Everything visible at once. No progressive disclosure. | Three layers: Overview (are we OK?) → Detail (what's happening?) → Action (what do I do?) |
| 10 | **Missing Mental Model** | User doesn't know where to look first, what anything means, or what "good" looks like | First visit: guided overlay or annotated cards. Persistent: status hierarchy (top-left = most important), consistent layout, targets shown alongside actuals |

### 6.3 Data Presentation Rules

1. **Every number gets context.** Format: `[Value] [Target indicator] [Delta with direction] [Plain-language interpretation]`
2. **Rank by impact, not by alphabet.** Most important data goes top-left (F-pattern reading).
3. **Use concrete language.** "17 of 22 enquiries came on weekdays before 5pm" — not "most enquiries during business hours."
4. **Monospace for numbers.** All numeric data in tables and KPIs uses monospace font. Proportional fonts misalign digits and make scanning harder.
5. **Sparklines over isolated numbers.** A 7-day sparkline on a KPI card tells you instantly whether the number is trending up or down. A bare number requires mental math.
6. **Targets always visible.** Every metric that has a target must show the target alongside the actual. The gap is the story.
7. **Financial impact quantification.** Whenever possible, translate metrics into money: "Closing the Saturday coverage gap = ~£1,134/month in captured enquiries."

### 6.4 Content Clarity Rules

1. **Concrete > Abstract.** "Revenue dropped 11% because Wednesday evenings have 23% call answer rate" — not "revenue has declined due to operational factors."
2. **Specific > General.** "4 quotes expired this week. £12,400 in pipeline at risk." — not "some opportunities were lost."
3. **Active voice.** "Your Pipeline Agent found 3 leads matching your ICP" — not "3 leads were found."
4. **No AI copywriting clichés.** BANNED WORDS: Elevate, Seamless, Unleash, Next-Gen, Game-changer, Revolutionize, Delve, Transformative, Cutting-edge, Best-in-class. Write plain, specific language.
5. **No fake brand names.** BANNED: Acme, Nexus, Flowbit, Quantumly, NovaCore, SmartFlow. Use real-sounding names or actual client names.
6. **No fake round numbers.** Never `99.99%`, `50%`, `1234567`. Use organic data: `47.2%`, `+1 (312) 847-1928`.
7. **No filler UI text.** "Scroll to explore," "Swipe down," scroll arrows, bouncing chevrons are BANNED. The content pulls users in naturally.

---

## §7 — COMPONENT PATTERNS

### 7.1 Buttons

```
Primary:   Accent fill, white text, no outer glow
Secondary: Ghost/outline, accent border, transparent bg
Tertiary:  Text-only, underline on hover
Disabled:  40% opacity (NOT 50%), cursor: not-allowed

Shape:     rounded-md (4-6px) default, rounded-full (pills) only for CTAs in premium mode
Padding:   px-5 py-2.5 (standard), px-6 py-3 (generous/CTA)
Active:    translateY(-1px) or scale(0.98) — tactile push feel
Hover:     background shifts by 8%+ lightness, never a glow
Focus:     2px offset ring in accent color
```

**The "Button-in-Button" pattern (soft-skill):** If a CTA has a trailing arrow/icon, it sits inside its own circular wrapper (`w-8 h-8 rounded-full bg-black/5`) flush with the button's right padding. The icon circle translates diagonally on hover (`group-hover:translate-x-1 group-hover:-translate-y-[1px]`).

**CTA Restraint (stitch-skill):** Maximum one primary CTA button in the hero. No secondary "Learn more" link.

### 7.2 Cards

```
Background:     Surface color
Border:         1px solid at 6-8% opacity of text color
Border-radius:  8-12px (standard), 2rem-2.5rem (premium/soft mode)
Shadow:         Ultra-diffuse: 0 20px 40px -15px rgba(0,0,0,0.05)
                 No shadow in brutalist mode
Padding:        24px internal (standard), 32-40px (generous)
Hover:          Subtle lift: translateY(-2px) + shadow intensifies slightly
                 Duration: 200-300ms, spring physics
```

**Card Restraint:** Use cards ONLY when elevation communicates hierarchy. For high-density layouts (DENSITY > 7), replace cards with `border-top: 1px solid` dividers or negative space. Too many cards = visual noise.

**No Cards-Inside-Cards:** Maximum 2 levels of nesting. If you see card > card > card, flatten it.

### 7.3 Inputs & Forms

```
Layout:       Label ABOVE input (not floating, not placeholder-as-label)
Helper text:  Optional, below label, muted
Error text:   Below input, in error color (#DC2626)
Focus ring:   2px offset in accent color
Gap:          0.5rem between label-input-error in the stack
Width:        Full width of container, max 480px for single-field forms
```

**Anti-patterns:** Floating labels (accessibility nightmare), placeholder-as-label (disappears on focus), inline validation that appears before user finishes typing, submit buttons that are invisible until form is complete.

### 7.4 Data Tables

```
Header:       UPPERCASE, 11px, 700 weight, 0.1em tracking, muted background
Rows:         Alternating subtle backgrounds OR border-bottom dividers (never both)
Hover:        Row background shifts 2-4 lightness points
Sort:         Clickable headers with ▲/▼ indicator on active column
Numbers:      Monospace, right-aligned
Text:         Sans-serif, left-aligned
Actions:      Right-aligned, icon-only or icon+text buttons
Empty:        Composed illustration, not "No data found"
```

### 7.5 KPI Cards (Dashboard + Portal)

```html
<!-- Every KPI card must have ALL of these -->
<div class="kpi-card">
  <div class="kpi-icon"><!-- SVG icon, 24px --></div>
  <div class="kpi-sparkline"><!-- Inline SVG, 7 data points, 60px wide, 24px tall --></div>
  <div class="kpi-label"><!-- UPPERCASE, 11px, 0.1em tracking, muted --></div>
  <div class="kpi-value"><!-- 24-32px, 800 weight, -0.04em tracking, monospace --></div>
  <div class="kpi-delta"><!-- ▲/▼ with color, % change, "from X" context --></div>
  <div class="kpi-target"><!-- Progress bar or "X of Y target" --></div>
</div>
```

### 7.6 Insight / Advisory Cards

```
Structure:    Priority badge (HIGH/MED/LOW) → Headline → 2-3 sentence body → Action button
Priority:     Color-coded (red=HIGH, amber=MED, slate=LOW)
Action:       Specific and executable: "Enable weekend coverage →" not "Learn more"
Financial:    Every insight MUST trace to a revenue or cost figure
```

### 7.7 Modals & Dialogs

```
Backdrop:     rgba(0,0,0,0.6) + backdrop-blur(4px)
Panel:        Surface color, 16px radius, max 560px height, 420-540px width
Header:       Title + close button, bottom border
Body:         Scrollable if needed, 16-20px padding
Footer:       Actions row, right-aligned, 16-20px padding
Close:        ✕ button top-right, Escape key, click-outside
Focus trap:   Tab cycles within modal only
```

### 7.8 Loading States

**Skeletal shimmer ONLY.** Never circular spinners — they communicate nothing.

```
Pattern:      Gray placeholder shapes matching exact layout dimensions + rounded corners
Animation:    Shifting light reflection across placeholder (left-to-right gradient sweep)
Duration:     1.5-2s cycle
States:       One skeleton per content block that will eventually render there
```

### 7.9 Empty States

```
Structure:    Illustration/icon composition (top) + "Nothing yet" headline (middle) + Action button (bottom)
Tone:         Helpful, not accusatory. "You haven't added any leads yet" not "No data."
Action:       Always include a creation button: "+ Add your first lead"
Illustration: Monochrome line sketch or composed icon set — never a generic placeholder
```

### 7.10 Error States

```
Inline:       Red accent border or underline on the failing element
Contextual:   Error message explains what went wrong and how to fix it
Recovery:     Always include a clear recovery action ("Try again," "Check your connection," "Contact support")
Global:       Banner at top for system-level errors, with dismiss button
```

### 7.11 Navigation

```
Desktop:      Horizontal links with generous spacing, no hamburger menu
Mobile:       Clean slide-in or full-screen overlay, labeled menu items
Active:       Accent color indicator (underline or left-border)
Sticky:       Floating glass pill (premium) or simple fixed bar (standard)
              backdrop-blur only on fixed/sticky elements — NEVER on scrolling containers
```

### 7.12 The Double-Bezel Pattern (Premium / Soft Mode)

For interfaces that need to feel physical and expensive:

```
Outer Shell:  Wrapper div with subtle bg (bg-black/5), hairline border (ring-1 ring-black/5),
              p-1.5 or p-2 padding, large outer radius (rounded-[2rem])
Inner Core:   Content container with distinct bg, inner highlight
              (shadow-[inset_0_1px_1px_rgba(255,255,255,0.15)]),
              mathematically smaller radius (rounded-[calc(2rem-0.375rem)])
```

### 7.13 Agent Action Cards (Portal-Specific)

```
Structure:    Agent name + last run time + status dot (green pulsing = active)
              + last output summary + "Run Now" button + next scheduled run
Status dot:   Green with pulse animation (opacity 1 → 0.4 → 1, 2s cycle)
Action:       "Expand pipeline coverage →" or "Review 3 flagged leads →"
```

---

## §8 — INTERACTIVITY & STATES

### 8.1 State Requirements (Every Interactive Element)

Every button, link, input, card, and interactive element MUST have defined styles for ALL of these states:

| State | Requirement |
|-------|------------|
| **Default** | Baseline appearance |
| **Hover** | 8%+ lightness delta. `transition: 200-300ms` |
| **Focus** | `:focus-visible` outline, 2px offset, accent color. NEVER remove focus styles. |
| **Active** | Tactile feedback: `translateY(-1px)` or `scale(0.98)`. 100-150ms. |
| **Disabled** | 40% opacity, `cursor: not-allowed`, no hover effects |
| **Loading** | Skeletal shimmer or inline spinner WITH contextual text ("Sending..." not just a spinner) |
| **Error** | Red accent border/underline, inline error text, clear recovery path |

### 8.2 Disabled State (Critical Rule)

**40% opacity, not 50%.** This specific value (0.40) is the result of user testing at both MD3 and Workday. 50% creates visual competition with active elements — users try to click 50%-opacity buttons. 40% is clearly inactive but still readable. This is a measurable, testable, reproducible perceptual rule — not an opinion.

### 8.3 Hover State (Critical Rule)

**Minimum 8% lightness delta.** Below 8%, the state change is imperceptible on most consumer monitors. This means:
- Light backgrounds: darken by 8%+
- Dark backgrounds: lighten by 8%+
- Test on an actual monitor, not just in code — what looks visible on a MacBook Pro screen may be invisible on a £200 Dell

### 8.4 Focus State

- ALWAYS use `:focus-visible` (not `:focus`) — prevents focus rings on mouse clicks
- Focus ring: 2px solid outline in accent color, 2px offset from element edge
- NEVER remove focus styles without providing an equally visible alternative
- Interactive elements must be reachable via Tab (positive tabindex only when necessary)

### 8.5 Color-Only State Indicators

**BANNED.** State must never be conveyed by color alone:
- Error: red border + error icon + error text
- Success: green border + checkmark + confirmation text
- Warning: amber border + warning icon + warning text
- Active/Selected: accent indicator + text label + (optional) icon

### 8.6 Touch Targets (Mobile)

- Minimum **44×44px** for all interactive elements (WCAG 2.1 AAA is 44px, AA requires "sufficient" size — we target AAA here because it's a measurable, defensible standard)
- Generous spacing between touch targets (minimum 8px gap)
- Buttons go full-width on viewports below 768px

---

## §9 — MOTION ENGINE

### 9.1 The Hardware Acceleration Rule (Applies to ALL animation)

**Only animate `transform` and `opacity`.** Never animate `top`, `left`, `width`, `height`, or any layout-triggering property. This is not a preference — layout-triggering animations run on the main thread, cause reflows, and kill frame rates.

```css
/* CORRECT — compositor-only, 60fps */
.element { transform: translateY(12px); opacity: 0; }
.element.visible { transform: translateY(0); opacity: 1; }

/* WRONG — triggers layout, janky */
.element { top: 12px; opacity: 0; }
```

### 9.2 Spring Physics Default

All interactive motion uses spring physics, not linear or default easing:

```
Default spring:    stiffness: 100, damping: 20
CSS equivalent:    cubic-bezier(0.32, 0.72, 0, 1)
Entrance easing:   cubic-bezier(0.16, 1, 0.3, 1) — gentle fade-up
```

**Banned easing:** `linear`, `ease-in-out` (the default that screams "I didn't think about motion")

### 9.3 Motion Duration Rules

| Context | Duration | Notes |
|---------|----------|-------|
| Micro-interactions (hover, focus, active) | 100-200ms | Fast enough to feel instant |
| Small element entrance (icon, badge, tooltip) | 200-400ms | Perceptible but not slow |
| Card/section entrance | 400-600ms | Weighty, intentional |
| Hero/hero element entrance | 600-800ms | Cinematic, draws attention |
| Page transition | 300-500ms | Between routes/states |
| Background ambient | 20s+ | Barely perceptible drift |

**Floor: 100ms. Ceiling: 800ms for entrances.** (PencilPlaybook: motion under 100ms is invisible, over 800ms feels like the interface is lagging)

### 9.4 Scroll Entry (Standard Pattern)

```css
.entrance {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 600ms cubic-bezier(0.16, 1, 0.3, 1),
              transform 600ms cubic-bezier(0.16, 1, 0.3, 1);
}
.entrance.visible {
  opacity: 1;
  transform: translateY(0);
}
```

**Implementation:** Use `IntersectionObserver`, NEVER `window.addEventListener('scroll')` — scroll handlers cause continuous reflows and kill mobile performance.

### 9.5 Staggered Reveals

Lists and grids enter with cascaded delays:

```css
.list-item {
  animation-delay: calc(var(--index) * 80ms);
  /* Items cascade in rather than all appearing at once */
}
```

**Never mount everything at once.** Stagger creates the perception of speed — the first item appears instantly while the rest cascade, giving the brain time to process.

### 9.6 Perpetual Micro-Loops

Active dashboard components may have infinite-loop states:

| Loop | Use | Implementation |
|------|-----|---------------|
| **Pulse** | Status dots, live indicators | `opacity` 1 → 0.4 → 1, 2s cycle |
| **Shimmer** | Loading skeletons | Gradient sweep across placeholder, 1.5-2s |
| **Float** | Feature icons, decorative elements | `translateY(0)` → `translateY(-4px)`, 3-4s cycle |
| **Typewriter** | Search placeholder text | Rotate through search suggestions, 4-5s per phrase |

**Constraint:** Perpetual animations MUST be on `position: fixed; pointer-events: none` layers or isolated leaf components. Never trigger parent re-renders. Target 60fps minimum.

### 9.7 GSAP (When Used)

```javascript
// Always create paused timeline, register for HyperFrames
const tl = gsap.timeline({ paused: true, defaults: { duration: 0.6, ease: "power3.out" } });
tl.from(".title", { y: 48, opacity: 0 }, 0)
  .to(".accent", { scaleX: 1, duration: 0.5 }, 0.25);

// Use stagger, not manual delays
gsap.to(".item", { x: (i) => i * 50, stagger: 0.1 });

// Never infinite repeat (-1) — compute finite repeats from visible duration
// Use transform aliases: x, y, scale, rotation, autoAlpha — never raw transform strings
// Respect prefers-reduced-motion via gsap.matchMedia()
```

### 9.8 CSS Animations (When Used)

```css
/* Good: finite iteration, compositor-only properties */
@keyframes pulse-ring {
  from { opacity: 0; transform: scale(0.82); }
  35%  { opacity: 1; }
  to   { opacity: 0; transform: scale(1.18); }
}
.pulse-ring {
  animation: pulse-ring 1200ms cubic-bezier(0.2, 0, 0, 1) 3 both;
}

/* Stagger via CSS custom properties */
.dot { animation: dot-pop 900ms ease-out both; animation-delay: calc(var(--i) * 120ms); }
```

### 9.9 Motion Intensity Tuning

| Level | Value | Character |
|-------|-------|-----------|
| Static | 1-2 | No animation. Pure document. |
| Subtle | 3-4 | Hover/active states only. Scroll entries at reduced duration. |
| Fluid | 5-7 | Spring physics, staggered reveals, scroll entries, perpetual micro-loops on dashboards. |
| Cinematic | 8-10 | GSAP ScrollTriggers, pinned sections, scrubbing text reveals, card stacking. Full choreography. |

### 9.10 `prefers-reduced-motion`

Always wrap aggressive motion in a reduced-motion check:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

In GSAP: use `gsap.matchMedia()` with `(prefers-reduced-motion: reduce)` condition, setting duration to 0.

---

## §10 — ACCESSIBILITY BASELINE (WCAG 2.1 AA)

### 10.1 Non-Negotiable Requirements

| # | Requirement | Standard |
|---|------------|----------|
| 1 | Color contrast ratio minimum 4.5:1 for body text, 3:1 for large text (18px+ bold or 24px+ regular) | WCAG AA 1.4.3 |
| 2 | All interactive elements keyboard accessible (Tab, Enter, Space, Escape) | WCAG AA 2.1.1 |
| 3 | Focus indicators visible on all interactive elements (`:focus-visible`) | WCAG AA 2.4.7 |
| 4 | Touch targets minimum 44×44px | WCAG AAA 2.5.5 (we target AAA for touch) |
| 5 | All form inputs have associated `<label>` elements | WCAG AA 1.3.1 |
| 6 | Images have `alt` attributes (descriptive or empty for decorative) | WCAG AA 1.1.1 |
| 7 | Page has a logical heading hierarchy (h1 → h2 → h3, no skips) | WCAG AA 1.3.1 |
| 8 | State not conveyed by color alone (always pair with icon or text) | WCAG AA 1.4.1 |
| 9 | `prefers-reduced-motion` respected | WCAG AA 2.3.3 |
| 10 | Page has a descriptive `<title>` and `lang` attribute | WCAG AA 2.4.2 |

### 10.2 Keyboard Navigation

- **Tab order** follows visual layout (don't break it with `tabindex` > 0)
- **Modal focus trap:** Tab cycles within modal, Escape closes
- **Dropdown menus:** Arrow keys navigate options, Enter selects, Escape closes
- **Skip link:** "Skip to main content" as first focusable element on every page

### 10.3 Screen Reader Essentials

- **ARIA labels** on elements without visible text (icon buttons, close buttons)
- **`aria-live` regions** for dynamic content updates: `aria-live="polite"` for status updates, `aria-live="assertive"` for critical alerts
- **`role` attributes** on custom interactive elements (custom selects, tabs, dialogs)
- **`aria-expanded`** on toggle buttons, **`aria-selected`** on selected items
- **Descriptive link text:** "View Q1 2026 report" not "Click here"

### 10.4 Common Accessibility Anti-Patterns

| Anti-Pattern | Fix |
|-------------|-----|
| `placeholder` as label | Use `<label>` above input |
| `display: none` on focusable elements | Use `visibility: hidden` or remove from tab order |
| `outline: none` without replacement | Use `:focus-visible` with custom outline |
| Click handlers on non-interactive elements (div, span) | Use `<button>` — it's free and accessible by default |
| `aria-*` attributes without testing with a screen reader | Test with VoiceOver (Mac) or NVDA (Windows) |
| Color-only error states | Always add icon + text |
| Infinite scroll without "load more" fallback | Provide a manual trigger |

### 10.5 Semantic HTML First

Before reaching for ARIA, use the correct HTML element:
- `<button>` for actions (not `<div onclick="...">`)
- `<a>` for navigation (not `<span onclick="location=...">`)
- `<input>` + `<label>` for form fields
- `<table>` for tabular data (not CSS grid tables)
- `<nav>` for navigation regions
- `<main>` for primary content
- `<dialog>` for modals (with polyfill if needed)

---

## §11 — MODE OVERRIDES

When a project calls for a specific aesthetic, apply ONE mode override. Modes override the defaults in §3-§9. Do not mix modes mid-project.

### 11.1 Mode Selection Decision Matrix

| Project Type | Mode | Key Traits |
|-------------|------|-----------|
| SaaS, productivity, developer tools | **Soft Structural** | Diffused shadows, generous radius, spring physics, airy spacing |
| Dashboards, data-heavy, enterprise | **Swiss Rational** | Grid-obsessed, monochrome, typography-first, invisible borders |
| Portfolio, lifestyle, legal, editorial | **Editorial Luxury** | Serif display, warm off-white, film grain, massive type contrast |
| Terminal apps, declassified-data aesthetic | **Industrial Brutalist** | 90° corners, visible grids, monospace data, CRT scanlines |
| Clean, warm, document-style workspaces | **Minimalist** | Warm monochrome, flat bento, muted pastels, editorial serif option |
| When in doubt or client has existing system | **Neutral Baseline** | System fonts, grayscale, minimal opinion |

### 11.2 Mode: Soft Structural (Premium / Awwwards-Tier)

**Override source:** soft-skill

```
Typography:  Geist, Clash Display, Plus Jakarta Sans, or PP Editorial New
             Inter/Roboto/Arial/Open Sans/Helvetica BANNED
Icons:       Phosphor Light, Remix Line (ultra-light precise lines)
             Lucide/FontAwesome/Material Icons BANNED
Cards:       Double-Bezel pattern (outer shell + inner core)
             radius: 2rem-2.5rem (exaggerated squircle)
             Shadow: ultra-diffuse, wide-spreading, low opacity
Buttons:     rounded-full CTA pills, button-in-button trailing icons
Spacing:     py-24 to py-40 for sections (double standard)
Layout:      Asymmetrical Bento or Z-Axis Cascade or Editorial Split
Motion:      Custom cubic-bezier curves, spring physics exclusively,
             staggered nav reveals, magnetic button hover physics,
             scroll entry with blur dissolve (translate-y-16 blur-md → clear)
Borders:     hairline ring-1, never generic 1px solid gray
Shadows:     heavily customized ultra-diffuse, never shadow-md/lg/xl
Background:  Deep OLED (#050505) + radial mesh gradients
             OR warm creams (#FDFBF7) + CSS noise overlay
             OR silver-grey/white + ambient floating shadows
```

### 11.3 Mode: Industrial Brutalist

**Override source:** brutalist-skill

```
Typography:  Neue Haas Grotesk Black, Inter Extra Bold, Archivo Black,
             JetBrains Mono, IBM Plex Mono, Space Mono, VT323
             Massive scale: clamp(4rem, 10vw, 15rem)
             Macro: tight tracking (-0.03 to -0.06em), compressed leading (0.85-0.95), UPPERCASE
             Micro: generous tracking (0.05-0.1em), monospace, UPPERCASE
Color:       Light: #F4F4F0 bg, #050505 fg, #E61919 accent only
             Dark: #0A0A0A bg, #EAEAEA fg, #E61919 accent only
             Terminal green (#4AF626): ONE element only, if needed
             Gradients, soft shadows, translucency STRICTLY PROHIBITED
Layout:      CSS Grid with gap: 1px for razor-thin lines
             All corners exactly 90° — NO border-radius anywhere
             Visible compartmentalization: 1-2px solid borders everywhere
             Bimodal density: extreme density OR vast negative space
Effects:     Halftone dithering, CRT scanlines, SVG noise overlay
             ASCII framing: [ DELIVERY SYSTEMS ], >>> directional markers
             Registration marks, crosshairs at grid intersections
Semantic:    <data>, <samp>, <kbd>, <output>, <dl> tags
```

### 11.4 Mode: Editorial Luxury

**Override source:** minimalist-skill + soft-skill + gpt-tasteskill

```
Typography:  Serif display: Lyon Text, Newsreader, Playfair Display, Instrument Serif
             Sans body: SF Pro Display, Geist Sans, Helvetica Neue, Switzer
             Mono: Geist Mono, SF Mono, JetBrains Mono
             Display tracking: -0.02 to -0.04em, leading 1.1
             Body: off-black only (#111111 or #2F3437), leading 1.6
Color:       Canvas: #FFFFFF or #F7F6F3 (warm bone)
             Text: #111111 primary, #787774 secondary
             Accent: washed-out pastels only
               Pale Red #FDEBEC (text #9F2F2D)
               Pale Blue #E1F3FE (text #1F6C9F)
               Pale Green #EDF3EC (text #346538)
               Pale Yellow #FBF3DB (text #956400)
Layout:      Generous sections (py-24 to py-32)
             Content max-w-4xl or max-w-5xl
             Asymmetric, editorial split layouts
             Bento grids with 1px solid #EAEAEA borders, 8-12px radius
Buttons:     Solid #111111 bg, white text, 4-6px radius, no shadow
             Active: scale(0.98)
             Hover: background shifts to #333333
Cards:       1px solid #EAEAEA border, 8-12px radius
             No shadow (ultra-flat aesthetic)
Icons:       Phosphor Bold or Fill weights, Radix UI Icons
             Thicker stroke aesthetic
Motion:      Subtle: translateY(12px) + opacity 0 → 1, 600ms
             IntersectionObserver only
             Background: slow radial gradient blob (20s+, opacity 0.02-0.04)
```

### 11.5 Mode: Minimalist (Premium Utilitarian)

**Override source:** minimalist-skill

```
Typography:  SF Pro Display, Geist Sans, Switzer — clean geometric/system
             Serif option for hero: Lyon Text, Newsreader, Instrument Serif
             Mono: Geist Mono, SF Mono, JetBrains Mono
Color:       Canvas: #FFFFFF or #FBFBFA (warm white)
             Surface: #FFFFFF or #F9F9F8
             Borders: #EAEAEA or rgba(0,0,0,0.06)
             Text: #111111 primary, #787774 secondary
             Accent: washed-out pastels only (muted red, blue, green, yellow)
             NEVER: gradients, neon, glassmorphism, primary-colored large elements
Icons:       Phosphor Bold/Fill, Radix UI
             NEVER: Lucide, Feather, Heroicons — too thin, too generic
Layout:      Flat bento grids: 1px solid #EAEAEA borders, 8-12px radius max
             Padding: 24-40px internal
             Section spacing: py-24 to py-32
             Content width: max-w-4xl or max-w-5xl
Buttons:     Solid #111111, white text, 4-6px radius, no shadow
             Active: scale(0.98)
             NEVER: rounded-full for containers, cards, or primary buttons
Tags:        Pill-shaped (rounded-full), text-xs, UPPERCASE, 0.05em tracking
             Background: muted pastels only
Shadows:     Ultra-subtle or none. If used: 0 2px 8px rgba(0,0,0,0.04)
             NEVER: shadow-md, shadow-lg, shadow-xl
```

### 11.6 The Design Dials (Project-Level Overrides)

Set these at project start. They cascade through all rules above.

| Dial | Range | Default | What It Controls |
|------|-------|---------|-----------------|
| DESIGN_VARIANCE | 1-10 | 6 | Layout predictability. 1=rigid symmetric. 10=artsy chaotic. |
| MOTION_INTENSITY | 1-10 | 5 | Animation depth. 1=static. 10=cinematic GSAP choreography. |
| VISUAL_DENSITY | 1-10 | 5 | Information density. 1=gallery-airy. 10=cockpit-dense. |

**Dial cascade effects:**
- VISUAL_DENSITY > 7 → all numbers forced to monospace, cards replaced with dividers
- DESIGN_VARIANCE < 3 → centered layouts allowed, symmetric grids preferred
- DESIGN_VARIANCE > 7 → centered hero BANNED, asymmetric required
- MOTION_INTENSITY < 3 → no scroll entries, hover-only motion, reduced durations
- MOTION_INTENSITY > 7 → GSAP ScrollTriggers, pinning, scrubbing text reveals

---

## §12 — QUALITY GATE

**MUST PASS before ANY visual output is delivered.** This is the last filter. If any check fails, fix it before showing the user.

### 12.1 Quick Visual Scan (30 seconds)

- [ ] No Inter, Roboto, Arial, Open Sans fonts visible
- [ ] No purple/blue AI gradients anywhere
- [ ] No pure black (#000000) — all blacks are off-black
- [ ] No emojis in any text, heading, or alt attribute
- [ ] No "Elevate," "Seamless," "Unleash," "Next-Gen," or other AI clichés
- [ ] No 3 equal cards in a horizontal row (unless VARIANCE < 3)
- [ ] No centered hero with generic layout (unless VARIANCE < 3)
- [ ] No "Scroll to explore" or bouncing chevrons
- [ ] No cards inside cards inside cards
- [ ] No circular spinners (skeletal shimmer only)

### 12.2 5-Dimension Critique (huashu-design)

Score each dimension 1-5. Anything under 3 = fix before emitting.

| Dimension | What to Check |
|-----------|--------------|
| **Philosophy** | Does the design have a clear point of view? Is it making deliberate choices or averaging defaults? |
| **Hierarchy** | Can you identify the 3 most important elements in 2 seconds? Does visual weight match information importance? |
| **Detail** | Are states complete (hover, focus, active, disabled, error)? Are edge cases handled (empty, loading, long text)? |
| **Function** | Can the user complete their primary task without friction? Are touch targets sufficient? Is navigation clear? |
| **Innovation** | Is there at least one element that feels designed for THIS specific context — not pulled from a template? |

### 12.3 Content & Clarity Check

- [ ] The 3-Question Framework is answerable in 5 seconds (Are we OK? What needs attention? What do I decide?)
- [ ] Every number has context (label + target + delta + plain-language interpretation)
- [ ] No mystery metrics — every value is understandable to a non-technical user
- [ ] Every alert includes a specific action ("Do X" not "Be aware of Y")
- [ ] No jargon without plain-language translation
- [ ] No fake names (Acme, Nexus), fake numbers (99.99%), or filler text
- [ ] All copy is concrete and specific, not abstract and generic

### 12.4 Accessibility Baseline

- [ ] Color contrast ≥ 4.5:1 for body text, 3:1 for large text
- [ ] All interactive elements keyboard accessible
- [ ] Focus indicators visible (`:focus-visible`)
- [ ] All form inputs have labels
- [ ] Images have alt attributes
- [ ] Heading hierarchy is logical (no skipped levels)
- [ ] State not conveyed by color alone
- [ ] Touch targets ≥ 44×44px on mobile
- [ ] `prefers-reduced-motion` respected

### 12.5 Output Completeness (output-skill)

- [ ] No `// ...`, `// TODO`, `/* ... */`, or bare `...` in code
- [ ] No "rest of the code follows the same pattern" or "implement similarly"
- [ ] Every requested deliverable is present and complete
- [ ] Code blocks contain actual runnable code, not descriptions
- [ ] No "Let me know if you want me to continue" or "I can provide more details"

### 12.6 Motion Check (if animation present)

- [ ] All animations use `transform` and `opacity` only (no `top`/`left`/`width`/`height`)
- [ ] No `linear` or `ease-in-out` easing — spring physics or custom cubic-bezier
- [ ] `backdrop-blur` only on fixed/sticky elements
- [ ] Scroll detection uses `IntersectionObserver`, not `window.addEventListener('scroll')`
- [ ] `prefers-reduced-motion` respected
- [ ] `will-change` used sparingly, only on actively animating elements

### 12.7 Responsive Check

- [ ] Tested at 375px, 768px, 1440px
- [ ] No horizontal scroll on mobile
- [ ] All multi-column layouts collapse to single column below 768px
- [ ] Buttons full-width on mobile
- [ ] Typography scales via `clamp()`, body ≥ 14px

---

## §13 — FRAMEWORK ADAPTERS

### 13.1 Tailwind v3

```js
// tailwind.config.js — extend, don't overwrite
module.exports = {
  theme: {
    extend: {
      colors: {
        // Map DESIGN.md tokens here
        canvas: '#F9FAFB',
        surface: '#FFFFFF',
        accent: '#3B82F6',
        // ... etc
      },
      fontFamily: {
        sans: ['Geist', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'ui-monospace', 'monospace'],
      },
      spacing: {
        // 8px base unit extensions if needed
      },
      borderRadius: {
        card: '0.75rem',    // 12px
        button: '0.375rem', // 6px
        modal: '1rem',      // 16px
      },
    },
  },
};
```

### 13.2 Tailwind v4

```css
@import "tailwindcss";

@theme {
  --color-canvas: #F9FAFB;
  --color-surface: #FFFFFF;
  --color-accent: #3B82F6;
  --font-sans: "Geist", system-ui, sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --spacing-card: 1.5rem;     /* 24px */
  --spacing-section: 6rem;    /* 96px */
  --radius-card: 0.75rem;
  --radius-button: 0.375rem;
}
```

### 13.3 Vanilla CSS (CSS Custom Properties)

```css
:root {
  /* Always use semantic names, never raw hex scattered in components */
  --color-canvas: #F9FAFB;
  --color-surface: #FFFFFF;
  --color-text: #0F172A;
  --color-text-secondary: #64748B;
  --color-accent: #3B82F6;
  --color-accent-hover: #2563EB;
  --color-border: rgba(15, 23, 42, 0.08);
  --color-success: #16A34A;
  --color-warning: #D97706;
  --color-error: #DC2626;
  --font-sans: 'Geist', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', 'SF Mono', ui-monospace, monospace;
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-xl: 16px;
  --space-unit: 8px;
  --text-body: 1rem;
  --leading-body: 1.6;
  --tracking-display: -0.025em;
  --tracking-overline: 0.05em;
  --shadow-card: 0 20px 40px -15px rgba(0, 0, 0, 0.05);
  --motion-spring: cubic-bezier(0.32, 0.72, 0, 1);
  --motion-entrance: cubic-bezier(0.16, 1, 0.3, 1);
}
```

**Rule:** NEVER use raw hex values in component CSS. Always reference the custom property. `color: var(--color-text)` not `color: #0F172A`. This is what makes token propagation possible.

### 13.4 React / JSX Patterns

- One component file ≤ 200 lines. Split if longer.
- No inline styles — use CSS modules, Tailwind classes, or styled-components
- All interactive elements must have defined states (see §8)
- Form inputs must have associated labels (htmlFor + id)
- Use `<button>` not `<div onClick>`
- Respect `prefers-reduced-motion` at the provider/context level

---

## §14 — APPENDIX: TOKEN PRESETS

Ready-to-use design system presets. Pick one, customize the accent, start building.

### 14.1 Preset: Midnight (Dark, Electric Blue)

```json
{
  "palette": "monochrome_dark",
  "colors": {
    "canvas": "#07090F",
    "surface": "#0C1018",
    "card": "#111622",
    "cardHover": "#161D2B",
    "border": "#1E2D42",
    "text": "#E2EAF6",
    "textSecondary": "#8899B4",
    "accent": "#58A6FF",
    "accentHover": "#79B8FF"
  },
  "typography": {
    "display": "Inter",
    "body": "Inter",
    "mono": "JetBrains Mono"
  },
  "density": "balanced",
  "variance": 5,
  "motion": 4,
  "darkMode": true
}
```

### 14.2 Preset: Ember (Terminal Dark, Amber)

```json
{
  "palette": "monochrome_dark",
  "colors": {
    "canvas": "#0A0A0A",
    "surface": "#141414",
    "card": "#1A1A1A",
    "border": "#262626",
    "text": "#E5E5E5",
    "textSecondary": "#A3A3A3",
    "accent": "#F59E0B",
    "accentHover": "#FBBF24"
  },
  "typography": {
    "display": "JetBrains Mono",
    "body": "JetBrains Mono",
    "mono": "JetBrains Mono"
  },
  "spacing": "tight",
  "density": 8,
  "variance": 3,
  "motion": 2,
  "darkMode": true
}
```

### 14.3 Preset: Grove (Earthy Light, Forest Green)

```json
{
  "palette": "warm_minimal",
  "colors": {
    "canvas": "#FFFBEB",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "border": "#E5E5E0",
    "text": "#1A1A1A",
    "textSecondary": "#6B7280",
    "accent": "#2D6A4F",
    "accentHover": "#1B4332"
  },
  "typography": {
    "display": "DM Sans",
    "body": "DM Sans",
    "mono": "JetBrains Mono"
  },
  "spacing": "generous",
  "density": 3,
  "variance": 4,
  "motion": 3,
  "darkMode": false
}
```

### 14.4 Preset: Bloom (Playful Light, Rose)

```json
{
  "palette": "light_clean",
  "colors": {
    "canvas": "#FFFFFF",
    "surface": "#F8FAFC",
    "card": "#FFFFFF",
    "border": "#E2E8F0",
    "text": "#0F172A",
    "textSecondary": "#64748B",
    "accent": "#F43F5E",
    "accentHover": "#E11D48"
  },
  "typography": {
    "display": "Plus Jakarta Sans",
    "body": "Plus Jakarta Sans",
    "mono": "JetBrains Mono"
  },
  "density": 3,
  "variance": 7,
  "motion": 6,
  "darkMode": false
}
```

### 14.5 Preset: Volt (Neobrutalist, Yellow + Black)

```json
{
  "palette": "light_clean",
  "colors": {
    "canvas": "#FFFFFF",
    "surface": "#FAFAFA",
    "card": "#FFFFFF",
    "border": "#000000",
    "text": "#000000",
    "textSecondary": "#525252",
    "accent": "#FACC15",
    "accentHover": "#EAB308"
  },
  "typography": {
    "display": "Space Grotesk",
    "body": "Space Grotesk",
    "mono": "JetBrains Mono"
  },
  "density": 4,
  "variance": 8,
  "motion": 5,
  "darkMode": false,
  "borderRadius": "0px — 90° corners everywhere",
  "shadows": "4px hard offset black, no diffusion"
}
```

### 14.6 Preset: Material Design 3

```json
{
  "palette": "light_clean",
  "colors": {
    "canvas": "#FFFBFE",
    "surface": "#FFFBFE",
    "card": "#F7F2FA",
    "border": "#CAC4D0",
    "text": "#1C1B1F",
    "textSecondary": "#49454F",
    "accent": "#6750A4",
    "accentHover": "#4F378B"
  },
  "typography": {
    "display": "Roboto",
    "body": "Roboto",
    "mono": "Roboto Mono"
  },
  "density": 4,
  "variance": 2,
  "motion": 4,
  "darkMode": false
}
```

### 14.7 Preset: Minimal / Neutral

```json
{
  "palette": "light_clean",
  "colors": {
    "canvas": "#FAFAFA",
    "surface": "#FFFFFF",
    "card": "#FFFFFF",
    "border": "#E5E5E5",
    "text": "#0A0A0A",
    "textSecondary": "#737373",
    "accent": "#171717",
    "accentHover": "#262626"
  },
  "typography": {
    "display": "system-ui",
    "body": "system-ui",
    "mono": "ui-monospace"
  },
  "density": 5,
  "variance": 3,
  "motion": 2,
  "darkMode": false
}
```

### 14.8 Preset: SEGGUINÉE Navy (Government / Legal)

```json
{
  "palette": "navy_and_white",
  "colors": {
    "canvas": "#0F172A",
    "surface": "#1E293B",
    "card": "#1E293B",
    "cardHover": "#273449",
    "border": "#334155",
    "text": "#F8FAFC",
    "textSecondary": "#94A3B8",
    "accent": "#3B82F6",
    "accentHover": "#2563EB",
    "gold": "#F59E0B"
  },
  "typography": {
    "display": "Geist",
    "body": "Geist",
    "mono": "JetBrains Mono"
  },
  "density": 8,
  "variance": 3,
  "motion": 3,
  "darkMode": true,
  "dialOverrides": "VARIANCE=3 (government needs predictability), MOTION=3 (subtle CSS only), DENSITY=8 (Cockpit Mode — packed data, monospace numbers)"
}
```

---

## VERSION HISTORY

| Version | Date | Changes |
|---------|------|---------|
| 4.0 | 2026-05-22 | Complete rewrite. 17 sources absorbed into 14 sections. Zero overlap. One file. |
| 3.0 | 2026-04-15 | Orchestrator version. Loaded 5 source skills in sequence. |
| 2.0 | 2026-03-01 | Initial design skill. |
