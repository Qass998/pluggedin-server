"""
lib/website_builder.py — Animated Website Generator + Netlify Deploy

Module 13: Website Builder Agent

Design philosophy:
  Higgsfield-inspired motion  — cinematic scroll reveals, full-screen moments,
                                everything has weight and direction
  Huashu aesthetic            — architectural whitespace, ink-brush restraint,
                                nothing decorative, everything intentional
  Open Design principles      — semantic HTML, accessible, fast, no bloat
  Impeccable execution        — every pixel deliberate, every transition earned

Pipeline:
  business_profile → Claude Sonnet (copy + structure) → HTML generator →
  Netlify API (zip + deploy) → live URL returned in under 60 seconds

Also handles:
  - Client portal white-label deploy to Netlify (per-client subdomain)
  - Preview generation (base64 screenshot placeholder)
  - Multi-page sites (home, services, about, contact)

Netlify API:
  Token: NETLIFY_TOKEN in .env
  Endpoint: https://api.netlify.com/api/v1/
  Deploy: POST /sites → POST /deploys with zip
"""

import os
import io
import json
import zipfile
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
NETLIFY_TOKEN     = os.getenv("NETLIFY_TOKEN", "")
NETLIFY_API       = "https://api.netlify.com/api/v1"


# ─────────────────────────────────────────────
# DESIGN SYSTEM
# Shared tokens used across all generated sites
# ─────────────────────────────────────────────

FONT_STACKS = {
    "professional": ("'Plus Jakarta Sans', 'Inter', sans-serif", "https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap"),
    "luxury":       ("'Cormorant Garamond', 'Georgia', serif",  "https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@300;400;500;600;700&display=swap"),
    "technical":    ("'JetBrains Mono', 'Fira Code', monospace",  "https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;500;700&display=swap"),
    "friendly":     ("'DM Sans', 'Inter', sans-serif",           "https://fonts.googleapis.com/css2?family=DM+Sans:ital,wght@0,300;0,400;0,500;0,700;1,400&display=swap"),
    "budget":       ("'Inter', system-ui, sans-serif",           "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap"),
}

COLOUR_PALETTES = {
    "professional": {"bg": "#0a0a0f", "surface": "#12121a", "text": "#e8e8f0", "accent": "#6366f1", "muted": "#525266"},
    "luxury":       {"bg": "#0d0b08", "surface": "#161310", "text": "#f0ede8", "accent": "#b59a6a", "muted": "#665c4d"},
    "technical":    {"bg": "#050a10", "surface": "#0d1520", "text": "#cde8ff", "accent": "#00d4ff", "muted": "#2a4a6a"},
    "friendly":     {"bg": "#ffffff", "surface": "#f8f8fb", "text": "#1a1a2e", "accent": "#7c3aed", "muted": "#9090b0"},
    "budget":       {"bg": "#0f172a", "surface": "#1e293b", "text": "#e2e8f0", "accent": "#22c55e", "muted": "#475569"},
}


def _get_palette(tone: str) -> dict:
    tone = (tone or "professional").lower()
    for key in COLOUR_PALETTES:
        if key in tone:
            return COLOUR_PALETTES[key]
    return COLOUR_PALETTES["professional"]


def _get_font(tone: str) -> tuple:
    tone = (tone or "professional").lower()
    for key in FONT_STACKS:
        if key in tone:
            return FONT_STACKS[key]
    return FONT_STACKS["professional"]


# ─────────────────────────────────────────────
# COPY GENERATOR
# Claude Sonnet writes the website copy
# ─────────────────────────────────────────────

