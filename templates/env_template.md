# PluggedIN — .env Template by Module
# Copy relevant keys into client .env based on modules purchased.
# Never share or commit .env files. Always in .gitignore.

---

## ALWAYS REQUIRED (every client)

```
ANTHROPIC_API_KEY=
AIRTABLE_TOKEN=
AIRTABLE_BASE_[CLIENTNAME]=
```

---

## MODULE 1 — PRESENCE AGENT
Requires: VAPI, Cal.com

```
VAPI_API_KEY=
VAPI_PHONE_NUMBER_ID=
VAPI_RECEPTIONIST_ASSISTANT_ID=
CALCOM_API_KEY=
CALCOM_EVENT_TYPE_ID=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

---

## MODULE 2 — PIPELINE AGENT
Requires: Apify, Vibe Prospecting, Gmail MCP

```
APIFY_TOKEN=
VIBE_PROSPECTING_KEY=
# Gmail MCP configured separately in .claude.json
```

---

## MODULE 3 — MARKETING AGENT
Requires: Creatomate, Artlist (manual), Meta Ads API

```
CREATOMATE_API_KEY=
META_ACCESS_TOKEN=
META_AD_ACCOUNT_ID=
META_PAGE_ID=
# Artlist: manual download, no API key required
```

---

## MODULE 4 — INTELLIGENCE AGENT
Requires: Apify, TinyFish, Google Alerts (via RSS)

```
APIFY_TOKEN=
TINYFISH_API_KEY=
GOOGLE_PLACES_API_KEY=
```

---

## MODULE 5 — SALES INTELLIGENCE
Requires: VAPI (call recording access), Airtable

```
VAPI_API_KEY=
# Uses existing VAPI key from Module 1 if purchased
```

---

## MODULE 6 — DATA INTELLIGENCE
Requires: Airtable, Remotion (local install)

```
# Remotion: npm install remotion
# No API key — runs locally
# PowerPoint: python-pptx installed via requirements.txt
```

---

## MODULE 7 — CONVERSION AGENT
Requires: TinyFish, Google Analytics (read), Framer

```
TINYFISH_API_KEY=
GOOGLE_ANALYTICS_PROPERTY_ID=
GOOGLE_ANALYTICS_CREDENTIALS=
```

---

## MODULE 8 — LEAD MARKETPLACE
Requires: VAPI outbound, Apify, Vibe

```
VAPI_API_KEY=
VAPI_PHONE_NUMBER_ID=
VAPI_QUALIFIER_ASSISTANT_ID=
APIFY_TOKEN=
VIBE_PROSPECTING_KEY=
```

---

## MODULE 9 — CUSTOMER RETENTION OS
Requires: Twilio WhatsApp, Google Places API (reviews)

```
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
GOOGLE_PLACES_API_KEY=
GOOGLE_BUSINESS_ACCESS_TOKEN=
```

---

## MODULE 10 — STOCK INTELLIGENCE
Requires: Airtable (stock tables), Gmail MCP (supplier alerts)

```
# Uses Airtable base with Stock and Suppliers tables
# Supplier alerts sent via Gmail MCP
# No additional API keys required beyond base requirements
```

---

## PLUGGEDIN LIVE ONLY (not for clients)

```
OPENROUTER_API_KEY=
OPENROUTER_DEFAULT_MODEL=
GITHUB_TOKEN=
TINYFISH_API_KEY=
VIBE_PROSPECTING_KEY=
AIRTABLE_BASE_PLUGGEDIN=
SHOPIFY_STORE_DOMAIN=
SHOPIFY_ACCESS_TOKEN=
GUMROAD_ACCESS_TOKEN=
ETSY_KEYSTRING=
ETSY_SHARED_SECRET=
```

---

## GETTING API KEYS

| Service | URL |
|---------|-----|
| Anthropic | https://console.anthropic.com/settings/keys |
| Airtable | https://airtable.com/create/tokens |
| VAPI | https://dashboard.vapi.ai/account |
| Apify | https://console.apify.com/settings/integrations |
| TinyFish | https://tinyfish.io/dashboard |
| Twilio | https://console.twilio.com |
| Creatomate | https://creatomate.com/dashboard |
| Cal.com | https://cal.com/settings/developer/api-keys |
| Google Cloud | https://console.cloud.google.com/apis/credentials |
| OpenRouter | https://openrouter.ai/keys |
| GitHub | https://github.com/settings/tokens |
| Meta | https://developers.facebook.com |
