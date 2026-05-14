"""
market_scout.py — PluggedIN Free Market Intelligence Engine
============================================================
Scrapes Reddit, HackerNews, trade forums, and B2B marketplaces
using ONLY free tools — no Apify, no paid proxies.

Runs on your Mac (not in a sandbox) so has full internet access.

Reddit strategy (3 layers, best → fallback):
  1. PRAW  — official Reddit library, 60 req/min free. Needs a free Reddit
             app (2 min setup): https://www.reddit.com/prefs/apps
             Add to .env:  REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET
  2. RSS   — append .rss to any Reddit URL. Never blocked, no auth needed.
             Structured XML, reliable fallback.
  3. JSON  — append .json to Reddit URLs. Works without auth but rate-limited.

Other sources:
  • HackerNews Algolia     — hn.algolia.com/api/v1/search (free, no auth)
  • TradeKey               — public B2B RFQ board (HTML, fragile)
  • EC21                   — public trade leads (HTML, fragile)
  • Go4WorldBusiness       — verified buyer listings (HTML)

Usage:
  python3 lib/market_scout.py
  python3 lib/market_scout.py --topic africa_china
  python3 lib/market_scout.py --source reddit
  python3 lib/market_scout.py --list-topics

Setup Reddit (optional but recommended — 10x more results):
  1. Go to https://www.reddit.com/prefs/apps → Create App → script
  2. Add to PluggedIN/.env:
       REDDIT_CLIENT_ID=your_id
       REDDIT_CLIENT_SECRET=your_secret
"""

import os, sys, json, time, re, argparse, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

try:
    import requests
    from bs4 import BeautifulSoup
except ImportError:
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install",
                   "requests", "beautifulsoup4", "lxml",
                   "--break-system-packages", "-q"])
    import requests
    from bs4 import BeautifulSoup

ROOT = Path(__file__).parent.parent.resolve()

# ── Colour helpers ────────────────────────────────────────────
GRN = "\033[32m"; YLW = "\033[33m"; RED = "\033[31m"
CYN = "\033[36m"; BLD = "\033[1m"; RST = "\033[0m"
def ok(msg):  print(f"  {GRN}✓{RST} {msg}")
def warn(msg): print(f"  {YLW}⚠{RST} {msg}")
def err(msg):  print(f"  {RED}✗{RST} {msg}")
def info(msg): print(f"  {CYN}→{RST} {msg}")

