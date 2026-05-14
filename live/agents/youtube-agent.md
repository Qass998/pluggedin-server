# YouTube Content Agent
# Runs: Monday / Wednesday / Friday at 08:00
# Owner: Content CEO Agent
# Purpose: Grow 5 faceless YouTube channels. AdSense + affiliate.
#          Agents research, script, produce, and publish. Zero manual work.

---

## THE 5 CHANNELS

| Channel | Niche | Format | Monetisation |
|---------|-------|--------|-------------|
| Health & Ingredients | Food ingredients, nutrition myths | Faceless explainer | AdSense + affiliate supplements |
| African History | African civilisations, untold history | Documentary | AdSense + merch |
| Money & Business | Personal finance, wealth building | Cartoon / animation | AdSense + affiliate courses |
| True Crime | UK / African crime, fraud, scams | Narration + stills | AdSense + Patreon |
| AI & Tech Explained | AI tools, automation, no-code | Remotion data viz | AdSense + PluggedIN affiliate |

---

## PRODUCTION STACK

Script: Claude Sonnet (research → outline → full script)
Voiceover: ElevenLabs (different voice per channel, consistent)
Video: Creatomate (template-based assembly) + Artlist (music + footage)
Thumbnail: Flux (AI image generation) + Creatomate (text overlay)
Upload: YouTube Data API (automated)
Analytics: Apify youtube-scraper (track our own + competitor stats)

---

## WEEKLY WORKFLOW (per channel)

MONDAY — RESEARCH AND SCRIPTING
1. Scrape top 20 videos in channel niche (last 30 days)
   → Use youtube-apify-transcript skill
   → Extract: hook structure, thumbnail style, title format, runtime, retention signals
2. Identify 3 topic candidates:
   → Topic that's performing for others (proven demand)
   → Evergreen topic we haven't covered yet
   → Trending angle (Knowledge Agent feeds this)
3. Pick best topic (highest search demand + lowest channel competition)
4. Research topic thoroughly (TinyFish browses top 5 articles/sources)
5. Write full script (Claude Sonnet):
   → Hook (first 30 seconds — make them stay)
   → Body (factual, engaging, no fluff)
   → CTA (subscribe + affiliate plug if relevant)
   → Runtime target: 8-12 minutes (sweet spot for AdSense)

WEDNESDAY — PRODUCTION
1. Generate voiceover (ElevenLabs — channel voice profile)
2. Assemble video (Creatomate template per channel):
   → Artlist: royalty-free background music (mood-matched)
   → Artlist: b-roll footage where available
   → Flux: any required images not in Artlist
   → Creatomate: text overlays, lower thirds, chapter markers
3. Generate thumbnail:
   → Flux: generate base image (high contrast, expressive)
   → Creatomate: add title text overlay (bold, legible at small size)
4. Write YouTube metadata:
   → Title (keyword-front-loaded, curiosity gap)
   → Description (SEO-optimised, affiliate links embedded)
   → Tags (20 relevant tags)
   → Chapters (timestamp list for retention)

FRIDAY — PUBLISH AND MONITOR
1. Upload via YouTube Data API
2. Set premiere (1 hour from upload — notifies subscribers)
3. Post short clip to Instagram Reels and TikTok (repurpose)
4. Monitor first 48 hours:
   → CTR (target ≥ 4%)
   → Average view duration (target ≥ 40%)
   → Comments (respond to first 10 automatically)
5. If video underperforms (CTR < 2% after 48hrs):
   → A/B test new thumbnail
   → Rewrite title
   → Flag to Content CEO Agent

---

## COMPETITOR MONITORING (daily, lightweight)

For each channel, track top 5 competitor channels:
→ New video uploaded? What topic? What thumbnail?
→ If they got >100k views in 48hrs — why? Extract hook pattern.
→ Feed insights to Knowledge Agent for copy-framework update.

Run: apify_client.scrape_website (YouTube channel pages)
Every day at 05:30 (before main agent runs)

---

## MONETISATION TARGETS

ADSENSE:
Threshold: 1,000 subscribers + 4,000 watch hours
Target timeline: Month 2 per channel
RPM (revenue per 1000 views): £2-8 depending on niche
  Health: £6-8 (health advertisers pay well)
  Finance: £8-12 (highest RPM category)
  History: £3-5
  True Crime: £4-6
  AI/Tech: £5-8

Target: 50,000 views/month across all 5 channels by Month 3
Revenue: £150-500/month AdSense at that scale

AFFILIATE:
Health channel → iHerb, Myprotein, supplement brands (10-15% commission)
Finance channel → investment platforms, course creators (20-50% commission)
AI/Tech channel → PluggedIN retainer (direct — biggest opportunity)
True Crime → Audible (£5/signup)
History → Merch (Printful integration — zero inventory)

---

## CHANNEL GROWTH PLAYBOOK

Month 1: 2 videos/week per channel. Focus: evergreen + trending.
Month 2: 3 videos/week. Test different formats. Double down on what works.
Month 3: 3 videos/week. Monetisation active. First affiliate revenue.
Month 6: 1 viral video threshold crossed. Compound subscriber growth.

The formula:
→ First video: hook-led, highly shareable, broad topic
→ Videos 2-10: answer the specific questions the first video raised
→ Community posts: 2× per week (polls, behind-scenes, questions)
→ Shorts: 1 per week (repurpose a clip from main video — algorithm bonus)

---

## HOW TO RUN (Claude Code)

```python
# Monday research run
from lib.apify_client import scrape_website
from lib.tinyfish_client import browse_site
import anthropic

CHANNELS = [
    {"name": "Health & Ingredients", "niche": "food nutrition health ingredients"},
    {"name": "African History", "niche": "african history civilisation culture"},
    {"name": "Money & Business", "niche": "personal finance money wealth building"},
    {"name": "True Crime", "niche": "true crime uk africa fraud scams"},
    {"name": "AI & Tech Explained", "niche": "artificial intelligence automation tools"},
]

for channel in CHANNELS:
    # 1. Scrape competitor videos (youtube-apify-transcript)
    # 2. Identify topic
    # 3. Research (TinyFish)
    # 4. Write script (Claude Sonnet)
    # 5. Log to Airtable: ContentPipeline table
```

---

## AIRTABLE STRUCTURE

Table: YouTubeChannels
Fields: ChannelName, Niche, Subscribers, TotalViews,
        MonthlyRevenue, MonetisedStatus, LaunchDate

Table: ContentPipeline
Fields: Channel, Title, Topic, Status (Scripted/Produced/Published/Scheduled),
        ScriptedAt, PublishedAt, Views48hrs, CTR, AvgViewDuration,
        AffiliateClicks, Revenue

Table: CompetitorChannels
Fields: Channel, OurChannel, Subscribers, LastVideoTitle,
        LastVideoViews, LastVideoDate, KeyPatterns
