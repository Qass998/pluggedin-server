# PluggedIN Acquisition Backend

Backend API for PluggedIN's lead acquisition pipeline.

## Setup

```bash
npm install
```

## Environment

Copy `.env.example` to `.env` and fill in:
```
AIRTABLE_API_KEY=your_key
AIRTABLE_BASE_ACQUISITION=appGHRvhTGe9KlQNw
```

## Run

```bash
npm start      # production
npm run dev    # development (with nodemon)
```

Server runs on http://localhost:3001

## API Endpoints

### Find Leads
```bash
POST /api/leads/find
{
  "country": "UK",
  "niche": "Legal Services",
  "limit": 50
}
```

### List Leads
```bash
GET /api/leads
GET /api/leads?status=Discovered
GET /api/leads?source=LinkedIn
```

### Get Single Lead
```bash
GET /api/leads/:id
```

### Update Lead Status
```bash
PATCH /api/leads/:id
{
  "status": "Contacted"
}
```

### Log Outreach
```bash
POST /api/leads/:id/outreach
{
  "leadName": "John Smith",
  "type": "Email",
  "message": "Subject: Partnership opportunity",
  "status": "Sent"
}
```

### Pipeline Metrics
```bash
GET /api/pipeline
```

## Status Codes

- **Discovered** — Lead found
- **Enriched** — Lead enriched with data
- **Contacted** — Outreach sent
- **Replied** — Lead responded
- **Meeting Booked** — Meeting scheduled
- **Proposal Sent** — Proposal delivered
- **Closed Won** — Deal closed
- **Closed Lost** — Lead unqualified