HEADERS = {
    "User-Agent": "PluggedIN-MarketScout/1.0 (research bot; contact@pluggedin.ai)",
    "Accept": "application/json, text/html;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# ── Topic configuration ───────────────────────────────────────
TRADE_TOPICS = {
    "africa_china": {
        "label": "Africa → China (Zero Tariff 2026)",
        "reddit_queries": [
            "Africa export China zero tariff 2026",
            "sesame seeds export Nigeria Ghana broker",
            "cashew Africa China trade opportunity",
            "shea butter export wholesale buyer",
            "African commodity China import",
        ],
        "reddit_subs": ["importexport", "supplychain", "entrepreneur",
                        "smallbusiness", "Africa", "Nigeria", "ghana"],
        "hn_queries": ["Africa trade China", "commodity broker Africa"],
        "b2b_keywords": ["sesame seeds", "cashew nuts", "shea butter",
                         "ginger export", "hibiscus zobo", "African cocoa"],
    },
    "africa_europe": {
        "label": "Africa → Europe (UK, Germany, Poland)",
        "reddit_queries": [
            "African coffee specialty roasters UK",
            "hardwood charcoal import Europe Nigeria",
            "Rwanda coffee wholesale buyers",
            "moringa powder wholesale UK",
            "Africa commodity broker Europe commission",
        ],
        "reddit_subs": ["coffee", "importexport", "supplychain",
                        "UKBusiness", "entrepreneur"],
        "hn_queries": ["specialty coffee Africa Europe", "commodity import Europe"],
        "b2b_keywords": ["specialty coffee", "hardwood charcoal",
                         "moringa powder", "macadamia nuts", "shea butter bulk"],
    },
    "ai_agency": {
        "label": "AI Agency Services Demand",
        "reddit_queries": [
            "hire AI agency automation 2026",
            "AI lead generation service UK",
            "VAPI phone agent setup hire",
            "AI workflow automation agency price",
            "agentic team business automation",
        ],
        "reddit_subs": ["Entrepreneur", "smallbusiness", "AITools",
                        "SaaS", "startups", "consulting"],
        "hn_queries": ["AI agency automation", "hire AI agent developer"],
        "b2b_keywords": [],
    },
    "printful": {
        "label": "Print-on-Demand Trending Products",
        "reddit_queries": [
            "printful best selling products 2026",
            "print on demand niche trending Etsy",
            "POD business winning products AI theme",
            "Etsy trending designs 2026",
        ],
        "reddit_subs": ["Entrepreneur", "Etsy", "printfulshop",
                        "printondemand", "PassiveIncome"],
        "hn_queries": ["print on demand 2026", "Etsy automation"],
        "b2b_keywords": [],
    },
}


# ══════════════════════════════════════════════════════════════
#  SOURCE 1: Reddit — 3-layer strategy
#    Layer A: PRAW (official library, 60 req/min, needs free app)
#    Layer B: RSS  (never blocked, no auth, always works)
#    Layer C: JSON (fallback, rate-limited without auth)
# ══════════════════════════════════════════════════════════════

def _get_praw():
    """Return a PRAW Reddit instance if credentials are in .env, else None."""
    client_id     = os.getenv("REDDIT_CLIENT_ID", "")
    client_secret = os.getenv("REDDIT_CLIENT_SECRET", "")
    if not client_id or not client_secret:
        return None
    try:
        import praw
        return praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent="PluggedIN-MarketScout/1.0 by PluggedIN",
        )
    except ImportError:
        try:
            import subprocess
            subprocess.run([sys.executable, "-m", "pip", "install",
                           "praw", "--break-system-packages", "-q"])
            import praw
            return praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent="PluggedIN-MarketScout/1.0 by PluggedIN",
            )
        except Exception:
            return None
    except Exception as e:
        warn(f"PRAW init failed: {e}")
        return None


def _reddit_post_to_dict(post_data: dict, source_query: str) -> dict:
    """Normalise a raw Reddit post dict into our signal format."""
    return {
        "source": "reddit",
        "subreddit": post_data.get("subreddit", ""),
        "title": post_data.get("title", ""),
        "text": (post_data.get("selftext") or "")[:500],
        "score": post_data.get("score", 0),
        "comments": post_data.get("num_comments", 0),
        "url": f"https://reddit.com{post_data.get('permalink', '')}",
        "created": datetime.fromtimestamp(
            post_data.get("created_utc", 0), tz=timezone.utc
        ).strftime("%Y-%m-%d"),
        "query": source_query,
    }


def _scrape_reddit_praw(reddit, queries: list, subreddits: list, limit=8) -> list:
    """Layer A — PRAW. Best results, respects rate limits automatically."""
    results = []
    try:
        # Search all of Reddit
        for query in queries[:4]:
            for post in reddit.subreddit("all").search(query, sort="relevance",
                                                       time_filter="year", limit=limit):
                results.append({
                    "source": "reddit",
                    "subreddit": str(post.subreddit),
                    "title": post.title,
                    "text": (post.selftext or "")[:500],
                    "score": post.score,
                    "comments": post.num_comments,
                    "url": f"https://reddit.com{post.permalink}",
                    "created": datetime.fromtimestamp(
                        post.created_utc, tz=timezone.utc
                    ).strftime("%Y-%m-%d"),
                    "query": query,
                })

        # Top posts from targeted subreddits
        for sub in subreddits[:4]:
            try:
                for post in reddit.subreddit(sub).top(time_filter="month", limit=5):
                    results.append({
                        "source": "reddit",
                        "subreddit": sub,
                        "title": post.title,
                        "text": (post.selftext or "")[:500],
                        "score": post.score,
                        "comments": post.num_comments,
                        "url": f"https://reddit.com{post.permalink}",
                        "created": datetime.fromtimestamp(
                            post.created_utc, tz=timezone.utc
                        ).strftime("%Y-%m-%d"),
                        "query": f"top/{sub}",
                    })
            except Exception:
                pass
    except Exception as e:
        warn(f"PRAW search error: {e}")
    return results


