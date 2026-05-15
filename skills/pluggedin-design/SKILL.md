---
name: pluggedin-design
description: "PluggedIN unified web design intelligence. Synthesises huashu-design (base philosophy), ui-ux-pro-max (design system depth), open-design (structure + dashboard patterns), gsap (cinematic animation), and css-animations (transitions). Use for all HTML, dashboards, portals, and website work."
---

# PluggedIN Design Intelligence

You are a senior web designer who has studied and internalised 5 design systems. Before producing any visual output, read all source skills listed below in order. Then apply the synthesis rules from this file.

## Step 1 — Load all source skills (mandatory, in order)

Read each file in full before writing a single line of HTML:

1. `skills/huashu-design/SKILL.md` — base philosophy and anti-slop rules
2. `skills/ui-ux-pro-max/SKILL.md` — design system depth (tokens, palettes, font pairings)
3. `skills/open-design/SKILL.md` — structural patterns and dashboard templates
4. `skills/gsap/SKILL.md` — GSAP animation reference (use for complex motion)
5. `skills/css-animations/SKILL.md` — CSS animation patterns (use for simple transitions)

## Step 2 — Apply the synthesis

After reading all 5, use the following rules. These override any conflicting rule in the source skills.

---

### LAYER 1 — huashu-design (base constraints, non-negotiable)

These rules from huashu-design always win:

- NO purple gradients — ever
- NO Inter as display font
- NO emoji icons
- USE oklch() for all colour values
- USE CSS Grid as the primary layout tool
- USE `text-wrap: pretty` on all paragraph elements
- ONE accent colour maximum per design
- Syne for display headings, Inter for body
- Every visual decision must be intentional — nothing decorative for its own sake

---

### LAYER 2 — ui-ux-pro-max (design system depth)

Elevate the design using:

- **Colour palettes**: Use ui-ux-pro-max's palette vocabulary but convert all values to oklch()
- **Font pairings**: Use their pairing logic — but never Inter as display, never system-ui alone for headings
- **Design tokens**: Define CSS custom properties at `:root` for every colour, spacing unit, radius, and shadow
- **Component patterns**: Use their shadcn/UI-inspired component structures for cards, inputs, buttons
- **Brand identity thinking**: Before designing, establish: primary colour, secondary, neutral, accent. Then stick to them.

---

### LAYER 3 — open-design (structure and information architecture)

Use open-design's structural intelligence:

- **Information hierarchy first**: Establish what the viewer must understand in 3 seconds, then design around that
- **Dashboard layouts**: Use their grid patterns for multi-panel layouts — header row, KPI strip, main content, sidebar
- **Data density**: Design for the right information density — not too sparse (wasteful), not too dense (overwhelming)
- **Whitespace as structure**: Use negative space deliberately to group related elements

---

### LAYER 4 — GSAP (complex animation)

Use GSAP when:
- Multiple elements animate in sequence
- A timeline needs precise control
- You need stagger effects across lists or grids
- Motion needs to feel cinematic (entrances, exits, reveals)

GSAP pattern:
```js
const tl = gsap.timeline({ defaults: { ease: "power3.out" } });
tl.from(".hero-title",  { y: 40, opacity: 0, duration: 0.7 }, 0)
  .from(".hero-sub",    { y: 24, opacity: 0, duration: 0.6 }, 0.15)
  .from(".hero-cta",    { y: 16, opacity: 0, duration: 0.5 }, 0.3)
  .from(".stat-item",   { y: 20, opacity: 0, duration: 0.5, stagger: 0.08 }, 0.4);
```

Load GSAP from CDN: `https://cdn.jsdelivr.net/npm/gsap@3.14.2/dist/gsap.min.js`

---

### LAYER 5 — css-animations (simple transitions)

Use CSS animations when:
- A single element transitions between two states
- Hover effects
- Pulse, fade, or slide-in that doesn't need timeline control
- You want zero JS dependency

CSS pattern:
```css
.reveal {
  opacity: 0;
  transform: translateY(24px);
  transition: opacity .6s cubic-bezier(.16,1,.3,1),
              transform .6s cubic-bezier(.16,1,.3,1);
}
.reveal.on { opacity: 1; transform: none; }
```

Use Intersection Observer to trigger `.on` class. This is the default animation approach for scroll reveals.

---

## Step 3 — Decision matrix

| Situation | Use |
|-----------|-----|
| Scroll reveal on section entry | CSS transitions + Intersection Observer |
| Hero entrance (multiple elements) | GSAP timeline |
| Counter animation | requestAnimationFrame (vanilla JS) |
| Hover state | CSS transition only |
| Page/section transition | GSAP |
| Loading state | CSS animation (keyframes) |
| Dashboard layout | open-design grid patterns |
| Colour system | oklch() from ui-ux-pro-max palette vocabulary |
| Typography | huashu-design rules (Syne display, Inter body) |
| Components | ui-ux-pro-max component patterns |

---

## Step 4 — Quality checklist before output

Before writing the final HTML, verify:

- [ ] All colours are oklch() — no hex in visual tokens
- [ ] No purple gradients anywhere
- [ ] Display font is Syne (or another strong display face) — NOT Inter
- [ ] CSS custom properties defined at `:root` for every colour and spacing value
- [ ] CSS Grid used for all multi-column layouts
- [ ] `text-wrap: pretty` on all `<p>` elements
- [ ] GSAP loaded from CDN if GSAP is used
- [ ] Scroll reveals use Intersection Observer
- [ ] Every animation has a purpose — not just decoration
- [ ] One accent colour used consistently
- [ ] Mobile responsive (grid collapses correctly at 960px and 560px)

---

## What makes PluggedIN design different

We are not building generic SaaS pages. We are building AI infrastructure interfaces for business owners. The visual language must communicate:

1. **Seriousness** — this is a real operating system, not a chatbot
2. **Intelligence** — the system knows things, surfaces them clearly
3. **Trust** — dark, composed, confident — not loud
4. **Premium** — they are paying for an outcome, not a tool

Every design decision should pass this filter: does this make the product feel like infrastructure, or does it make it feel like a startup's landing page?
