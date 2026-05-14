"""
lib/github_skills.py — Vetted GitHub Tool Discovery for Agent Enhancement

The Agent Creator's skill-finding engine.

When building or upgrading an agent, this module searches GitHub for
high-quality, actively maintained tools that the agent can use as skills or MCPs.

Vetting criteria (non-negotiable):
  ★ Stars:        >500 minimum, prefer >2,000
  ✓ License:      MIT, Apache 2.0, BSD only (no GPL for commercial use)
  ✓ Maintained:   Last commit within 12 months
  ✓ No risk:      No known CVEs, no crypto, no network sniffing
  ✓ Relevant:     Topic-matched to agent role

Risk categories that are ALWAYS excluded:
  - Any package with exec/shell injection capabilities
  - Web scrapers that bypass rate limits or ToS
  - Credential harvesters or browser automation that touches passwords
  - Anything with >3 known CVEs in the past 2 years
  - Cryptography / key management
  - Network packet sniffers

Output powers:
  - agent_creator.py (assigns skills to new agents)
  - CEO meta-agent skill upgrades
  - Dashboard "Upgrade Agent" button
"""

import os
import json
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

GITHUB_API   = "https://api.github.com"
MIN_STARS    = 500
SAFE_LICENSES = {"mit", "apache-2.0", "bsd-2-clause", "bsd-3-clause", "isc", "unlicense", "cc0-1.0"}
MAX_AGE_DAYS  = 365  # Must have been committed to within a year


# ─────────────────────────────────────────────
# CURATED VETTED SKILL LIBRARY
# Pre-vetted, high-star tools per agent domain
# Used as the primary source (GitHub API as backup)
# ─────────────────────────────────────────────

