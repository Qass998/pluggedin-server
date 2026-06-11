# PluggedIN Content Analysis & Video Generation Pipeline

Complete system for analyzing content and generating personalized outreach videos.

---

## **ARCHITECTURE**

```
POST /api/content/analyze-and-create-video
  ↓
[Obscura Scraper] ← Parallel LinkedIn/Instagram scraping with anti-detection
  ↓
[Content Analyzer] ← Claude analyzes posts, identifies strengths/gaps
  ↓
[Script Generator] ← Claude creates natural scripts
  ↓
[11Labs Voiceover] ← Converts script to audio
  ↓
[Remotion Rendering] ← Creates video with custom data
  ↓
[FFmpeg Merge] ← Combines video + audio
  ↓
[Multi-Channel Drafts] ← Generates LinkedIn/Email/Instagram copy
  ↓
[Airtable Storage] ← Saves everything for tracking
```

---

## **COMPONENTS**

### **1. Obscura Scraper** (`/scrapers/obscura-scraper.js`)
**What it does:** Parallel web scraping with anti-detection

**Features:**
- 5-10 concurrent browser instances
- Anti-bot fingerprint randomization
- Random user-agent rotation
- Random delays between requests
- LinkedIn post extraction (content, author, metrics)
- Instagram video extraction (caption, video URL, metrics)

**Usage:**
```javascript
const scraper = new ObscuraScraper({ maxConcurrent: 5 });
await scraper.initialize();

const posts = await scraper.scrapeLinkedInPosts({
  keywords: ['legal', 'solicitors'],
  limit: 50
});
```

---

### **2. Content Analyzer** (`/services/content-analyzer.js`)
**What it does:** Claude analyzes content and generates insights

**Features:**
- LinkedIn post analysis (hook strength, CTA effectiveness)
- Instagram video analysis (retention potential)
- Generates actionable improvements
- Scores strengths/gaps on 1-10 scale
- Provides specific rewrite suggestions

**Output:**
```json
{
  "strengths": ["clear messaging", "strong data points"],
  "gaps": ["weak call-to-action"],
  "hook_strength": 7,
  "cta_effectiveness": 4,
  "improvements": ["add social proof", "strengthen CTA"],
  "rewritten_hook": "Better opening line",
  "rewritten_cta": "Stronger call-to-action"
}
```

---

### **3. Script Generator** (`/services/script-generator.js`)
**What it does:** Creates natural voiceover scripts and generates audio

**Features:**
- LinkedIn script: 60 seconds, conversational tone
- Instagram script: 45 seconds, creator-to-creator vibe
- Uses Claude for personalized scripts
- Generates 11Labs voiceover automatically
- Returns MP3 audio file

**Pipeline:**
```
Claude generates script → 11Labs converts to speech → Returns MP3 audio
```

---

### **4. Video Generator** (`/services/video-generator.js`)
**What it does:** Renders Remotion videos and merges with audio

**Features:**
- Renders custom React components via Remotion
- Combines video + voiceover using FFmpeg
- Supports dynamic data injection (prospect name, metrics, etc.)
- Returns final MP4 file

**Process:**
```
Remotion template → renders MP4 video
                 ↓
            FFmpeg merges with audio
                 ↓
           Final MP4 (60 seconds)
```

---

### **5. Remotion Templates**
**LinkedIn Post Analysis** (`/video-templates/linkedin-post-analysis.jsx`)
- [0-5s] Opening with prospect name
- [5-15s] Display their actual post
- [15-25s] Analysis (strengths vs. gaps)
- [25-40s] Improved version side-by-side
- [40-50s] Value proposition
- [50-60s] CTA + calendar link

**Instagram Video Improvement** (coming soon)
- Similar structure, optimized for video creators

---

### **6. Outreach Drafts** (`/services/outreach-drafts.js`)
**What it does:** Generates multi-channel messaging

**Channels:**
- **LinkedIn DM:** Professional, specific to post, under 150 words
- **Email:** Data-driven, includes analysis + video + calendar link
- **Instagram DM:** Casual creator-to-creator, enthusiastic tone

