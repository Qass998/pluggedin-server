"""
PluggedIN Python Wrappers
lib/vibe_client.py

Vibe Prospecting wrapper for B2B contact finding and enrichment.
Use for: finding decision-maker emails, phone numbers,
         LinkedIn profiles, company details.
Agent calls these methods directly.
Never writes raw Vibe Prospecting API calls.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
VIBE_API_KEY = os.getenv("VIBE_PROSPECTING_KEY")
BASE_URL = "https://api.vibepro.io/v1"

HEADERS = {
    "Authorization": f"Bearer {VIBE_API_KEY}",
    "Content-Type": "application/json"
}


def find_contacts(company_name: str, company_domain: str,
                  titles: list = None, limit: int = 5) -> list:
    """
    Find decision-maker contacts at a company.
    Returns list of contacts with email and LinkedIn.

    Example:
    contacts = find_contacts(
        "Graham Coffey & Co",
        "gcoffey.co.uk",
        titles=["Partner", "Director", "Managing Partner"],
        limit=3
    )
    """
    payload = {
        "company_name": company_name,
        "domain": company_domain,
        "titles": titles or ["Director", "Partner", "Managing Director", "CEO", "Founder"],
        "limit": limit
    }

    response = requests.post(
        f"{BASE_URL}/people/search",
        headers=HEADERS,
        json=payload
    )
    return response.json().get("contacts", [])


def enrich_contact(email: str = None, linkedin_url: str = None) -> dict:
    """
    Enrich a contact with full profile data.
    Returns phone, email, LinkedIn, job title, company.

    Example:
    profile = enrich_contact(email="graham@gcoffey.co.uk")
    profile = enrich_contact(linkedin_url="https://linkedin.com/in/graham-coffey")
    """
    payload = {}
    if email:
        payload["email"] = email
    if linkedin_url:
        payload["linkedin_url"] = linkedin_url

    response = requests.post(
        f"{BASE_URL}/people/enrich",
        headers=HEADERS,
        json=payload
    )
    return response.json().get("person", {})


def enrich_company(domain: str) -> dict:
    """
    Enrich a company with full firmographic data.
    Returns size, revenue, tech stack, industry, HQ.

    Example:
    company = enrich_company("gcoffey.co.uk")
    """
    payload = {"domain": domain}

    response = requests.post(
        f"{BASE_URL}/companies/enrich",
        headers=HEADERS,
        json=payload
    )
    return response.json().get("company", {})


def search_by_icp(industry: str, location: str, size_min: int = 1,
                  size_max: int = 50, keywords: list = None,
                  limit: int = 100) -> list:
    """
    Search for companies matching your ICP.
    Returns list of companies with key contacts.

    Example:
    leads = search_by_icp(
        industry="Legal Services",
        location="Manchester, UK",
        size_min=2,
        size_max=30,
        keywords=["housing disrepair", "personal injury"],
        limit=50
    )
    """
    payload = {
        "industry": industry,
        "location": location,
        "employee_count_min": size_min,
        "employee_count_max": size_max,
        "keywords": keywords or [],
        "limit": limit
    }

    response = requests.post(
        f"{BASE_URL}/companies/search",
        headers=HEADERS,
        json=payload
    )
    return response.json().get("companies", [])


def verify_email(email: str) -> dict:
    """
    Verify an email address before outreach.
    Returns validity status and deliverability score.

    Example:
    result = verify_email("graham@gcoffey.co.uk")
    # Returns: {"valid": True, "score": 95, "reason": "verified"}
    """
    response = requests.get(
        f"{BASE_URL}/email/verify",
        headers=HEADERS,
        params={"email": email}
    )
    return response.json()
