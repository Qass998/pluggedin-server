"""
lib/job_hunter.py — PluggedIN M12 Job Hunter Agent
====================================================
Scrapes job listings from Indeed, Reed, LinkedIn Jobs, Totaljobs,
and Glassdoor. Analyses each listing for employer signals — the real
reasons they're hiring, the pain points behind the job spec, the
keywords that matter. Then generates a tailored CV and cover letter
per job using Claude, mirroring the employer's own language.

Usage:
    from lib.job_hunter import JobHunter

    hunter = JobHunter()

    # Run a full search and generate CVs
    results = hunter.run(
        keywords="AI consultant",
        location="London",
        salary_min=60000,
        max_jobs=20,
    )

    # Get just the top matches with tailored CVs
    for job in results["top_matches"]:
        print(job["tailored_cv"])

    # Or run from CLI:
    # python3 lib/job_hunter.py --keywords "AI consultant" --location "London"
"""

import os
import json
import time
import logging
import re
from datetime import datetime, timezone
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
log = logging.getLogger("job_hunter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ─── Optional deps ─────────────────────────────────────────────────────────────
try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False

try:
    import requests as _req
    _REQUESTS_AVAILABLE = True
except ImportError:
    _REQUESTS_AVAILABLE = False


# ─────────────────────────────────────────────────────────────────────────────
# BASE PROFILE — the candidate's background
# Customise this per user. Stored in Airtable (Base Profile table) or here.
# ─────────────────────────────────────────────────────────────────────────────

BASE_PROFILE = {
    "name":        os.getenv("CANDIDATE_NAME",    "Pasha Abdul-Karim"),
    "email":       os.getenv("CANDIDATE_EMAIL",   "abdulkarimqassim@gmail.com"),
    "phone":       os.getenv("CANDIDATE_PHONE",   "+44 7XXX XXX XXX"),
    "location":    os.getenv("CANDIDATE_LOCATION","London, UK"),
    "linkedin":    os.getenv("CANDIDATE_LINKEDIN",""),
    "website":     os.getenv("CANDIDATE_WEBSITE", ""),

    "headline": (
        "AI Agency Founder & Systems Builder — I build agentic business operating "
        "systems for SMEs that automate lead generation, customer retention, and "
        "revenue intelligence using AI."
    ),

    "core_skills": [
        "Agentic AI systems (Claude, VAPI, Apify, Airtable)",
        "Multi-tenant SaaS architecture",
        "Business process automation",
        "Voice AI & conversational agents",
        "Lead generation pipelines",
        "CRM design and implementation",
        "Client onboarding and retention systems",
        "Python, JavaScript, FastAPI",
        "Prompt engineering & LLM orchestration",
        "SME digital transformation consulting",
    ],

    "experience": [
        {
            "title":    "Founder & CEO",
            "company":  "PluggedIN",
            "dates":    "2024 – Present",
            "bullets": [
                "Built a multi-tenant AI agency OS managing M1–M12 agent modules across SME clients",
                "Designed CEO Agent hierarchy: per-client AI orchestrators reporting to a Master CEO Agent",
                "Deployed VAPI voice agents that handle 24/7 inbound calls and book appointments automatically",
                "Created agentic client portals with live advisory engine, growth checkpoints, and Remotion video briefings",
                "Grew MRR through automated lead prospecting, redesign audits, and cold outreach systems",
            ],
        },
        {
            "title":    "AI Systems Consultant",
            "company":  "Freelance",
            "dates":    "2022 – 2024",
            "bullets": [
                "Delivered CRM, pipeline, and automation systems for legal, construction, and hospitality clients",
                "Built Airtable-based business intelligence dashboards integrated with third-party APIs",
                "Designed and deployed WhatsApp retention campaigns reducing churn by 30%+",
                "Automated competitor monitoring and review management for multi-site businesses",
            ],
        },
    ],

    "education": [
        {
            "degree":  "BSc Computer Science",
            "school":  "University of [X]",
            "dates":   "2019 – 2022",
        }
    ],

    "achievements": [
        "Deployed AI agent that answers 200+ calls/month for a London solicitors firm — zero missed enquiries",
        "Built a review improvement campaign that lifted a restaurant from 3.8★ to 4.6★ in 90 days",
        "Grew PluggedIN from 0 to £X,XXX MRR in first 6 months using own prospecting agents",
    ],
}


# ─────────────────────────────────────────────────────────────────────────────
# PLATFORMS
# ─────────────────────────────────────────────────────────────────────────────

PLATFORMS = {
    "indeed":    {"apify_actor": "misceres/indeed-scraper",     "enabled": True},
    "reed":      {"apify_actor": "misceres/reed-scraper",       "enabled": True},
    "linkedin":  {"apify_actor": "curious_coder/linkedin-jobs-scraper", "enabled": True},
    "totaljobs": {"apify_actor": "misceres/totaljobs-scraper",  "enabled": False},  # enable when needed
    "glassdoor": {"apify_actor": "misceres/glassdoor-jobs-scraper", "enabled": False},
}

# Fallback: search via Apify's general web scraper when platform actor not found
FALLBACK_ACTOR = "apify/web-scraper"


# ─────────────────────────────────────────────────────────────────────────────
# JOB HUNTER
# ─────────────────────────────────────────────────────────────────────────────

class JobHunter:
    """
    M12 — Job Hunter Agent.
    Scrapes job listings, scores them, analyses employer signals,
    and generates a tailored CV + cover letter for each top match.
    """

    MODEL = "claude-sonnet-4-6"

    def __init__(self):
        self.anthropic_key   = os.getenv("ANTHROPIC_API_KEY", "")
        self.apify_token     = os.getenv("APIFY_TOKEN", "")
        self.airtable_token  = os.getenv("AIRTABLE_TOKEN", "")
        self.airtable_base   = os.getenv("AIRTABLE_BASE_PLUGGEDIN", "")
        self._claude         = None

    @property
    def claude(self):
        if self._claude is None and _ANTHROPIC_AVAILABLE and self.anthropic_key:
            self._claude = anthropic.Anthropic(api_key=self.anthropic_key)
        return self._claude

    # ─── Main entry point ─────────────────────────────────────────────────

    def run(
        self,
        keywords:    str,
        location:    str  = "United Kingdom",
        salary_min:  int  = 0,
        job_type:    str  = "any",      # "full-time" | "contract" | "remote" | "any"
        max_jobs:    int  = 30,
        top_n:       int  = 5,
        platforms:   list = None,
    ) -> dict:
        """
        Full pipeline:
        1. Scrape all enabled platforms for matching jobs
        2. Deduplicate by title + company
        3. Score each job (match strength vs. base profile)
        4. Analyse top N for employer signals
        5. Generate tailored CV + cover letter for each top match
        6. Save everything to Airtable
        7. Return structured results
        """
        log.info(f"Job Hunter running — '{keywords}' in {location}")

        platforms = platforms or [k for k,v in PLATFORMS.items() if v["enabled"]]

        # 1. Scrape
        raw_jobs = []
        for platform in platforms:
            log.info(f"Scraping {platform}...")
            jobs = self._scrape(platform, keywords, location, salary_min, job_type)
            log.info(f"  → {len(jobs)} listings from {platform}")
            raw_jobs.extend(jobs)

        if not raw_jobs:
            log.warning("No jobs scraped. Check Apify token and platform actors.")
            raw_jobs = self._stub_jobs(keywords, location)  # demo data

        # 2. Deduplicate
        seen   = set()
        unique = []
        for j in raw_jobs:
            key = (j.get("title","").lower().strip(), j.get("company","").lower().strip())
            if key not in seen:
                seen.add(key)
                unique.append(j)
        log.info(f"Deduplicated: {len(raw_jobs)} → {len(unique)} unique listings")

        # 3. Score
        scored = [self._score_job(j) for j in unique[:max_jobs]]
        scored.sort(key=lambda x: x["match_score"], reverse=True)

        # 4 + 5. Analyse signals and generate CVs for top N
        top_matches = []
        for job in scored[:top_n]:
            log.info(f"Analysing + generating CV: {job['title']} @ {job['company']}")
            analysis   = self._analyse_signals(job)
            cv         = self._generate_cv(job, analysis)
            cover      = self._generate_cover_letter(job, analysis)
            top_matches.append({
                **job,
                "signals":        analysis,
                "tailored_cv":    cv,
                "cover_letter":   cover,
                "generated_at":   datetime.now(timezone.utc).isoformat(),
            })

        # 6. Save to Airtable
        for match in top_matches:
            self._save_to_airtable(match)

        result = {
            "query":          {"keywords": keywords, "location": location, "job_type": job_type},
            "total_found":    len(unique),
            "scored":         scored,
            "top_matches":    top_matches,
            "run_at":         datetime.now(timezone.utc).isoformat(),
        }

        log.info(f"Job Hunter complete — {len(unique)} listings, {len(top_matches)} CVs generated")
        return result

    # ─── Scraping ─────────────────────────────────────────────────────────

    def _scrape(self, platform: str, keywords: str, location: str, salary_min: int, job_type: str) -> list:
        """Scrape a single platform via Apify."""
        if not _REQUESTS_AVAILABLE or not self.apify_token:
            return []

        actor = PLATFORMS.get(platform, {}).get("apify_actor", FALLBACK_ACTOR)

        # Build platform-specific input
        actor_input = self._build_actor_input(platform, keywords, location, salary_min, job_type)

        try:
            # Start the Apify actor run
            run_url = f"https://api.apify.com/v2/acts/{actor}/runs"
            headers = {"Authorization": f"Bearer {self.apify_token}", "Content-Type": "application/json"}
            r = _req.post(run_url, headers=headers, json=actor_input, timeout=30)
            if r.status_code not in (200, 201):
                log.warning(f"{platform}: actor start failed ({r.status_code}) — {r.text[:200]}")
                return []

            run_id  = r.json()["data"]["id"]
            dataset = r.json()["data"].get("defaultDatasetId", "")

            # Poll until finished (max 120s)
            for _ in range(24):
                time.sleep(5)
                status_r = _req.get(f"https://api.apify.com/v2/actor-runs/{run_id}",
                                    headers=headers, timeout=15)
                status = status_r.json()["data"]["status"]
                if status in ("SUCCEEDED", "FAILED", "ABORTED"):
                    break

            if status != "SUCCEEDED":
                log.warning(f"{platform}: actor run ended with status {status}")
                return []

            # Fetch results
            items_r = _req.get(
                f"https://api.apify.com/v2/datasets/{dataset}/items?format=json&limit=100",
                headers=headers, timeout=30,
            )
            items = items_r.json() if isinstance(items_r.json(), list) else items_r.json().get("items", [])
            return [self._normalise(item, platform) for item in items]

        except Exception as e:
            log.error(f"{platform} scrape error: {e}")
            return []

    def _build_actor_input(self, platform: str, keywords: str, location: str, salary_min: int, job_type: str) -> dict:
        """Platform-specific Apify actor input."""
        base = {"maxItems": 50}
        if platform == "indeed":
            return {**base, "query": keywords, "location": location, "minSalary": salary_min or ""}
        elif platform == "reed":
            return {**base, "keywords": keywords, "location": location, "minimumSalary": salary_min}
        elif platform == "linkedin":
            return {**base, "keywords": keywords, "location": location,
                    "datePosted": "past-week", "jobType": job_type if job_type != "any" else ""}
        elif platform == "totaljobs":
            return {**base, "keywords": keywords, "location": location}
        elif platform == "glassdoor":
            return {**base, "query": keywords, "location": location}
        return {**base, "startUrls": [{"url": f"https://www.indeed.co.uk/jobs?q={keywords}&l={location}"}]}

    def _normalise(self, item: dict, platform: str) -> dict:
        """Normalise scraped item to a standard job dict."""
        return {
            "platform":    platform,
            "title":       item.get("title") or item.get("jobTitle") or item.get("positionName", ""),
            "company":     item.get("company") or item.get("companyName") or item.get("employer", ""),
            "location":    item.get("location") or item.get("jobLocation", ""),
            "salary":      item.get("salary") or item.get("salaryRange") or item.get("salaryText", ""),
            "description": item.get("description") or item.get("jobDescription") or item.get("summary", ""),
            "url":         item.get("url") or item.get("jobUrl") or item.get("externalApplyLink", ""),
            "posted":      item.get("postedAt") or item.get("date") or item.get("datePosted", ""),
            "job_type":    item.get("jobType") or item.get("contractType", ""),
            "raw":         item,
        }

    # ─── Demo / stub data (when Apify not available) ──────────────────────

    def _stub_jobs(self, keywords: str, location: str) -> list:
        """Return stub listings for offline testing."""
        return [
            {
                "platform": "indeed", "title": f"Senior {keywords}", "company": "TechCorp Ltd",
                "location": location, "salary": "£70,000 - £90,000",
                "description": f"We're looking for a senior {keywords} to join our fast-growing team. "
                               "You'll be responsible for designing and implementing AI systems, working closely "
                               "with our product and engineering teams. Experience with Python, LLMs, and "
                               "automation required. Startup mindset essential. Remote-friendly.",
                "url": "https://indeed.co.uk/job/example", "posted": "2 days ago", "job_type": "Full-time",
            },
            {
                "platform": "reed", "title": f"{keywords} Consultant", "company": "Digital Ventures Ltd",
                "location": location, "salary": "£55,000 - £75,000",
                "description": f"Exciting opportunity for an experienced {keywords} consultant. You will lead "
                               "client projects, building AI-powered business systems from scratch. "
                               "Strong client-facing skills and technical depth needed. "
                               "Experience with agentic AI, no-code tools, and CRM implementation preferred.",
                "url": "https://reed.co.uk/job/example", "posted": "1 day ago", "job_type": "Contract",
            },
            {
                "platform": "linkedin", "title": f"Head of AI Automation", "company": "GrowthBase",
                "location": location, "salary": "£85,000 + equity",
                "description": "GrowthBase is hiring a Head of AI Automation to own our internal AI stack. "
                               "You'll build agent workflows, integrate LLMs with our CRM and sales tools, "
                               "and train the wider team. We're scaling fast — this is a founding team role. "
                               "Python essential. Background in sales/marketing automation a huge plus.",
                "url": "https://linkedin.com/job/example", "posted": "3 days ago", "job_type": "Full-time",
            },
        ]

    # ─── Scoring ──────────────────────────────────────────────────────────

    def _score_job(self, job: dict) -> dict:
        """
        Score a job listing against the base profile.
        Returns job dict with added match_score (0–100) and match_reasons.
        """
        description = (job.get("description") or "").lower()
        title       = (job.get("title") or "").lower()
        score       = 0
        reasons     = []

        # Skill keyword matching
        skill_hits = 0
        for skill in BASE_PROFILE["core_skills"]:
            keywords = skill.lower().replace("(","").replace(")","").split()
            if any(kw in description or kw in title for kw in keywords if len(kw) > 3):
                skill_hits += 1
        skill_score = min(40, skill_hits * 5)
        score += skill_score
        if skill_hits >= 4:
            reasons.append(f"{skill_hits} core skills match the listing")

        # Seniority / title alignment
        senior_words = ["senior", "head of", "lead", "principal", "director", "founder", "consultant"]
        if any(w in title for w in senior_words):
            score += 15
            reasons.append("Seniority level aligns")

        # AI / automation keywords
        ai_words = ["ai", "artificial intelligence", "llm", "automation", "agent", "gpt", "claude",
                    "machine learning", "nlp", "agentic", "workflow"]
        ai_hits = sum(1 for w in ai_words if w in description)
        if ai_hits >= 3:
            score += 20
            reasons.append(f"Strong AI/automation focus ({ai_hits} signals)")
        elif ai_hits >= 1:
            score += 10
            reasons.append("Some AI focus")

        # Remote / flexible
        if any(w in description for w in ["remote", "hybrid", "flexible", "work from home"]):
            score += 10
            reasons.append("Remote/hybrid friendly")

        # Salary signal
        salary_text = (job.get("salary") or "").lower()
        if "£" in salary_text:
            nums = re.findall(r'\d[\d,]+', salary_text.replace(",",""))
            nums = [int(n) for n in nums if len(n) >= 5]
            if nums and max(nums) >= 60000:
                score += 15
                reasons.append(f"Strong salary signal (£{max(nums):,}+)")

        # Recency bonus
        posted = (job.get("posted") or "").lower()
        if "today" in posted or "hour" in posted:
            score += 5
        elif "1 day" in posted or "yesterday" in posted:
            score += 3

        job["match_score"]   = min(100, score)
        job["match_reasons"] = reasons
        return job

    # ─── Signal analysis ──────────────────────────────────────────────────

    def _analyse_signals(self, job: dict) -> dict:
        """
        Use Claude to read the job description and extract:
        - The real pain the employer is trying to solve
        - The top 5 skills/keywords to mirror in the CV
        - The hiring manager's likely concerns
        - Tone and culture signals
        - Best angle to position the candidate
        """
        description = job.get("description", "")
        if not description:
            return self._stub_signals(job)

        if not self.claude:
            return self._stub_signals(job)

        prompt = f"""You are an expert career coach and CV strategist.

Read this job listing and extract the employer's real signals.

JOB TITLE: {job.get('title','')}
COMPANY: {job.get('company','')}
DESCRIPTION:
{description[:3000]}

Extract:
1. PAIN_POINTS: The 2-3 real problems this employer is trying to solve by hiring (not the listed responsibilities — the underlying business pain)
2. MUST_HAVE_KEYWORDS: The 8-10 exact words/phrases from the listing the CV must mirror (ATS and hiring manager will scan for these)
3. NICE_TO_HAVE: 3-4 bonus signals that would tip the decision
4. CULTURE_SIGNALS: What kind of person/culture this company wants (startup energy, corporate, technical, commercial)
5. HIRING_CONCERN: The single biggest doubt the hiring manager will have about any candidate
6. POSITIONING_ANGLE: In one sentence, how this candidate should position themselves to land this role

Return ONLY valid JSON:
{{
  "pain_points": ["...", "...", "..."],
  "must_have_keywords": ["...", "...", "...", "...", "...", "...", "...", "..."],
  "nice_to_have": ["...", "...", "..."],
  "culture_signals": "...",
  "hiring_concern": "...",
  "positioning_angle": "..."
}}"""

        try:
            msg = self.claude.messages.create(
                model=self.MODEL,
                max_tokens=700,
                messages=[{"role": "user", "content": prompt}],
            )
            raw = msg.content[0].text.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
            return json.loads(raw.strip())
        except Exception as e:
            log.error(f"Signal analysis failed: {e}")
            return self._stub_signals(job)

    def _stub_signals(self, job: dict) -> dict:
        return {
            "pain_points": [
                "Needs someone who can build and ship AI systems without hand-holding",
                "Current team lacks the technical depth to implement automation",
            ],
            "must_have_keywords": ["AI", "automation", "Python", "LLM", "agent", "pipeline", "integration", "client-facing"],
            "nice_to_have": ["Startup experience", "VAPI or voice AI", "Airtable"],
            "culture_signals": "Fast-moving, outcome-oriented, values shipping over planning",
            "hiring_concern": "Can they actually build things independently or do they need constant direction?",
            "positioning_angle": "Position as a builder who has shipped production AI systems and grown revenue with them.",
        }

    # ─── CV generation ────────────────────────────────────────────────────

    def _generate_cv(self, job: dict, signals: dict) -> str:
        """
        Generate a tailored CV for this specific job.
        Mirrors the job listing's language. Leads with the most relevant experience.
        """
        if not self.claude:
            return self._stub_cv(job, signals)

        profile    = BASE_PROFILE
        experience = "\n".join([
            f"{e['title']} at {e['company']} ({e['dates']})\n" +
            "\n".join(f"  - {b}" for b in e["bullets"])
            for e in profile["experience"]
        ])
        achievements = "\n".join(f"- {a}" for a in profile["achievements"])

        prompt = f"""You are a professional CV writer. Write a tailored, ATS-optimised CV for this candidate applying to this job.

CANDIDATE PROFILE:
Name: {profile['name']}
Location: {profile['location']}
Headline: {profile['headline']}
Core skills: {', '.join(profile['core_skills'])}
Experience:
{experience}
Key achievements:
{achievements}

TARGET JOB:
Title: {job.get('title','')}
Company: {job.get('company','')}
Job description excerpt: {job.get('description','')[:1500]}

EMPLOYER SIGNALS (use these to tailor):
Must-have keywords to mirror: {', '.join(signals.get('must_have_keywords',[]))}
Positioning angle: {signals.get('positioning_angle','')}
Hiring concern to address: {signals.get('hiring_concern','')}
Culture: {signals.get('culture_signals','')}

RULES:
- Mirror the exact language and keywords from the job listing — ATS reads for these
- Lead the professional summary with the positioning angle
- Reorder bullet points so the most relevant experience appears first per role
- Quantify everything possible (£, %, numbers, timeframes)
- Address the hiring concern implicitly — don't mention it directly, just counter it with evidence
- Keep to 2 pages max
- No fluff. Every line earns its place.
- Format: plain text, clean sections, no tables or columns (ATS-friendly)

Write the complete CV now."""

        try:
            msg = self.claude.messages.create(
                model=self.MODEL,
                max_tokens=1800,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            log.error(f"CV generation failed: {e}")
            return self._stub_cv(job, signals)

    def _stub_cv(self, job: dict, signals: dict) -> str:
        p = BASE_PROFILE
        return f"""{p['name']}
{p['location']} | {p['email']} | {p['phone']}
{"─"*60}

PROFESSIONAL SUMMARY
{p['headline']}

{"─"*60}
CORE SKILLS
{chr(10).join('• ' + s for s in p['core_skills'])}

{"─"*60}
EXPERIENCE
{chr(10).join(
    f"{e['title']} | {e['company']} | {e['dates']}" + chr(10) +
    chr(10).join('  • ' + b for b in e['bullets'])
    for e in p['experience']
)}

{"─"*60}
KEY ACHIEVEMENTS
{chr(10).join('• ' + a for a in p['achievements'])}

{"─"*60}
[Tailored for: {job.get('title','')} at {job.get('company','')}]
[Connect Anthropic API for fully AI-tailored version]
"""

    # ─── Cover letter ─────────────────────────────────────────────────────

    def _generate_cover_letter(self, job: dict, signals: dict) -> str:
        """Generate a punchy, tailored cover letter. No generic openers."""
        if not self.claude:
            return "[Connect Anthropic API for tailored cover letter generation]"

        p = BASE_PROFILE
        prompt = f"""Write a cover letter for this job application. No generic openers ("I am writing to apply..."). Start with something specific that shows you've read the job and understood the real pain they're hiring for.

CANDIDATE: {p['name']} — {p['headline']}
JOB: {job.get('title','')} at {job.get('company','')}

EMPLOYER'S REAL PAIN: {', '.join(signals.get('pain_points',['solving complex AI problems']))}
POSITIONING ANGLE: {signals.get('positioning_angle','')}
HIRING CONCERN TO COUNTER: {signals.get('hiring_concern','')}

RULES:
- 3 short paragraphs max. Under 250 words.
- Paragraph 1: Hook — reference their specific pain/need, not your desire for a job
- Paragraph 2: Your most relevant proof — one specific, quantified result that speaks directly to their pain
- Paragraph 3: Brief close — why this role, what you'd do in the first 30 days
- End with a call to action, not "I look forward to hearing from you"
- No fluff. Write like someone confident, not someone begging.

Write the cover letter now."""

        try:
            msg = self.claude.messages.create(
                model=self.MODEL,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            return msg.content[0].text.strip()
        except Exception as e:
            log.error(f"Cover letter generation failed: {e}")
            return "[Cover letter generation failed — check API connection]"

    # ─── Airtable ─────────────────────────────────────────────────────────

    def _save_to_airtable(self, match: dict):
        """Save job match + CV to Airtable → Job Applications table."""
        if not _REQUESTS_AVAILABLE or not self.airtable_token or not self.airtable_base:
            return
        try:
            url     = f"https://api.airtable.com/v0/{self.airtable_base}/Job%20Applications"
            headers = {"Authorization": f"Bearer {self.airtable_token}", "Content-Type": "application/json"}
            payload = {
                "fields": {
                    "Job Title":     match.get("title", ""),
                    "Company":       match.get("company", ""),
                    "Platform":      match.get("platform", ""),
                    "Location":      match.get("location", ""),
                    "Salary":        match.get("salary", ""),
                    "URL":           match.get("url", ""),
                    "Match Score":   match.get("match_score", 0),
                    "Match Reasons": "\n".join(match.get("match_reasons", [])),
                    "Positioning":   match.get("signals", {}).get("positioning_angle", ""),
                    "CV":            match.get("tailored_cv", "")[:10000],    # Airtable text limit
                    "Cover Letter":  match.get("cover_letter", "")[:5000],
                    "Status":        "Generated",
                    "Generated At":  match.get("generated_at", ""),
                }
            }
            _req.post(url, headers=headers, json=payload, timeout=10)
        except Exception as e:
            log.warning(f"Airtable save failed: {e}")

    # ─── Quick search (no CV, just listings) ─────────────────────────────

    def search_only(self, keywords: str, location: str = "UK", max_jobs: int = 50) -> list:
        """Return scored job listings without generating CVs. Fast scan."""
        raw = []
        for platform, cfg in PLATFORMS.items():
            if not cfg["enabled"]:
                continue
            raw.extend(self._scrape(platform, keywords, location, 0, "any"))
        if not raw:
            raw = self._stub_jobs(keywords, location)
        scored = [self._score_job(j) for j in raw[:max_jobs]]
        return sorted(scored, key=lambda x: x["match_score"], reverse=True)


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="M12 Job Hunter Agent")
    parser.add_argument("--keywords",   default="AI consultant",  help="Job search keywords")
    parser.add_argument("--location",   default="London",         help="Location")
    parser.add_argument("--salary-min", default=0, type=int,      help="Minimum salary")
    parser.add_argument("--job-type",   default="any",            help="full-time | contract | remote | any")
    parser.add_argument("--max-jobs",   default=30, type=int,     help="Max listings to process")
    parser.add_argument("--top-n",      default=5,  type=int,     help="Top N to generate CVs for")
    parser.add_argument("--search-only",action="store_true",      help="Just list matches, no CV generation")
    args = parser.parse_args()

    hunter = JobHunter()

    if args.search_only:
        results = hunter.search_only(args.keywords, args.location, args.max_jobs)
        print(f"\n{'─'*60}")
        print(f"  Top matches for '{args.keywords}' in {args.location}")
        print(f"{'─'*60}\n")
        for j in results[:10]:
            print(f"  [{j['match_score']:>3}/100] {j['title']} @ {j['company']} ({j['platform']})")
            print(f"          {j['salary']} · {j['location']} · {j['posted']}")
            if j["match_reasons"]:
                print(f"          ✓ {' · '.join(j['match_reasons'])}")
            print()
    else:
        results = hunter.run(
            keywords   = args.keywords,
            location   = args.location,
            salary_min = args.salary_min,
            job_type   = args.job_type,
            max_jobs   = args.max_jobs,
            top_n      = args.top_n,
        )

        print(f"\n{'═'*60}")
        print(f"  Job Hunter Complete")
        print(f"{'═'*60}")
        print(f"  Found:    {results['total_found']} listings")
        print(f"  CVs made: {len(results['top_matches'])}")
        print(f"{'─'*60}\n")

        for i, match in enumerate(results["top_matches"], 1):
            print(f"  #{i} [{match['match_score']}/100] {match['title']} @ {match['company']}")
            print(f"      {match['salary']} · {match['location']}")
            print(f"      Angle: {match['signals'].get('positioning_angle','')}")
            print(f"      Saved to Airtable ✓" if match.get("generated_at") else "")
            print()

        # Print first CV in full
        if results["top_matches"]:
            top = results["top_matches"][0]
            print(f"\n{'═'*60}")
            print(f"  TAILORED CV — {top['title']} @ {top['company']}")
            print(f"{'═'*60}\n")
            print(top["tailored_cv"])
            print(f"\n{'─'*60}")
            print("  COVER LETTER")
            print(f"{'─'*60}\n")
            print(top["cover_letter"])