**Example:**
```
LinkedIn: "Hi [Name], I analyzed your post on [topic]..."
Email:    "Subject: Quick analysis of your [company] content..."
Instagram: "Hey! 👋 I noticed your recent post..."
```

---

### **7. Airtable Integration**
**Tables:**
- `LinkedIn Posts` — Raw scraped content
- `Content Analysis` — Analysis results + scripts + videos
- `Generated Videos` — Video metadata + URLs
- `Outreach Drafts` — All three channel versions

---

## **API ENDPOINT**

### **POST /api/content/analyze-and-create-video**

**Request:**
```json
{
  "source": "linkedin",
  "contentType": "post",
  "keywords": ["legal", "solicitors"],
  "limit": 20,
  "vertical": "legal"
}
```

**Response:**
```json
{
  "success": true,
  "summary": {
    "total_processed": 18,
    "total_errors": 2,
    "source": "linkedin",
    "vertical": "legal"
  },
  "results": [
    {
      "prospect": {
        "name": "John Smith",
        "company": "Smith & Associates"
      },
      "analysis": {
        "strengths": ["clear messaging"],
        "gaps": ["weak CTA"]
      },
      "script": {
        "wordCount": 152,
        "estimatedSeconds": 62
      },
      "video": {
        "url": "https://videos.pluggedin.io/john-smith.mp4",
        "duration": 60
      },
      "outreach": {
        "linkedin": { "draft": "..." },
        "email": { "subject": "...", "body": "..." },
        "instagram": { "draft": "..." }
      },
      "airtable_id": "rec123abc...",
      "ready": true
    }
  ],
  "errors": []
}
```

---

## **SETUP INSTRUCTIONS**

### **1. Install Dependencies**
```bash
cd backend
npm install
```

### **2. Set Environment Variables**
Copy `.env.example` to `.env` and fill in:
```
ANTHROPIC_API_KEY=your_key_here
ELEVENLABS_API_KEY=your_key_here
AIRTABLE_API_KEY=your_key_here
```

### **3. Create Airtable Tables**
In your PluggedIN Acquisition base, create:
- `Content Analysis` table
- `LinkedIn Posts` table
- `Generated Videos` table
- `Outreach Drafts` table

### **4. Start Server**
```bash
npm run dev
```

### **5. Test Endpoint**
```bash
curl -X POST http://localhost:3001/api/content/analyze-and-create-video \
  -H "Content-Type: application/json" \
  -d '{
    "source": "linkedin",
    "keywords": ["legal"],
    "limit": 5,
    "vertical": "legal"
  }'
```

---

## **WORKFLOW: SEND OUTREACH**

Once videos are generated:

1. **LinkedIn:** Copy draft → Send DM with video link
2. **Email:** Copy email draft → Send via Gmail
3. **Instagram:** Copy DM draft → Send via Instagram

**Expected response rates:**
- LinkedIn DM: 20-30%
- Email: 15-20%
- Instagram DM: 25-35%

---

## **COSTS & SCALE**

**Per video:**
- Scraping: Free (Obscura)
- Claude analysis: ~$0.01
- 11Labs voiceover: ~$0.10
- Remotion rendering: ~$0.05
- **Total per video: ~$0.16**

**At scale:**
- 50 videos: ~$8
- 100 videos: ~$16
- 1000 videos: ~$160

---

## **STATUS**

✅ Scrapers (Obscura)
✅ Content Analyzer (Claude)
✅ Script Generator (Claude + 11Labs)
✅ Video Templates (Remotion JSX)
✅ Outreach Drafts
⏳ Video Rendering (awaits Remotion setup)
⏳ Cloud Upload (Vercel Blob / S3)

---

## **NEXT STEPS**

1. Test with 20 LinkedIn prospects
2. Measure response rates
3. Add Instagram scraper
4. Optimize script quality based on response patterns
5. Scale to 100+ daily videos
6. Add more verticals (B2B SaaS, ecommerce, roofing)
