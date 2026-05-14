"""
PluggedIN Python Wrappers
lib/tinyfish_client.py

TinyFish API wrapper for intelligent web browsing.
Use for: Reddit, legal directories, bot-protected sites,
         competitor research, signal detection.
Agent calls these methods directly.
"""

import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()
TINYFISH_API_KEY = os.getenv("TINYFISH_API_KEY")
BASE_URL = "https://agent.tinyfish.ai/v1"


def browse_site(url: str, goal: str, stealth: bool = False) -> dict:
    """
    Intelligently browse a website with a natural language goal.
    Returns clean structured data.
    
    Example:
    result = browse_site(
        "https://gcoffey.co.uk",
        "Find the firm's phone number, email address, 
         and whether they mention housing disrepair cases",
        stealth=False
    )
    """
    payload = {
        "url": url,
        "goal": goal,
        "browser_profile": "stealth" if stealth else "standard"
    }
    
    headers = {
        "X-API-Key": TINYFISH_API_KEY,
        "Content-Type": "application/json"
    }
    
    response = requests.post(
        f"{BASE_URL}/automation/run-sse",
        headers=headers,
        json=payload,
        stream=True
    )
    
    result = {}
    for line in response.iter_lines():
        if line:
            try:
                data = json.loads(line.decode().replace("data: ", ""))
                if data.get("type") == "COMPLETE":
                    result = data.get("resultJson", {})
            except:
                pass
    
    return result


def scrape_reddit(subreddit: str, query: str, limit: int = 50) -> list:
    """
    Scrape Reddit for relevant discussions and signals.
    
    Example:
    posts = scrape_reddit(
        "HousingDisrepair",
        "expert witness surveyor",
        50
    )
    """
    url = f"https://reddit.com/r/{subreddit}/search.json"
    goal = f"""
    Search for posts about: {query}
    Return a JSON array where each item has:
    - title: post title
    - author: username  
    - upvotes: number
    - url: post URL
    - snippet: first 200 chars of post
    - signals: any buying intent signals detected
    Limit to {limit} most relevant posts.
    """
    
    return browse_site(url, goal, stealth=True)


def search_legal_directories(query: str, location: str) -> list:
    """
    Search legal directories for solicitor firms.
    Handles bot-protected legal directories.
    
    Example:
    firms = search_legal_directories(
        "housing disrepair",
        "Manchester"
    )
    """
    directories = [
        "https://solicitors.lawsociety.org.uk",
        "https://www.lawsociety.org.uk/find-a-solicitor",
        "https://www.legalombudsman.org.uk"
    ]
    
    all_results = []
    goal = f"""
    Find solicitor firms specialising in {query} in {location}.
    For each firm return JSON with:
    - firm_name: string
    - address: string
    - phone: string
    - email: string
    - website: string
    - specialisms: list of practice areas
    - size: number of lawyers if visible
    """
    
    for directory in directories:
        results = browse_site(directory, goal, stealth=True)
        if results:
            all_results.extend(results if isinstance(results, list) else [results])
    
    return all_results


def monitor_competitor(competitor_url: str) -> dict:
    """
    Monitor a competitor website for changes and signals.
    
    Example:
    intel = monitor_competitor("https://competitor.com")
    """
    goal = """
    Analyse this competitor website and return JSON with:
    - new_services: any new services or products
    - pricing_changes: any pricing mentioned
    - new_content: recent blog posts or news
    - team_changes: any new team members
    - technology: what tools/tech they use
    - messaging: their key value propositions
    - weaknesses: any gaps or weaknesses visible
    """
    
    return browse_site(competitor_url, goal)


def extract_contact_signals(website_url: str) -> dict:
    """
    Extract contact info and buying signals from any website.
    
    Example:
    signals = extract_contact_signals("https://gcoffey.co.uk")
    """
    goal = """
    Extract from this website and return as JSON:
    - phone: main phone number
    - email: main email address
    - contact_name: any named partners or directors
    - services: list of main services
    - housing_disrepair: true/false if they mention it
    - expert_witnesses: true/false if they use them
    - legal_aid: true/false if they offer it
    - size_signals: any indicators of firm size
    - buying_signals: list of any signals they need help
    """
    
    return browse_site(website_url, goal)