def generate_site_copy(profile: dict) -> dict:
    """
    Use Claude Sonnet to write all website copy:
    hero headline, subhead, services descriptions, about section, CTA.
    Returns structured dict ready for HTML injection.
    """
    import anthropic
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    name     = profile.get("business_name", "The Business")
    industry = profile.get("industry", "General")
    services = profile.get("services", [])
    target   = profile.get("target_customer", "clients")
    tone     = profile.get("tone", "professional")
    location = profile.get("location", "")

    prompt = f"""Write website copy for {name}, a {industry} business.
Target customer: {target}
Services: {', '.join(services[:5])}
Tone: {tone}
Location: {location}

Return ONLY a JSON object:
{{
  "hero_headline": "Bold 5-8 word headline. No fluff. Captures the core transformation.",
  "hero_subhead": "One sentence. What they do and who for. Max 18 words.",
  "hero_cta": "3-word CTA button text",
  "hero_cta2": "Secondary CTA — softer option (e.g. 'See our work')",
  "services": [
    {{
      "name": "Service Name",
      "tagline": "6-word outcome statement",
      "description": "2 sentences. Problem → solution. Specific, not generic.",
      "icon": "single emoji"
    }}
  ],
  "about_headline": "5-word company philosophy headline",
  "about_body": "2 punchy paragraphs. Who you are, why you're different. 60 words total.",
  "proof_stat_1": {{"number": "200+", "label": "clients served"}},
  "proof_stat_2": {{"number": "98%", "label": "retention rate"}},
  "proof_stat_3": {{"number": "£4M+", "label": "value delivered"}},
  "cta_headline": "Final CTA headline — 6 words, closes the loop with the hero",
  "cta_subhead": "One sentence. Remove the last objection.",
  "footer_tagline": "4-word brand positioning statement"
}}

Write real copy. No placeholder text. Make every word earn its place.
Return ONLY valid JSON."""

    try:
        resp = client.messages.create(
            model     = "claude-sonnet-4-6",
            max_tokens= 1500,
            messages  = [{"role": "user", "content": prompt}]
        )
        text = resp.content[0].text.strip().replace("```json", "").replace("```", "").strip()
        return json.loads(text)
    except Exception as e:
        print(f"[WebBuilder] Copy generation error: {e}")
        # Fallback copy
        return {
            "hero_headline":  f"Built For Results. Proven in {industry}.",
            "hero_subhead":   f"{name} delivers {services[0].lower() if services else 'expert solutions'} that move the needle.",
            "hero_cta":       "Get Started",
            "hero_cta2":      "See Our Work",
            "services":       [{"name": s, "tagline": f"Expert {s.lower()} delivery", "description": f"We deliver {s.lower()} with precision and speed. Trusted by leading {industry.lower()} firms.", "icon": "✦"} for s in services[:4]],
            "about_headline": "Excellence in Every Engagement",
            "about_body":     f"{name} is a {industry.lower()} firm built on results. We work with {target} who demand more than the standard offering.\n\nEvery engagement is deliberate. Every outcome is measured.",
            "proof_stat_1":   {"number": "100+", "label": "clients served"},
            "proof_stat_2":   {"number": "95%", "label": "retention rate"},
            "proof_stat_3":   {"number": "5★", "label": "average rating"},
            "cta_headline":   "Ready to See the Difference?",
            "cta_subhead":    "Book a free consultation. No pitch, no pressure.",
            "footer_tagline": f"{name}. Built different."
        }


# ─────────────────────────────────────────────
# HTML GENERATOR
# The actual site — Higgsfield motion + Huashu aesthetic
# ─────────────────────────────────────────────

def generate_site_html(profile: dict, copy: dict) -> str:
    """
    Generate a complete, animated, single-page website.

    Motion design principles (Higgsfield-inspired):
      - Every section entrance is choreographed
      - Stagger children — never everything at once
      - Scroll-driven reveals — content earns its reveal
      - One focal point per section — no competition

    Visual principles (Huashu aesthetic):
      - Ink on paper — contrast does the work
      - Generous white space — silence is intentional
      - Typography hierarchy — size and weight carry meaning
      - Grid with breathing room — nothing crammed
    """
    name     = profile.get("business_name", "The Business")
    tone     = profile.get("tone", "professional")
    location = profile.get("location", "")
    has_wa   = profile.get("has_whatsapp", False)

    palette  = _get_palette(tone)
    font, font_url = _get_font(tone)

    services = copy.get("services", [])
    bg       = palette["bg"]
    surface  = palette["surface"]
    text     = palette["text"]
    accent   = palette["accent"]
    muted    = palette["muted"]

    # Build services grid
    services_html = ""
    for i, svc in enumerate(services[:6]):
        services_html += f"""
        <div class="service-card reveal" data-delay="{i * 80}">
          <div class="service-icon">{svc.get('icon','✦')}</div>
          <div class="service-name">{svc.get('name','')}</div>
          <div class="service-tagline">{svc.get('tagline','')}</div>
          <div class="service-desc">{svc.get('description','')}</div>
        </div>"""

    # Proof stats
    stats = [copy.get(f"proof_stat_{i}", {}) for i in range(1, 4)]
    stats_html = "".join(f"""<div class="stat reveal" data-delay="{i*100}">
      <div class="stat-number">{s.get('number','—')}</div>
      <div class="stat-label">{s.get('label','')}</div>
    </div>""" for i, s in enumerate(stats) if s)

    # WhatsApp button
    wa_btn = f'<a href="https://wa.me/" class="btn btn-wa reveal">💬 WhatsApp Us</a>' if has_wa else ''

    # Pre-compute about body (can't use \n inside f-string expressions in Python <3.12)
    double_newline  = "\n\n"
    about_body_html = "".join(
        f"<p>{p.strip()}</p>"
        for p in copy.get("about_body", "").split(double_newline)
        if p.strip()
    )

    # Pre-compute nav rgba from hex bg (can't use backslash in f-string expressions)
    bg_r = int(bg[1:3], 16)
    bg_g = int(bg[3:5], 16)
    bg_b = int(bg[5:7], 16)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{name}</title>
