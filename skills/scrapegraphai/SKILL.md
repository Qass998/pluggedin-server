---
name: scrapegraphai
description: AI-driven web scraping using LLMs. Extracts structured data from any website by describing what you want in plain English. Use for contact extraction, business data, lead research from websites that block traditional scrapers.
source: github.com/ScrapeGraphAI/Scrapegraph-ai
stars: 26800
installed: 2026-06-07
---

# ScrapeGraphAI

Installed: `pip3 install scrapegraphai` (v1.20.1)
Also needs: `playwright install chromium` (run once)

## When to Use
- Extract emails, phones, names from a business website
- Scrape structured data (pricing, team pages, contact pages) from any URL
- Websites that block traditional scrapers — uses Playwright + LLM to navigate
- Need structured JSON output from unstructured web pages

## When NOT to Use
- LinkedIn (use Apify linkedin actor instead — ScrapeGraphAI gets blocked)
- Bulk scraping 100s of sites (use Apify for scale)
- Simple HTML parsing (use BeautifulSoup directly)

## Basic Usage

```python
from scrapegraphai.graphs import SmartScraperGraph
import os

graph_config = {
    "llm": {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": "openai/gpt-4o-mini",  # cheap, fast
    },
    "verbose": False,
    "headless": True,
}

scraper = SmartScraperGraph(
    prompt="Extract: company name, email addresses, phone numbers, and LinkedIn URL",
    source="https://example.com/contact",
    config=graph_config,
)

result = scraper.run()
print(result)
# Returns structured dict: {"company": "...", "email": "...", "phone": "...", "linkedin": "..."}
```

## Lead Gen Pattern (extract contacts from a list of URLs)

```python
from scrapegraphai.graphs import SmartScraperGraph
import os, json

def extract_contacts(url: str) -> dict:
    config = {
        "llm": {"api_key": os.getenv("OPENAI_API_KEY"), "model": "openai/gpt-4o-mini"},
        "verbose": False,
        "headless": True,
    }
    scraper = SmartScraperGraph(
        prompt="Extract: business name, owner/director name, email, phone number, and what the business does. Return as JSON.",
        source=url,
        config=config,
    )
    try:
        return scraper.run()
    except Exception as e:
        return {"error": str(e), "url": url}

# Run on a list of target websites
targets = [
    "https://restaurant-example.com/contact",
    "https://lawfirm-example.com/team",
]

leads = [extract_contacts(url) for url in targets]
print(json.dumps(leads, indent=2))
```

## Pipelines Available

| Pipeline | Use Case |
|----------|----------|
| SmartScraperGraph | Single URL, single prompt → structured output |
| SearchGraph | Search Google + scrape results automatically |
| ScriptCreatorGraph | Generates reusable scraping script for a site |
| OmniScraperGraph | Handles both text and images on the page |

## SearchGraph (find + scrape in one step)

```python
from scrapegraphai.graphs import SearchGraph

config = {
    "llm": {"api_key": os.getenv("OPENAI_API_KEY"), "model": "openai/gpt-4o-mini"},
    "max_results": 10,
    "verbose": False,
}

scraper = SearchGraph(
    prompt="Find UK restaurant owners with email addresses and phone numbers",
    config=config,
)

result = scraper.run()
```

## Environment
Requires: OPENAI_API_KEY (in .env)
First run: `python3 -m playwright install chromium`

## Cost Estimate
- gpt-4o-mini: ~$0.001-0.003 per page scraped
- 100 leads = ~$0.10-0.30 total
- Use gpt-4o-mini not gpt-4o for lead gen at scale