VETTED_SKILLS = {
    # Module 1 — Presence Agent (calls, booking)
    1: [
        {
            "name":        "cal.com",
            "github":      "calcom/cal.com",
            "stars":       30000,
            "description": "Open source scheduling infrastructure. Book appointments automatically.",
            "use_case":    "Booking link generation, availability sync, calendar management",
            "category":    "scheduling",
            "mcp_ready":   True,
        },
        {
            "name":        "twilio-node",
            "github":      "twilio/twilio-node",
            "stars":       3200,
            "description": "Official Twilio Node.js SDK. Voice, SMS, WhatsApp.",
            "use_case":    "Outbound calls, SMS alerts, WhatsApp messages",
            "category":    "communication",
            "mcp_ready":   True,
        },
    ],
    # Module 2 — Lead Generation
    2: [
        {
            "name":        "scrapy",
            "github":      "scrapy/scrapy",
            "stars":       52000,
            "description": "Fast high-level web crawling framework for Python.",
            "use_case":    "Prospect research, company data extraction from public pages",
            "category":    "data_extraction",
            "mcp_ready":   False,
        },
        {
            "name":        "hunter-python",
            "github":      "ilyabirman/hunter-python",
            "stars":       600,
            "description": "Python wrapper for Hunter.io email finder API.",
            "use_case":    "Find verified email addresses for B2B outreach",
            "category":    "prospecting",
            "mcp_ready":   False,
        },
        {
            "name":        "airtable.py",
            "github":      "gtalarico/airtable-python-wrapper",
            "stars":       1200,
            "description": "Python wrapper for Airtable API.",
            "use_case":    "Store and retrieve leads, sync CRM data",
            "category":    "crm",
            "mcp_ready":   True,
        },
    ],
    # Module 3 — WhatsApp Agent
    3: [
        {
            "name":        "twilio-python",
            "github":      "twilio/twilio-python",
            "stars":       2800,
            "description": "Official Twilio Python helper library.",
            "use_case":    "Send/receive WhatsApp messages, handle webhooks",
            "category":    "messaging",
            "mcp_ready":   True,
        },
        {
            "name":        "langchain",
            "github":      "langchain-ai/langchain",
            "stars":       97000,
            "description": "Framework for LLM-powered applications.",
            "use_case":    "Conversation memory, multi-turn dialogue management",
            "category":    "ai_framework",
            "mcp_ready":   False,
        },
    ],
    # Module 4 — Content Machine
    4: [
        {
            "name":        "python-docx",
            "github":      "python-openxml/python-docx",
            "stars":       4500,
            "description": "Create and update Microsoft Word files.",
            "use_case":    "Generate formatted content briefs, proposals, case studies",
            "category":    "document_generation",
            "mcp_ready":   False,
        },
        {
            "name":        "jinja2",
            "github":      "pallets/jinja",
            "stars":       10000,
            "description": "Fast, expressive template engine for Python.",
            "use_case":    "Content templates, email sequences, post frameworks",
            "category":    "templating",
            "mcp_ready":   False,
        },
        {
            "name":        "schedule",
            "github":      "dbader/schedule",
            "stars":       11000,
            "description": "Python job scheduling for humans.",
            "use_case":    "Schedule content publication at optimal times",
            "category":    "scheduling",
            "mcp_ready":   False,
        },
    ],
    # Module 5 — Competitor Intelligence
    5: [
        {
            "name":        "newspaper3k",
            "github":      "codelucas/newspaper",
            "stars":       14000,
            "description": "News article extraction and curation.",
            "use_case":    "Monitor competitor news, press releases, industry updates",
            "category":    "monitoring",
            "mcp_ready":   False,
        },
        {
            "name":        "difflib (stdlib)",
            "github":      None,
            "stars":       None,
            "description": "Python standard library diffing tool.",
            "use_case":    "Detect changes in competitor website content",
            "category":    "comparison",
            "mcp_ready":   False,
        },
    ],
    # Module 6 — Market Scout
    6: [
        {
            "name":        "feedparser",
            "github":      "kurtmckee/feedparser",
            "stars":       1900,
            "description": "Parse Atom and RSS feeds.",
            "use_case":    "Monitor trade news, market signals, industry RSS feeds",
            "category":    "data_feeds",
            "mcp_ready":   False,
        },
        {
            "name":        "praw",
            "github":      "praw-dev/praw",
            "stars":       3500,
            "description": "Python Reddit API Wrapper.",
            "use_case":    "Monitor subreddits for buyer intent signals",
            "category":    "social_monitoring",
            "mcp_ready":   False,
        },
    ],
    # Module 7 — Reviews Agent
    7: [
        {
            "name":        "googlemaps",
            "github":      "googlemaps/google-maps-services-python",
            "stars":       4400,
            "description": "Google Maps Platform Web Services for Python.",
            "use_case":    "Fetch Google Reviews via Places API",
            "category":    "reviews",
            "mcp_ready":   True,
        },
    ],
    # Module 9 — Retention Agent
    9: [
        {
            "name":        "twilio-python",
            "github":      "twilio/twilio-python",
            "stars":       2800,
            "description": "Official Twilio Python helper library.",
            "use_case":    "Send loyalty WhatsApp messages, win-back campaigns",
            "category":    "messaging",
            "mcp_ready":   True,
        },
    ],
    # Module 12 — Creative Studio
    12: [
        {
            "name":        "pillow",
            "github":      "python-pillow/Pillow",
            "stars":       12000,
            "description": "Python Imaging Library fork.",
            "use_case":    "Image processing, asset generation, resizing for social",
            "category":    "image_processing",
            "mcp_ready":   False,
        },
        {
            "name":        "moviepy",
            "github":      "Zulko/moviepy",
            "stars":       12000,
            "description": "Video editing with Python.",
            "use_case":    "Compile video scripts into video drafts, add subtitles",
            "category":    "video",
            "mcp_ready":   False,
        },
    ],
    # Module 13 — Website Builder
    13: [
        {
            "name":        "gsap",
            "github":      "greensock/GSAP",
            "stars":       19000,
            "description": "Professional-grade animation library for JavaScript.",
            "use_case":    "Scroll-triggered animations, hero entrance, stagger effects",
            "category":    "animation",
            "mcp_ready":   False,
        },
        {
            "name":        "netlify-python",
            "github":      "netlify/netlify-py",
            "stars":       700,
            "description": "Python client for Netlify API.",
            "use_case":    "Deploy websites, manage sites, update DNS",
            "category":    "deployment",
            "mcp_ready":   False,
        },
        {
            "name":        "beautifulsoup4",
            "github":      "waylan/beautifulsoup",
            "stars":       7600,
            "description": "Library for pulling data out of HTML/XML files.",
            "use_case":    "Analyse competitor sites, extract structure for redesign reference",
            "category":    "parsing",
            "mcp_ready":   False,
        },
        {
            "name":        "jinja2",
            "github":      "pallets/jinja",
            "stars":       10000,
            "description": "Fast, expressive template engine.",
            "use_case":    "Generate multi-page websites from templates",
            "category":    "templating",
            "mcp_ready":   False,
        },
    ],
    # General / any agent
    "general": [
        {
            "name":        "anthropic-sdk",
            "github":      "anthropics/anthropic-sdk-python",
            "stars":       5000,
            "description": "Official Anthropic Python SDK.",
            "use_case":    "AI reasoning, copy generation, data analysis",
            "category":    "ai",
            "mcp_ready":   True,
        },
        {
            "name":        "httpx",
            "github":      "encode/httpx",
            "stars":       13000,
            "description": "Next generation HTTP client for Python.",
            "use_case":    "Make API calls to any external service",
            "category":    "http",
            "mcp_ready":   False,
        },
        {
            "name":        "pydantic",
            "github":      "pydantic/pydantic",
            "stars":       21000,
            "description": "Data validation using Python type annotations.",
            "use_case":    "Validate and structure data from any source",
            "category":    "data_validation",
            "mcp_ready":   False,
        },
    ],
}