def _scrape_reddit_rss(queries: list, subreddits: list, limit=5) -> list:
    """Layer B — RSS feeds. Never blocked, no auth, always structured."""
    results = []
    NS = "http://www.w3.org/2005/Atom"

    def _parse_rss(url: str, query: str):
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code != 200:
                return
            root = ET.fromstring(r.text)
            # Handle both RSS 2.0 and Atom
            entries = root.findall("channel/item") or root.findall(f"{{{NS}}}entry")
            for entry in entries[:limit]:
                def txt(tag):
                    el = entry.find(tag) or entry.find(f"{{{NS}}}{tag}")
                    return el.text.strip() if el is not None and el.text else ""
                title   = txt("title")
                link    = txt("link") or txt("id")
                summary = txt("description") or txt("summary") or txt("content")
                # Strip HTML from summary
                summary = re.sub(r"<[^>]+>", " ", summary)[:500].strip()
                pubdate = txt("pubDate") or txt("updated") or ""
                if title:
                    results.append({
                        "source": "reddit",
                        "subreddit": url.split("/r/")[1].split("/")[0] if "/r/" in url else "reddit",
                        "title": title,
                        "text": summary,
                        "score": 0,
                        "comments": 0,
                        "url": link,
                        "created": pubdate[:10] if pubdate else "",
                        "query": query,
                    })
            time.sleep(1.0)
        except Exception as e:
            warn(f"RSS parse failed ({url[:60]}): {e}")

    # Search RSS (Reddit search as RSS)
    for query in queries[:3]:
        q = requests.utils.quote(query)
        _parse_rss(f"https://www.reddit.com/search.rss?q={q}&sort=relevance&t=year", query)

    # Subreddit top posts via RSS
    for sub in subreddits[:4]:
        _parse_rss(f"https://www.reddit.com/r/{sub}/top.rss?t=month", f"top/{sub}")

    return results


def _scrape_reddit_json(queries: list, subreddits: list, limit=5) -> list:
    """Layer C — JSON API fallback. No auth, rate-limited ~10 req before 429."""
    results = []
    for query in queries[:2]:
        url = (f"https://www.reddit.com/search.json"
               f"?q={requests.utils.quote(query)}&sort=relevance&limit={limit}&t=year")
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                for p in r.json().get("data", {}).get("children", []):
                    d = p.get("data", {})
                    if d.get("score", 0) < 2: continue
                    results.append(_reddit_post_to_dict(d, query))
            elif r.status_code == 429:
                warn("Reddit JSON rate-limited — try adding PRAW credentials to .env")
                break
            time.sleep(2.0)
        except Exception as e:
            warn(f"Reddit JSON failed: {e}")
    return results


def scrape_reddit(queries: list, subreddits: list, limit=8) -> list:
    """
    Smart Reddit scraper — auto-selects best available method:
      PRAW (if credentials set) → RSS (always works) → JSON (fallback)
    """
    reddit = _get_praw()

    if reddit:
        info("Reddit: using PRAW (authenticated, 60 req/min)")
        results = _scrape_reddit_praw(reddit, queries, subreddits, limit)
        ok(f"PRAW → {len(results)} posts")
        return results

    info("Reddit: using RSS feeds (no auth needed, always reliable)")
    results = _scrape_reddit_rss(queries, subreddits, limit)
    ok(f"RSS → {len(results)} posts")

    if len(results) < 5:
        info("Reddit: topping up with JSON API...")
        results += _scrape_reddit_json(queries, subreddits, limit)

    return results

    return results


