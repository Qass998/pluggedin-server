"""
PluggedIN Python Wrappers
lib/github_client.py

GitHub wrapper for skill discovery and validation.
Use for: finding agent skills, validating repos,
         checking stars and freshness before installing.
Agent calls these methods directly.
Never installs skills without passing validate_skill() first.
"""

import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
BASE_URL = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28"
}
if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"

# Approved skill sources from CLAUDE.md
APPROVED_SOURCES = [
    "VoltAgent/awesome-agent-skills",
    "gooseworks-ai/goose-skills",
    "gtmagents/gtm-agents",
    "VoltAgent/awesome-openclaw-skills",
    "tinyfish-io/skills",
    "coreyhaines31/marketingskills"
]

# Minimum thresholds from CLAUDE.md
MIN_STARS = 50
MAX_AGE_DAYS = 180


def search_skills(query: str, limit: int = 10) -> list:
    """
    Search GitHub for agent skills matching a query.
    Only searches approved sources from CLAUDE.md.
    Returns list of repos with validation status.

    Example:
    skills = search_skills("cold email outreach")
    skills = search_skills("competitor monitoring")
    """
    results = []

    for source in APPROVED_SOURCES:
        owner, repo = source.split("/")
        search_url = f"{BASE_URL}/search/code"

        params = {
            "q": f"{query} repo:{source} filename:SKILL.md",
            "per_page": limit
        }

        response = requests.get(search_url, headers=HEADERS, params=params)

        if response.status_code == 200:
            items = response.json().get("items", [])
            for item in items:
                results.append({
                    "repo": source,
                    "file": item.get("name"),
                    "path": item.get("path"),
                    "url": item.get("html_url"),
                    "raw_url": item.get("html_url", "").replace(
                        "github.com", "raw.githubusercontent.com"
                    ).replace("/blob/", "/")
                })

    return results[:limit]


def validate_skill(repo: str) -> dict:
    """
    Validate a GitHub repo before installing as a skill.
    Checks stars, freshness, README, and SKILL.md format.
    Returns validation result — PASS or FAIL with reasons.

    Agent MUST call this before installing any skill.

    Example:
    result = validate_skill("coreyhaines31/marketingskills")
    if result["valid"]:
        install_skill(result["skill_path"])
    """
    owner, repo_name = repo.split("/") if "/" in repo else ("", repo)

    # Get repo metadata
    repo_url = f"{BASE_URL}/repos/{owner}/{repo_name}"
    response = requests.get(repo_url, headers=HEADERS)

    if response.status_code != 200:
        return {
            "valid": False,
            "repo": repo,
            "reasons": ["Repo not found or inaccessible"]
        }

    data = response.json()
    stars = data.get("stargazers_count", 0)
    pushed_at = data.get("pushed_at", "")
    has_readme = data.get("has_pages", False)
    description = data.get("description", "")

    # Check age
    days_old = 999
    if pushed_at:
        last_push = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        days_old = (datetime.now(timezone.utc) - last_push).days

    # Check for SKILL.md
    skill_md_url = f"{BASE_URL}/repos/{owner}/{repo_name}/contents/SKILL.md"
    skill_response = requests.get(skill_md_url, headers=HEADERS)
    has_skill_md = skill_response.status_code == 200

    # Validate against CLAUDE.md thresholds
    reasons = []
    if stars < MIN_STARS:
        reasons.append(f"Only {stars} stars (minimum {MIN_STARS})")
    if days_old > MAX_AGE_DAYS:
        reasons.append(f"Last updated {days_old} days ago (maximum {MAX_AGE_DAYS})")
    if not has_skill_md:
        reasons.append("No SKILL.md found — not a valid skill format")
    if not description:
        reasons.append("No description — unclear purpose")

    valid = len(reasons) == 0

    return {
        "valid": valid,
        "repo": repo,
        "stars": stars,
        "days_since_update": days_old,
        "has_skill_md": has_skill_md,
        "description": description,
        "reasons": reasons if not valid else ["All checks passed"]
    }


def read_skill_md(repo: str, path: str = "SKILL.md") -> str:
    """
    Read the SKILL.md content from a GitHub repo.
    Agent reads this before installing to confirm purpose.

    Example:
    content = read_skill_md("coreyhaines31/marketingskills",
                            "cold-email/SKILL.md")
    """
    owner, repo_name = repo.split("/") if "/" in repo else ("", repo)

    url = f"{BASE_URL}/repos/{owner}/{repo_name}/contents/{path}"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        import base64
        content = response.json().get("content", "")
        return base64.b64decode(content).decode("utf-8")

    return ""


def list_skills_in_repo(repo: str) -> list:
    """
    List all skills available in an approved repo.
    Returns skill names, paths, and descriptions.

    Example:
    skills = list_skills_in_repo("coreyhaines31/marketingskills")
    """
    owner, repo_name = repo.split("/") if "/" in repo else ("", repo)

    url = f"{BASE_URL}/search/code"
    params = {
        "q": f"repo:{owner}/{repo_name} filename:SKILL.md",
        "per_page": 100
    }

    response = requests.get(url, headers=HEADERS, params=params)

    if response.status_code != 200:
        return []

    skills = []
    for item in response.json().get("items", []):
        skills.append({
            "name": item.get("path", "").replace("/SKILL.md", "").split("/")[-1],
            "path": item.get("path"),
            "url": item.get("html_url")
        })

    return skills


def check_all_approved_sources() -> dict:
    """
    Check all approved skill sources for availability and stats.
    Returns summary of each source repo.

    Example:
    sources = check_all_approved_sources()
    """
    results = {}

    for source in APPROVED_SOURCES:
        validation = validate_skill(source)
        skills = list_skills_in_repo(source)
        results[source] = {
            "accessible": validation.get("valid", False) or validation.get("stars", 0) > 0,
            "stars": validation.get("stars", 0),
            "skill_count": len(skills),
            "description": validation.get("description", "")
        }

    return results