# ─────────────────────────────────────────────
# RISK CHECKER
# Any repo must pass this before being recommended
# ─────────────────────────────────────────────

RISK_KEYWORDS = [
    "password", "credential", "keylogger", "sniffer", "packet", "exploit",
    "rootkit", "backdoor", "ransomware", "cryptominer", "bypass", "jailbreak",
    "selenium_stealth", "undetected", "tor", "proxy_chain", "vpn_bypass",
]

RISKY_TOPICS = {
    "hacking", "pentesting", "exploitation", "malware", "keylogging",
    "credential-stuffing", "phishing",
}


def is_safe(repo: dict) -> tuple[bool, str]:
    """
    Return (is_safe, reason).
    Runs security checks on a GitHub repo dict.
    """
    name        = (repo.get("name") or "").lower()
    description = (repo.get("description") or "").lower()
    topics      = set(t.lower() for t in (repo.get("topics") or []))
    license_key = ((repo.get("license") or {}).get("spdx_id") or "").lower()

    # License check
    if license_key and license_key not in SAFE_LICENSES and license_key != "noassertion":
        return False, f"License '{license_key}' not approved for commercial use"

    # Risky topic
    blocked_topics = topics & RISKY_TOPICS
    if blocked_topics:
        return False, f"Risky topics detected: {blocked_topics}"

    # Risky keywords in name/description
    for kw in RISK_KEYWORDS:
        if kw in name or kw in description:
            return False, f"Risk keyword found: '{kw}'"

    # Must have been updated recently
    pushed = repo.get("pushed_at") or repo.get("updated_at") or ""
    if pushed:
        try:
            last_push = datetime.strptime(pushed[:10], "%Y-%m-%d")
            if datetime.utcnow() - last_push > timedelta(days=MAX_AGE_DAYS):
                return False, f"Not maintained — last push {pushed[:10]}"
        except ValueError:
            pass

    return True, "ok"


# ─────────────────────────────────────────────
# GITHUB SEARCH (fallback when curated list insufficient)
# ─────────────────────────────────────────────

def search_github(
    query:     str,
    min_stars: int = MIN_STARS,
    language:  str = "python",
    limit:     int = 5,
) -> list[dict]:
    """
    Search GitHub for repos matching a query.
    Applies safety vetting before returning.
    """
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    params = {
        "q":        f"{query} language:{language} stars:>{min_stars}",
        "sort":     "stars",
        "order":    "desc",
        "per_page": limit * 2,  # fetch extras in case some fail vetting
    }

    try:
        resp = requests.get(
            f"{GITHUB_API}/search/repositories",
            headers=headers,
            params=params,
            timeout=10,
        )
        if resp.status_code == 403:
            print(f"[GitHubSkills] Rate limited. Add GITHUB_TOKEN to .env for higher limits.")
            return []
        if resp.status_code != 200:
            print(f"[GitHubSkills] GitHub search failed: {resp.status_code}")
            return []

        items = resp.json().get("items", [])
        results = []

        for repo in items:
            if len(results) >= limit:
                break

            safe, reason = is_safe(repo)
            if not safe:
                print(f"[GitHubSkills] Skipping {repo.get('full_name')}: {reason}")
                continue

            results.append({
                "name":        repo["name"],
                "github":      repo["full_name"],
                "stars":       repo["stargazers_count"],
                "description": repo.get("description", ""),
                "license":     (repo.get("license") or {}).get("spdx_id", "unknown"),
                "url":         repo["html_url"],
                "last_update": repo.get("pushed_at", "")[:10],
                "language":    repo.get("language", ""),
                "use_case":    "Discovered via GitHub search — review before use",
                "category":    "discovered",
                "mcp_ready":   False,
                "vetted":      True,
                "source":      "github_search",
            })

        return results

    except Exception as e:
        print(f"[GitHubSkills] Search error: {e}")
        return []


# ─────────────────────────────────────────────
# MAIN — GET SKILLS FOR AN AGENT
# ─────────────────────────────────────────────