# ══════════════════════════════════════════════════════════════
#  SOURCE 2: HackerNews Algolia API (free, no auth)
# ══════════════════════════════════════════════════════════════
def scrape_hackernews(queries: list, limit=5) -> list:
    results = []
    for query in queries[:3]:
        url = (f"https://hn.algolia.com/api/v1/search"
               f"?query={requests.utils.quote(query)}"
               f"&tags=story&hitsPerPage={limit}&numericFilters=created_at_i>1704067200")
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            if r.status_code == 200:
                hits = r.json().get("hits", [])
                for h in hits:
                    results.append({
                        "source": "hackernews",
                        "title": h.get("title", ""),
                        "text": (h.get("story_text") or "")[:400],
                        "score": h.get("points", 0),
                        "comments": h.get("num_comments", 0),
                        "url": h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                        "created": h.get("created_at", "")[:10],
                        "query": query,
                    })
            time.sleep(0.5)
        except Exception as e:
            warn(f"HN search failed for '{query}': {e}")
    return results


# ══════════════════════════════════════════════════════════════
#  SOURCE 3: Go4WorldBusiness — verified buyer listings (free HTML)
# ══════════════════════════════════════════════════════════════
def scrape_go4wb(keywords: list) -> list:
    results = []
    base = "https://www.go4worldbusiness.com"
    for kw in keywords[:4]:
        slug = kw.lower().replace(" ", "-")
        # Try buyer listings for Europe
        urls_to_try = [
            f"{base}/buyers/europe/buyers/{slug}.html",
            f"{base}/buyers/united-kingdom/buyers/{slug}.html",
            f"{base}/buyers/china/buyers/{slug}.html",
        ]
        for url in urls_to_try:
            try:
                r = requests.get(url, headers={**HEADERS, "Accept": "text/html"},
                                 timeout=10)
                if r.status_code == 200 and len(r.text) > 500:
                    soup = BeautifulSoup(r.text, "lxml")
                    # Extract buyer cards
                    cards = soup.select(".buyer-item, .company-item, [class*='buyer']")
                    for card in cards[:5]:
                        name = card.select_one("h2, h3, .company-name, strong")
                        country_el = card.select_one(".country, .location, [class*='country']")
                        product_el = card.select_one(".product, .products, p")
                        results.append({
                            "source": "go4worldbusiness",
                            "keyword": kw,
                            "buyer": name.get_text(strip=True) if name else "Unknown",
                            "country": country_el.get_text(strip=True) if country_el else url.split("/")[4],
                            "product": product_el.get_text(strip=True)[:200] if product_el else kw,
                            "url": url,
                        })
                time.sleep(2)
                break
            except Exception as e:
                warn(f"Go4WB failed for '{kw}': {e}")
    return results


# ══════════════════════════════════════════════════════════════
#  SOURCE 4: TradeKey public RFQs (free HTML)
# ══════════════════════════════════════════════════════════════
def scrape_tradekey(keywords: list) -> list:
    results = []
    for kw in keywords[:3]:
        url = f"https://www.tradekey.com/seekers/?keyword={requests.utils.quote(kw)}"
        try:
            r = requests.get(url, headers={**HEADERS, "Accept": "text/html"},
                             timeout=12)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                rfqs = soup.select(".rfq-item, .seeker-item, [class*='rfq'], article")
                for rfq in rfqs[:5]:
                    title_el = rfq.select_one("h2, h3, .title, a")
                    desc_el = rfq.select_one("p, .desc, .description")
                    country_el = rfq.select_one(".country, .location, [class*='country']")
                    results.append({
                        "source": "tradekey",
                        "keyword": kw,
                        "title": title_el.get_text(strip=True)[:150] if title_el else kw,
                        "description": desc_el.get_text(strip=True)[:300] if desc_el else "",
                        "buyer_country": country_el.get_text(strip=True) if country_el else "Unknown",
                        "url": url,
                    })
            time.sleep(2)
        except Exception as e:
            warn(f"TradeKey failed for '{kw}': {e}")
    return results


