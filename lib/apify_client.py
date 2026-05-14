"""
PluggedIN Python Wrappers
lib/apify_client.py

Apify API wrapper for bulk web scraping.
Agent calls these methods directly.
Never writes raw Apify API calls.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()
APIFY_TOKEN = os.getenv("APIFY_TOKEN")
BASE_URL = "https://api.apify.com/v2"


def search_google_maps(query: str, location: str = "", max_results: int = 100) -> list:
    """
    Search Google Maps for businesses.
    Returns list of businesses with contact details.
    
    Example:
    firms = search_google_maps(
        "housing disrepair solicitors",
        "Manchester, UK",
        50
    )
    """
    actor_id = "compass~crawler-google-places"
    run_url = f"{BASE_URL}/acts/{actor_id}/runs"
    
    payload = {
        "searchStringsArray": [f"{query} {location}"],
        "maxCrawledPlaces": max_results,
        "language": "en",
        "exportPlaceUrls": True
    }
    
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
    
    response = requests.post(run_url, json=payload, headers=headers)
    run_id = response.json()["data"]["id"]
    
    # Wait for completion and return results
    results_url = f"{BASE_URL}/actor-runs/{run_id}/dataset/items"
    results = requests.get(results_url, headers=headers)
    return results.json()


def scrape_linkedin_profiles(company_urls: list) -> list:
    """
    Scrape LinkedIn company profiles.
    Returns company details and key contacts.
    
    Example:
    profiles = scrape_linkedin_profiles([
        "https://linkedin.com/company/gromatic"
    ])
    """
    actor_id = "2SyF0bVxmgGr8IVCZ"
    run_url = f"{BASE_URL}/acts/{actor_id}/runs"
    
    payload = {
        "startUrls": [{"url": url} for url in company_urls],
        "maxItems": len(company_urls) * 10
    }
    
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
    response = requests.post(run_url, json=payload, headers=headers)
    run_id = response.json()["data"]["id"]
    
    results_url = f"{BASE_URL}/actor-runs/{run_id}/dataset/items"
    results = requests.get(results_url, headers=headers)
    return results.json()


def scrape_website(url: str, selectors: dict = None) -> dict:
    """
    Scrape a single website for structured data.
    Returns page content and extracted data.
    
    Example:
    data = scrape_website(
        "https://gcoffey.co.uk",
        {"phone": ".phone", "email": ".email"}
    )
    """
    actor_id = "apify~web-scraper"
    run_url = f"{BASE_URL}/acts/{actor_id}/runs"
    
    payload = {
        "startUrls": [{"url": url}],
        "pageFunction": """
            async function pageFunction(context) {
                const { page } = context;
                return {
                    url: page.url(),
                    title: await page.title(),
                    text: await page.evaluate(() => document.body.innerText)
                };
            }
        """
    }
    
    headers = {"Authorization": f"Bearer {APIFY_TOKEN}"}
    response = requests.post(run_url, json=payload, headers=headers)
    run_id = response.json()["data"]["id"]
    
    results_url = f"{BASE_URL}/actor-runs/{run_id}/dataset/items"
    results = requests.get(results_url, headers=headers)
    return results.json()[0] if results.json() else {}