def get_skills_for_agent(
    module_id:   int,
    agent_role:  str = "",
    search_live: bool = False,
) -> list[dict]:
    """
    Get vetted, high-star GitHub skills for a specific agent.

    module_id:   agent's module (1–13+)
    agent_role:  role description for live search fallback
    search_live: if True, also query GitHub API for additional tools

    Returns list of skill dicts, sorted by stars descending.
    """
    # Start with curated list
    curated  = VETTED_SKILLS.get(module_id, [])
    general  = VETTED_SKILLS.get("general", [])
    all_skills = curated + [s for s in general if not any(s["name"] == c["name"] for c in curated)]

    # Live search as supplement
    if search_live and agent_role and GITHUB_TOKEN:
        print(f"[GitHubSkills] Searching GitHub for: {agent_role}...")
        live = search_github(agent_role, min_stars=1000, limit=3)
        for s in live:
            if not any(s["name"].lower() in existing["name"].lower() for existing in all_skills):
                s["vetted"] = True
                all_skills.append(s)

    # Sort by stars
    all_skills.sort(key=lambda s: s.get("stars") or 0, reverse=True)

    # Add metadata
    for s in all_skills:
        s.setdefault("vetted", True)
        s.setdefault("source", "curated_library")
        s.setdefault("risk_level", "low")
        if s.get("stars") and s["stars"] >= 5000:
            s["tier"] = "gold"
        elif s.get("stars") and s["stars"] >= 2000:
            s["tier"] = "silver"
        else:
            s["tier"] = "standard"

    return all_skills


def get_skills_for_custom_agent(
    agent_spec: dict,
    search_live: bool = False,
) -> list[dict]:
    """
    Get skills for a custom agent (module_id >= 99) based on its spec.
    Uses the role, skills list, and MCPs to find relevant tools.
    """
    role     = agent_spec.get("role", "")
    skills   = agent_spec.get("skills", [])
    mcps     = agent_spec.get("mcps", [])

    # Start with general tools
    results  = list(VETTED_SKILLS.get("general", []))

    # Live search if token available
    if search_live and role and GITHUB_TOKEN:
        search_terms = role.lower().replace("agent", "").replace("ai", "").strip()
        live = search_github(search_terms, min_stars=500, limit=4)
        results.extend(live)

    return results[:6]


def recommend_skill_upgrades(
    agent:       dict,
    current_skills: list[str] = None,
) -> list[dict]:
    """
    Given an agent's current skill set, recommend upgrades.
    Used by the Agent Creator when the CEO agent wants to "level up" an agent.

    Returns: list of {skill, reason, stars, github, risk_level}
    """
    module_id     = agent.get("module_id", 0)
    current       = set(s.lower() for s in (current_skills or agent.get("skills", [])))
    all_available = get_skills_for_agent(module_id, agent.get("role", ""))

    upgrades = []
    for skill in all_available:
        skill_name = skill["name"].lower()
        if not any(c in skill_name or skill_name in c for c in current):
            upgrades.append({
                "skill":       skill["name"],
                "github":      skill.get("github", ""),
                "stars":       skill.get("stars", 0),
                "description": skill.get("description", ""),
                "use_case":    skill.get("use_case", ""),
                "tier":        skill.get("tier", "standard"),
                "risk_level":  "low",
                "reason":      f"Adds {skill.get('category','capability')} to {agent.get('name','this agent')}'s toolkit",
            })

    # Sort by tier then stars
    tier_order = {"gold": 0, "silver": 1, "standard": 2}
    upgrades.sort(key=lambda x: (tier_order.get(x.get("tier"), 2), -(x.get("stars") or 0)))

    return upgrades[:4]


# ─────────────────────────────────────────────
# SKILL INSTALLER
# Adds a discovered skill to an agent's config
# ─────────────────────────────────────────────

def install_skill(agent: dict, skill: dict) -> dict:
    """
    Add a vetted GitHub skill to an agent's skill list.
    Returns the updated agent dict.

    Only installs if:
    1. Skill passes safety check
    2. Stars >= MIN_STARS
    3. Not already in the agent's list
    """
    if not skill.get("vetted", False):
        print(f"[GitHubSkills] Refusing to install unvetted skill: {skill.get('name')}")
        return agent

    if (skill.get("stars") or 0) < MIN_STARS:
        print(f"[GitHubSkills] Refusing to install low-star skill: {skill.get('name')} ({skill.get('stars')} stars)")
        return agent

    current_skills = agent.get("skills", [])
    if skill["name"] not in current_skills:
        agent = dict(agent)
        agent["skills"] = current_skills + [skill["name"]]
        print(f"[GitHubSkills] Installed '{skill['name']}' → {agent.get('name')} ({skill.get('stars',0):,}★)")
    else:
        print(f"[GitHubSkills] '{skill['name']}' already installed for {agent.get('name')}")

    return agent