# ══════════════════════════════════════════════════════════════
#  SOURCE 5: EC21 Trade Leads (free HTML)
# ══════════════════════════════════════════════════════════════
def scrape_ec21(keywords: list) -> list:
    results = []
    for kw in keywords[:3]:
        url = f"https://www.ec21.com/trade-lead/?trade=buy&keyword={requests.utils.quote(kw)}"
        try:
            r = requests.get(url, headers={**HEADERS, "Accept": "text/html"},
                             timeout=12)
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, "lxml")
                leads = soup.select(".tl_item, .trade-lead-item, [class*='lead']")
                for lead in leads[:5]:
                    title_el = lead.select_one("h3, h4, .title, a")
                    desc_el = lead.select_one("p, .description")
                    results.append({
                        "source": "ec21",
                        "keyword": kw,
                        "title": title_el.get_text(strip=True)[:150] if title_el else kw,
                        "description": desc_el.get_text(strip=True)[:300] if desc_el else "",
                        "url": url,
                    })
            time.sleep(2)
        except Exception as e:
            warn(f"EC21 failed for '{kw}': {e}")
    return results


# ══════════════════════════════════════════════════════════════
#  SCORER — rank signals by relevance and intent
# ══════════════════════════════════════════════════════════════
BUY_SIGNALS = [
    "looking for", "want to buy", "seeking supplier", "need supplier",
    "require", "interested in", "rfq", "quotation", "import", "buyer",
    "wholesale", "bulk", "distributor", "commission", "broker",
]
MONEY_SIGNALS = ["contract", "£", "$", "€", "ton", "kg", "container", "fcl"]