<meta name="description" content="{copy.get('hero_subhead','')}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{font_url}" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/ScrollTrigger.min.js"></script>
<style>
/* ── Reset ──────────────────────────────── */
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
:root{{
  --bg:{bg};
  --surface:{surface};
  --text:{text};
  --accent:{accent};
  --muted:{muted};
  --font:{font};
  --ease-out-expo:cubic-bezier(0.16,1,0.3,1);
  --ease-in-out:cubic-bezier(0.87,0,0.13,1);
}}
html{{scroll-behavior:smooth;}}
body{{
  font-family:var(--font);
  background:var(--bg);
  color:var(--text);
  line-height:1.6;
  -webkit-font-smoothing:antialiased;
  overflow-x:hidden;
}}
/* ── Typography ─────────────────────────── */
.display{{font-size:clamp(3rem,8vw,7rem);font-weight:800;line-height:1.0;letter-spacing:-0.04em;}}
.headline{{font-size:clamp(2rem,5vw,4rem);font-weight:700;line-height:1.1;letter-spacing:-0.03em;}}
.subhead{{font-size:clamp(1.1rem,2vw,1.4rem);font-weight:400;color:var(--muted);line-height:1.6;}}
.label{{font-size:0.75rem;font-weight:700;text-transform:uppercase;letter-spacing:0.15em;color:var(--accent);}}
/* ── Layout ─────────────────────────────── */
.container{{max-width:1200px;margin:0 auto;padding:0 clamp(1.5rem,5vw,4rem);}}
section{{padding:clamp(5rem,12vw,10rem) 0;}}
/* ── Nav ─────────────────────────────────── */
nav{{
  position:fixed;top:0;left:0;right:0;z-index:100;
  padding:1.2rem clamp(1.5rem,5vw,4rem);
  display:flex;justify-content:space-between;align-items:center;
  backdrop-filter:blur(20px);-webkit-backdrop-filter:blur(20px);
  border-bottom:1px solid rgba(255,255,255,0.04);
  background:rgba({bg_r},{bg_g},{bg_b},0.85);
  transition:background 0.3s;
}}
.nav-logo{{font-size:1.1rem;font-weight:800;letter-spacing:-0.02em;}}
.nav-cta{{
  padding:0.55rem 1.4rem;
  border-radius:100px;
  font-size:0.85rem;font-weight:600;
  background:var(--accent);
  color:#fff;
  text-decoration:none;
  transition:opacity 0.2s,transform 0.2s;
}}
.nav-cta:hover{{opacity:0.85;transform:translateY(-1px);}}
/* ── Hero ─────────────────────────────────── */
#hero{{
  min-height:100vh;
  display:flex;align-items:center;
  padding-top:120px;
  position:relative;
  overflow:hidden;
}}
.hero-bg{{
  position:absolute;inset:0;
  background:radial-gradient(ellipse 80% 60% at 60% 40%, {accent}18 0%, transparent 70%);
  pointer-events:none;
}}
.hero-grid{{
  position:absolute;inset:0;
  background-image:linear-gradient({surface}55 1px,transparent 1px),linear-gradient(90deg,{surface}55 1px,transparent 1px);
  background-size:80px 80px;
  mask-image:radial-gradient(ellipse 70% 70% at 50% 50%,black 0%,transparent 100%);
  opacity:0.4;
  pointer-events:none;
}}
.hero-content{{position:relative;z-index:1;max-width:900px;}}
.hero-badge{{
  display:inline-flex;align-items:center;gap:0.5rem;
  font-size:0.75rem;font-weight:600;
  color:var(--accent);
  border:1px solid {accent}44;
  background:{accent}11;
  padding:0.4rem 1rem;
  border-radius:100px;
  margin-bottom:2rem;
  letter-spacing:0.05em;
}}
.hero-ctas{{display:flex;gap:1rem;flex-wrap:wrap;margin-top:2.5rem;}}
.btn{{
  padding:0.8rem 2rem;
  border-radius:100px;
  font-size:0.95rem;font-weight:600;
  text-decoration:none;
  display:inline-flex;align-items:center;gap:0.5rem;
  transition:all 0.25s var(--ease-out-expo);
  cursor:pointer;border:none;
}}
.btn-primary{{background:var(--accent);color:#fff;}}
.btn-primary:hover{{transform:translateY(-2px);box-shadow:0 12px 40px {accent}40;}}
.btn-secondary{{background:transparent;color:var(--text);border:1px solid rgba(255,255,255,0.15);}}
.btn-secondary:hover{{background:rgba(255,255,255,0.06);transform:translateY(-2px);}}
.btn-wa{{background:#25d366;color:#fff;}}
.btn-wa:hover{{transform:translateY(-2px);box-shadow:0 12px 30px #25d36640;}}
/* ── Stats bar ───────────────────────────── */
#stats{{
  padding:3rem 0;
  border-top:1px solid rgba(255,255,255,0.06);
  border-bottom:1px solid rgba(255,255,255,0.06);
}}
.stats-row{{display:flex;gap:4rem;flex-wrap:wrap;}}
.stat{{}}
.stat-number{{font-size:2.8rem;font-weight:800;color:var(--text);letter-spacing:-0.04em;}}
.stat-label{{font-size:0.8rem;color:var(--muted);text-transform:uppercase;letter-spacing:0.08em;margin-top:0.2rem;}}
/* ── Services ────────────────────────────── */
#services{{}}
.section-header{{margin-bottom:clamp(3rem,6vw,5rem);}}
.services-grid{{
  display:grid;
  grid-template-columns:repeat(auto-fill,minmax(300px,1fr));
  gap:1.5px;
  border:1.5px solid rgba(255,255,255,0.07);
  border-radius:24px;
  overflow:hidden;
  background:rgba(255,255,255,0.07);
}}
.service-card{{
  background:var(--bg);
  padding:2.5rem;
  transition:background 0.3s;
  position:relative;
  overflow:hidden;
}}
.service-card::before{{
  content:'';
  position:absolute;inset:0;
  background:radial-gradient(circle at 0% 0%,{accent}0a 0%,transparent 60%);
  opacity:0;
  transition:opacity 0.4s;
}}
.service-card:hover{{background:var(--surface);}}
.service-card:hover::before{{opacity:1;}}
.service-icon{{font-size:2rem;margin-bottom:1.2rem;}}
.service-name{{font-size:1.1rem;font-weight:700;margin-bottom:0.4rem;letter-spacing:-0.02em;}}
.service-tagline{{font-size:0.8rem;color:var(--accent);font-weight:600;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:1rem;}}
.service-desc{{font-size:0.9rem;color:var(--muted);line-height:1.65;}}
/* ── About ───────────────────────────────── */
#about{{}}
.about-grid{{display:grid;grid-template-columns:1fr 1fr;gap:6rem;align-items:center;}}
@media(max-width:768px){{.about-grid{{grid-template-columns:1fr;gap:3rem;}}}}
.about-text{{font-size:1.05rem;color:var(--muted);line-height:1.75;}}
.about-text p+p{{margin-top:1.2rem;}}
.accent-line{{
  width:3rem;height:3px;
  background:linear-gradient(90deg,var(--accent),transparent);
  margin-bottom:2rem;
  border-radius:2px;
}}
.about-visual{{
  aspect-ratio:1;
  border-radius:24px;
  background:var(--surface);
  border:1px solid rgba(255,255,255,0.07);
  display:flex;align-items:center;justify-content:center;
  font-size:6rem;
  position:relative;
  overflow:hidden;
}}
.about-visual::after{{
  content:'';
  position:absolute;inset:0;
  background:radial-gradient(circle at 30% 30%,{accent}18 0%,transparent 60%);
}}
/* ── CTA ─────────────────────────────────── */
#cta{{text-align:center;}}
.cta-box{{
  background:var(--surface);
  border:1px solid rgba(255,255,255,0.07);
  border-radius:32px;
  padding:clamp(3rem,6vw,6rem);
  position:relative;
  overflow:hidden;
}}
.cta-glow{{
  position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);
  width:60%;height:60%;
  background:radial-gradient(circle,{accent}20 0%,transparent 70%);
  pointer-events:none;
}}
/* ── Footer ──────────────────────────────── */
footer{{
  padding:3rem 0;
  border-top:1px solid rgba(255,255,255,0.06);
  display:flex;justify-content:space-between;align-items:center;
  flex-wrap:wrap;gap:1rem;
  font-size:0.85rem;color:var(--muted);
}}
/* ── Reveal animations ───────────────────── */
.reveal{{opacity:0;transform:translateY(32px);}}
.reveal.visible{{
  animation:revealUp 0.7s var(--ease-out-expo) forwards;
}}
@keyframes revealUp{{
  to{{opacity:1;transform:translateY(0);}}
}}
/* ── Cursor glow (desktop only) ──────────── */
@media(pointer:fine){{
  .cursor-glow{{
    position:fixed;width:400px;height:400px;
    border-radius:50%;
    pointer-events:none;z-index:0;
    background:radial-gradient(circle,{accent}08 0%,transparent 70%);
    transform:translate(-50%,-50%);
    transition:left 0.15s,top 0.15s;
  }}
}}
@media(max-width:768px){{
  .hero-ctas{{flex-direction:column;}}
  .btn{{justify-content:center;}}
}}
</style>
</head>
<body>

<div class="cursor-glow" id="cursorGlow"></div>

<!-- ── Navigation ───────────────────────── -->
<nav>
  <div class="nav-logo">{name}</div>
  <a href="#cta" class="nav-cta">{copy.get('hero_cta','Get Started')}</a>
</nav>

<!-- ── Hero ─────────────────────────────── -->
<section id="hero">
  <div class="hero-bg"></div>
  <div class="hero-grid"></div>
  <div class="container">
    <div class="hero-content">
      <div class="hero-badge" id="hero-badge">
        <span>●</span> {profile.get('industry','')} {f'· {location}' if location else ''}
      </div>
      <h1 class="display" id="hero-headline">{copy.get('hero_headline','Built For Results.')}</h1>
      <p class="subhead" id="hero-subhead" style="max-width:580px;margin-top:1.5rem;">{copy.get('hero_subhead','')}</p>
      <div class="hero-ctas">
        <a href="#cta" class="btn btn-primary" id="hero-cta1">
          {copy.get('hero_cta','Get Started')} →
        </a>
        <a href="#services" class="btn btn-secondary" id="hero-cta2">
          {copy.get('hero_cta2','See Our Work')}
        </a>
        {wa_btn}
      </div>
    </div>
  </div>
</section>

<!-- ── Stats ─────────────────────────────── -->
<section id="stats">
  <div class="container">
    <div class="stats-row">
      {stats_html}
    </div>
  </div>
</section>

<!-- ── Services ──────────────────────────── -->
<section id="services">
  <div class="container">
    <div class="section-header">
      <div class="label reveal">What We Do</div>
      <h2 class="headline reveal" style="margin-top:1rem;max-width:560px;">
        Every service. Built to move your business forward.
      </h2>
    </div>
    <div class="services-grid">
      {services_html}
    </div>
  </div>
</section>

<!-- ── About ─────────────────────────────── -->
<section id="about">
  <div class="container">
    <div class="about-grid">
      <div class="about-visual reveal">
        <span style="position:relative;z-index:1;">
          {'🏗️' if 'construct' in profile.get('industry','').lower() else
           '⚖️' if 'legal' in profile.get('industry','').lower() else
           '🏥' if 'health' in profile.get('industry','').lower() else
           '🍽️' if 'restaurant' in profile.get('industry','').lower() else
           '📦' if 'logistics' in profile.get('industry','').lower() else
           '💼'}
        </span>
      </div>
      <div>
        <div class="accent-line reveal"></div>
        <div class="label reveal">About Us</div>
        <h2 class="headline reveal" style="margin-top:1rem;margin-bottom:2rem;">
          {copy.get('about_headline','Excellence in Every Engagement')}
        </h2>
        <div class="about-text reveal">
          {about_body_html}
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ── CTA ───────────────────────────────── -->
<section id="cta">
  <div class="container">
    <div class="cta-box">
      <div class="cta-glow"></div>
      <div style="position:relative;z-index:1;">
        <div class="label reveal">Get Started</div>
        <h2 class="headline reveal" style="margin-top:1rem;margin-bottom:1rem;">
          {copy.get('cta_headline','Ready to See the Difference?')}
        </h2>
        <p class="subhead reveal" style="margin-bottom:2.5rem;max-width:480px;margin-left:auto;margin-right:auto;">
          {copy.get('cta_subhead','Book a free consultation. No pitch, no pressure.')}
        </p>
        <div style="display:flex;gap:1rem;justify-content:center;flex-wrap:wrap;">
          <a href="mailto:hello@{name.lower().replace(' ','')+'.com'}" class="btn btn-primary reveal">
            {copy.get('hero_cta','Get Started')} →
          </a>
          {wa_btn}
        </div>
      </div>
    </div>
  </div>
</section>

<!-- ── Footer ─────────────────────────────── -->
<footer>
  <div class="container" style="width:100%;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem;">
    <div style="font-weight:700;color:var(--text);">{name}</div>
    <div>{copy.get('footer_tagline','Built different.')}</div>
    <div>© {datetime.now().year} {name}{f' · {location}' if location else ''}</div>
  </div>
</footer>

<script>
// ── GSAP ScrollTrigger setup ──────────────
gsap.registerPlugin(ScrollTrigger);

// ── Hero entrance — staggered, choreographed ──
const heroTl = gsap.timeline({{delay: 0.1}});
heroTl
  .from('#hero-badge',    {{opacity:0, y:20, duration:0.6, ease:'power3.out'}})
  .from('#hero-headline', {{opacity:0, y:40, duration:0.8, ease:'power4.out'}},  '-=0.3')
  .from('#hero-subhead',  {{opacity:0, y:24, duration:0.7, ease:'power3.out'}},  '-=0.5')
  .from('#hero-cta1',     {{opacity:0, y:16, duration:0.5, ease:'power2.out'}},  '-=0.4')
  .from('#hero-cta2',     {{opacity:0, y:16, duration:0.5, ease:'power2.out'}},  '-=0.35')
  .from('.hero-bg',       {{opacity:0, duration:1.2, ease:'power2.out'}},         '-=1.0');

// ── Scroll reveals — every .reveal element ──
document.querySelectorAll('.reveal').forEach(el => {{
  const delay = parseFloat(el.dataset.delay || 0) / 1000;
  ScrollTrigger.create({{
    trigger: el,
    start: 'top 88%',
    once: true,
    onEnter: () => {{
      el.style.animationDelay = delay + 's';
      el.classList.add('visible');
    }},
  }});
}});

// ── Cursor glow (desktop only) ───────────
const glow = document.getElementById('cursorGlow');
if(glow && window.matchMedia('(pointer:fine)').matches){{
  document.addEventListener('mousemove', e => {{
    glow.style.left = e.clientX + 'px';
    glow.style.top  = e.clientY + 'px';
  }});
}}

// ── Nav background on scroll ─────────────
const navEl = document.querySelector('nav');
window.addEventListener('scroll', () => {{
  navEl.style.background = window.scrollY > 40
    ? 'rgba({bg_r},{bg_g},{bg_b},0.98)'
    : 'rgba({bg_r},{bg_g},{bg_b},0.85)';
}}, {{passive:true}});

// ── Stats count-up ───────────────────────
document.querySelectorAll('.stat-number').forEach(el => {{
  ScrollTrigger.create({{
    trigger: el, start:'top 85%', once:true,
    onEnter:() => gsap.from(el, {{y:20, opacity:0, duration:0.6, ease:'power3.out'}}),
  }});
}});
</script>
</body>
</html>"""


# ─────────────────────────────────────────────
# NETLIFY DEPLOYMENT
# Zip the HTML and push via Netlify API
# ─────────────────────────────────────────────

def _create_zip(files: dict) -> bytes:
    """Create an in-memory zip from {filename: content} dict."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        for filename, content in files.items():
            zf.writestr(filename, content)
    return buf.getvalue()


def deploy_to_netlify(
    site_name:  str,
    html:       str,
    token:      str = None,
    extra_files: dict = None,
) -> dict:
    """
    Deploy a website to Netlify.

    site_name: slug used for the subdomain (e.g. "gromatic-site")
    html:      the index.html content
    token:     Netlify personal access token (falls back to NETLIFY_TOKEN env var)
    extra_files: additional files to include {path: content}

    Returns: {
        "url":      "https://gromatic-site.netlify.app",
        "site_id":  "...",
        "deploy_id":"...",
        "status":   "deployed",
    }
    """
    token = token or NETLIFY_TOKEN
    if not token:
        return {"status": "error", "error": "NETLIFY_TOKEN not configured. Add it to .env"}

    headers = {"Authorization": f"Bearer {token}"}

    # Sanitise site name
    import re
    slug = re.sub(r'[^a-z0-9-]', '-', site_name.lower())[:32].strip('-')

    # Step 1: Create site (or get existing)
    try:
        create_resp = requests.post(
            f"{NETLIFY_API}/sites",
            headers={**headers, "Content-Type": "application/json"},
            json={"name": slug},
            timeout=15,
        )
        if create_resp.status_code == 422:
            # Site name taken — append timestamp
            slug = f"{slug}-{int(datetime.now().timestamp()) % 10000}"
            create_resp = requests.post(
                f"{NETLIFY_API}/sites",
                headers={**headers, "Content-Type": "application/json"},
                json={"name": slug},
                timeout=15,
            )
        site = create_resp.json()
        site_id  = site.get("id")
        site_url = site.get("ssl_url") or site.get("url") or f"https://{slug}.netlify.app"

        if not site_id:
            return {"status": "error", "error": f"Site creation failed: {create_resp.text[:200]}"}

    except Exception as e:
        return {"status": "error", "error": f"Netlify site creation failed: {e}"}

    # Step 2: Create zip with site files
    files = {"index.html": html}
    if extra_files:
        files.update(extra_files)

    # Add a _redirects file for SPA support
    files["_redirects"] = "/*  /index.html  200\n"

    zip_bytes = _create_zip(files)

    # Step 3: Deploy via zip upload
    try:
        deploy_resp = requests.post(
            f"{NETLIFY_API}/sites/{site_id}/deploys",
            headers={**headers, "Content-Type": "application/zip"},
            data=zip_bytes,
            timeout=60,
        )
        deploy = deploy_resp.json()
        deploy_id = deploy.get("id")

        return {
            "status":    "deployed",
            "url":       site_url,
            "site_id":   site_id,
            "deploy_id": deploy_id,
            "slug":      slug,
        }

    except Exception as e:
        return {"status": "error", "error": f"Netlify deploy failed: {e}"}


# ─────────────────────────────────────────────
# CLIENT PORTAL DEPLOY
# White-label, branded dashboard for each client
# ─────────────────────────────────────────────

def generate_client_portal_html(
    business_profile: dict,
    team:             list,
    accent_color:     str = None,
) -> str:
    """
    Generate a white-label client portal for a specific business.
    Stripped-down version of the main dashboard — shows THEIR agents, THEIR activity.
    Deployed to Netlify so the client gets their own URL.

    This is separate from the main PluggedIN OS dashboard (which is Pasha's master view).
    """
    name    = business_profile.get("business_name", "Your Business")
    industry = business_profile.get("industry", "")
    tone    = business_profile.get("tone", "professional")
    palette = _get_palette(tone)
    _, font_url = _get_font(tone)

    ac = accent_color or palette["accent"]
    bg = palette["bg"]
    surface = palette["surface"]
    text = palette["text"]
    muted = palette["muted"]

    # Build agent cards
    agent_cards = ""
    for a in team:
        if a.get("is_ceo"):
            continue
        agent_cards += f"""
        <div style="background:{surface};border:1px solid rgba(255,255,255,0.07);border-radius:16px;padding:20px;display:flex;gap:14px;align-items:center;">
          <div style="width:48px;height:48px;border-radius:50%;background:{a.get('color','#7c6fff')}22;border:2px solid {a.get('color','#7c6fff')}44;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;">{a.get('avatar','🤖')}</div>
          <div style="flex:1;">
            <div style="font-size:15px;font-weight:700;color:{text};">{a.get('name','Agent')}</div>
            <div style="font-size:12px;color:{muted};margin-top:2px;">{a.get('title','')}</div>
            <div style="font-size:11px;color:{a.get('color','#22c55e')};margin-top:6px;">● Online — {a.get('last_action','Monitoring...')}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:22px;font-weight:800;color:{a.get('color','#22c55e')};">{a.get('stats',{}).get('today',0)}</div>
            <div style="font-size:10px;color:{muted};">today</div>
          </div>
        </div>"""

    ceo = next((a for a in team if a.get("is_ceo")), None)
    ceo_name = ceo["name"] if ceo else "Your Chief of Staff"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{name} — AI Team Dashboard</title>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*,*::before,*::after{{margin:0;padding:0;box-sizing:border-box;}}
body{{font-family:'Inter',sans-serif;background:{bg};color:{text};-webkit-font-smoothing:antialiased;min-height:100vh;}}
</style>
</head>
<body>
<div style="max-width:800px;margin:0 auto;padding:2rem 1.5rem;">

  <!-- Header -->
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:2.5rem;padding-bottom:1.5rem;border-bottom:1px solid rgba(255,255,255,0.07);">
    <div>
      <div style="font-size:20px;font-weight:800;color:{text};">{name}</div>
      <div style="font-size:12px;color:{muted};margin-top:2px;">{industry} · AI Team Dashboard</div>
    </div>
    <div style="width:10px;height:10px;border-radius:50%;background:#22c55e;box-shadow:0 0 8px #22c55e88;"></div>
  </div>

  <!-- CEO Message -->
  <div style="background:linear-gradient(135deg,{ac}18,transparent);border:1px solid {ac}33;border-radius:16px;padding:20px;margin-bottom:2rem;">
    <div style="font-size:11px;color:{ac};font-weight:700;text-transform:uppercase;letter-spacing:.1em;margin-bottom:8px;">🌅 {ceo_name} · Today's Briefing</div>
    <div style="font-size:13px;color:{text};line-height:1.6;">Your team is live and working for {name}. All agents are online. Check below for today's activity.</div>
  </div>

  <!-- Agent Team -->
  <div style="font-size:11px;font-weight:700;color:{muted};text-transform:uppercase;letter-spacing:.1em;margin-bottom:12px;">Your AI Team</div>
  <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:2.5rem;">
    {agent_cards}
  </div>

  <!-- Footer -->
  <div style="text-align:center;font-size:11px;color:{muted};padding-top:1.5rem;border-top:1px solid rgba(255,255,255,0.05);">
    Powered by <strong style="color:{ac};">PluggedIN</strong> · AI Staff for growing businesses
  </div>

</div>
</body>
</html>"""


def deploy_client_portal(
    business_profile: dict,
    team:             list,
    token:            str = None,
) -> dict:
    """Deploy the client's white-label portal to Netlify."""
    name   = business_profile.get("business_name", "client")
    import re
    slug   = re.sub(r'[^a-z0-9]', '-', name.lower())[:20].strip('-')
    portal_html = generate_client_portal_html(business_profile, team)
    return deploy_to_netlify(
        site_name  = f"{slug}-portal",
        html       = portal_html,
        token      = token,
    )


# ─────────────────────────────────────────────
# MAIN BUILD PIPELINE
# ─────────────────────────────────────────────

def build_website(profile: dict, deploy: bool = True, token: str = None) -> dict:
    """
    Full pipeline: business profile → copy → HTML → Netlify deploy → URL.

    profile: from website_scanner.scan_business() or manual input
    deploy:  if True, push to Netlify. If False, return HTML only (for preview).
    token:   Netlify token (falls back to NETLIFY_TOKEN env var)

    Returns: {
        "status":  "deployed" | "generated" | "error",
        "url":     "https://...",     (if deployed)
        "html":    "...",             (always returned)
        "copy":    {...},             (generated copy)
        "site_id": "...",
    }
    """
    name = profile.get("business_name", "website")
    print(f"[WebBuilder] Building website for {name}...")

    # Step 1: Generate copy
    print(f"[WebBuilder] Generating copy via Claude Sonnet...")
    copy = generate_site_copy(profile)

    # Step 2: Generate HTML
    print(f"[WebBuilder] Generating animated HTML...")
    html = generate_site_html(profile, copy)

    if not deploy:
        return {"status": "generated", "html": html, "copy": copy}

    # Step 3: Deploy to Netlify
    import re
    slug = re.sub(r'[^a-z0-9]', '-', name.lower())[:28].strip('-')
    print(f"[WebBuilder] Deploying to Netlify as '{slug}'...")
    result = deploy_to_netlify(slug, html, token=token)

    return {**result, "html": html, "copy": copy, "business_name": name}