def score_signal(item: dict) -> int:
    text = (item.get("title", "") + " " + item.get("text", "") +
            " " + item.get("description", "")).lower()
    score = 0
    for sig in BUY_SIGNALS:
        if sig in text: score += 2
    for sig in MONEY_SIGNALS:
        if sig in text: score += 3
    score += min(item.get("score", 0) // 10, 5)
    score += min(item.get("comments", 0) // 5, 3)
    return score


# ══════════════════════════════════════════════════════════════
#  AIRTABLE LOGGER — saves signals to VendorLeads/MarketSignals
# ══════════════════════════════════════════════════════════════
def log_to_airtable(signals: list, topic_label: str):
    try:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env")
    except ImportError:
        pass

    token = os.getenv("AIRTABLE_TOKEN")
    base_id = os.getenv("AIRTABLE_BASE_AGENCY")
    if not token or not base_id:
        warn("No Airtable credentials — skipping log. Set AIRTABLE_TOKEN + AIRTABLE_BASE_AGENCY in .env")
        return

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    table = "Market%20Signals"
    url = f"https://api.airtable.com/v0/{base_id}/{table}"

    logged = 0
    for s in signals[:20]:
        record = {
            "fields": {
                "Topic": topic_label,
                "Source": s.get("source", ""),
                "Title": (s.get("title") or s.get("buyer") or "")[:255],
                "Summary": (s.get("text") or s.get("description") or s.get("product") or "")[:500],
                "URL": s.get("url", ""),
                "Relevance Score": s.get("_score", 0),
                "Date Found": datetime.now().strftime("%Y-%m-%d"),
                "Keyword": s.get("keyword") or s.get("query") or "",
                "Buyer Country": s.get("buyer_country") or s.get("country") or "",
            }
        }
        try:
            r = requests.post(url, headers=headers, json=record, timeout=10)
            if r.status_code in (200, 201):
                logged += 1
            time.sleep(0.2)
        except Exception as e:
            warn(f"Airtable log failed: {e}")

    ok(f"Logged {logged} signals to Airtable:Market Signals")


# ══════════════════════════════════════════════════════════════
#  MAIN RUNNER
# ══════════════════════════════════════════════════════════════
def run_scout(topic_key: str = None, source: str = "all",
              save_json: bool = True, log_airtable: bool = True):

    topics = {topic_key: TRADE_TOPICS[topic_key]} if topic_key and topic_key in TRADE_TOPICS else TRADE_TOPICS
    all_signals = []

    for key, config in topics.items():
        print(f"\n{BLD}{'─'*50}{RST}")
        print(f"{BLD}{CYN}Scouting: {config['label']}{RST}")
        print(f"{'─'*50}")

        signals = []

        if source in ("all", "reddit"):
            info("Scraping Reddit JSON API (free)...")
            reddit_results = scrape_reddit(
                config["reddit_queries"],
                config["reddit_subs"],
            )
            ok(f"Reddit → {len(reddit_results)} posts")
            signals.extend(reddit_results)

        if source in ("all", "hn"):
            info("Scraping HackerNews Algolia (free)...")
            hn_results = scrape_hackernews(config["hn_queries"])
            ok(f"HackerNews → {len(hn_results)} posts")
            signals.extend(hn_results)

        if source in ("all", "b2b") and config.get("b2b_keywords"):
            info("Scraping Go4WorldBusiness buyers (free HTML)...")
            g4_results = scrape_go4wb(config["b2b_keywords"])
            ok(f"Go4WB → {len(g4_results)} buyer listings")
            signals.extend(g4_results)

            info("Scraping TradeKey RFQs (free HTML)...")
            tk_results = scrape_tradekey(config["b2b_keywords"])
            ok(f"TradeKey → {len(tk_results)} RFQs")
            signals.extend(tk_results)

            info("Scraping EC21 trade leads (free HTML)...")
            ec_results = scrape_ec21(config["b2b_keywords"])
            ok(f"EC21 → {len(ec_results)} leads")
            signals.extend(ec_results)

        # Score and rank
        for s in signals:
            s["_score"] = score_signal(s)
            s["_topic"] = key
        signals.sort(key=lambda x: x["_score"], reverse=True)
        all_signals.extend(signals)

        # Print top hits
        top = [s for s in signals if s["_score"] > 0][:8]
        if top:
            print(f"\n{BLD}Top signals:{RST}")
            for i, s in enumerate(top, 1):
                src = s["source"].upper()
                title = (s.get("title") or s.get("buyer") or "")[:80]
                score = s["_score"]
                url = s.get("url", "")
                print(f"  {i}. [{src}] {title}")
                print(f"     Score: {score} | {url[:70]}")
        else:
            warn("No high-scoring signals found for this topic")

    # Save to JSON
    if save_json:
        out_dir = ROOT / "data" / "market_signals"
        out_dir.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M")
        out_file = out_dir / f"signals_{ts}.json"
        with open(out_file, "w") as f:
            json.dump(all_signals, f, indent=2)
        ok(f"Saved {len(all_signals)} signals → {out_file}")

    # Log to Airtable
    if log_airtable:
        log_to_airtable(all_signals, topic_key or "all")

    print(f"\n{BLD}Done.{RST} {len(all_signals)} total signals found.\n")
    return all_signals


def run_daily():
    """Entry point for scheduled daily run."""
    print(f"\n{CYN}{BLD}PluggedIN Market Scout — Daily Run{RST}")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    run_scout()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PluggedIN Market Scout")
    parser.add_argument("--topic", choices=list(TRADE_TOPICS.keys()),
                        help="Specific topic to scout")
    parser.add_argument("--source", default="all",
                        choices=["all", "reddit", "hn", "b2b"],
                        help="Which sources to scrape")
    parser.add_argument("--no-airtable", action="store_true",
                        help="Skip Airtable logging")
    parser.add_argument("--list-topics", action="store_true",
                        help="List available topics")
    args = parser.parse_args()

    if args.list_topics:
        print("\nAvailable topics:")
        for k, v in TRADE_TOPICS.items():
            print(f"  {k}: {v['label']}")
        sys.exit(0)

    run_scout(
        topic_key=args.topic,
        source=args.source,
        log_airtable=not args.no_airtable,
    )
