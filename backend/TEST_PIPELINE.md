# Testing the Content Pipeline

Quick start guide for testing the video outreach system.

---

## **PHASE 1: Setup** (15 min)

### **1. Install dependencies**
```bash
cd ~/Documents/AI-Agency/PluggedIN/backend
npm install
```

### **2. Create .env file**
```bash
cp .env.example .env
```

Edit `.env` and add your keys:
```
ANTHROPIC_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
AIRTABLE_API_KEY=patXXXXXX...
AIRTABLE_BASE_ACQUISITION=appGHRvhTGe9KlQNw
```

### **3. Verify Airtable base**
- Base: "PluggedIN Acquisition" (appGHRvhTGe9KlQNw)
- Tables needed:
  - ✅ Leads (exists)
  - ✅ Outreach (exists)
  - ✅ Pipeline (exists)
  - ❓ Content Analysis (create if missing)
  - ❓ LinkedIn Posts (create if missing)
  - ❓ Generated Videos (create if missing)

### **4. Start server**
```bash
npm run dev
```

You should see:
```
PluggedIN Backend running on port 3001
```

---

## **PHASE 2: Test Scraper** (10 min)

### **Test: Scrape LinkedIn posts**

```bash
curl -X POST http://localhost:3001/api/content/analyze-and-create-video \
  -H "Content-Type: application/json" \
  -d '{
    "source": "linkedin",
    "keywords": ["solicitor", "law firm"],
    "limit": 5,
    "vertical": "legal"
  }'
```

**Expected response:**
```json
{
  "success": true,
  "summary": {
    "total_processed": 3,
    "total_errors": 2,
    "source": "linkedin"
  },
  "results": [
    {
      "prospect": {
        "name": "John Smith",
        "company": "Smith & Associates"
      },
      "analysis": { ... },
      "outreach": { ... }
    }
  ]
}
```

**What's happening:**
1. Obscura scraper launches 5 browsers
2. Each browser visits LinkedIn search results
3. Extracts post content + engagement metrics
4. Returns 3-5 prospects from 5 attempts (2-3 might fail)

---

## **PHASE 3: Test Analysis** (5 min)

### **Look at the response**

The `analysis` object shows:
```json
{
  "strengths": [
    "clear messaging about legal services",
    "specific case examples"
  ],
  "gaps": [
    "weak call-to-action",
    "no engagement incentive"
  ],
  "hook_strength": 7,
  "cta_effectiveness": 3,
  "improvements": [
    "Add social proof (client testimonials)",
    "Strengthen CTA (specific next step)"
  ]
}
```

**This means:**
- Claude analyzed the post
- Identified 2 strengths, 2 gaps
- Scored hook (7/10) and CTA (3/10)
- Generated specific improvements

---

## **PHASE 4: Test Script Generation** (10 min)

### **Check the generated script**

In the API response, look at `results[0].script`:
```json
{
  "wordCount": 156,
  "estimatedSeconds": 63
}
```

The script was generated but not shown in API response (it's 150+ words).

### **View full script:**
Check Airtable → Content Analysis table → find the prospect → view "script" field

**Example script:**
```
Hi John, I analyzed your recent post about commercial property law.

Here's what I found: Your messaging is clear and specific - 
you're leading with real cases, which builds trust. That's strong.

But here's the gap: You're not giving readers a clear next step. 
Most people read this and think "interesting" but don't know what to do.

Here's how we'd fix it. Same post, but we'd add:
"If you're dealing with a commercial dispute, reply and let's talk."

That simple change increases response rate by 40%.

This is what we do for law firms. Want to see what it looks like 
for your specific practice areas? 15 minutes?
```

**What this means:**
- Script is 60+ seconds (conversational pace)
- Specifically mentions their post topic
- Compliments 1 strength
- Identifies 1 gap
- Shows improvement
- Soft CTA (15 min call)

---

## **PHASE 5: Test Multi-Channel Copy** (5 min)

### **Check outreach drafts**

In API response, look at `results[0].outreach`:

```json
{
  "linkedin": {
    "channel": "LinkedIn",
    "draft": "Hi John, I analyzed your post on commercial property law..."
  },
  "email": {
    "channel": "Email",
    "subject": "Opportunity in your commercial practice",
    "body": "Hi John, I spent 15 minutes analyzing..."
  },
  "instagram": {
    "channel": "Instagram",
    "draft": "Hey John! 👋 Saw your post on property law..."
  }
}
```

**What to test:**
- [ ] LinkedIn DM: under 150 words, professional
- [ ] Email: includes subject + body, has calendar link
- [ ] Instagram: casual, enthusiastic, uses emojis

---

## **PHASE 6: Check Airtable** (5 min)

### **View results in Airtable**

Go to: https://airtable.com → PluggedIN Acquisition base → Content Analysis table

**You should see:**
- [ ] Row for each prospect
- [ ] Prospect name + company filled
- [ ] Analysis JSON
- [ ] Script text
- [ ] Video URL (will be placeholder for now)
- [ ] Outreach drafts (all three channels)
- [ ] Status: "Ready"

---

## **PHASE 7: Test Error Handling** (5 min)

### **Test with bad input:**

```bash
curl -X POST http://localhost:3001/api/content/analyze-and-create-video \
  -H "Content-Type: application/json" \
  -d '{
    "source": "invalid",
    "keywords": [],
    "limit": 0
  }'
```

**Expected:**
- Server should return error message
- No crashes
- Clear error in response

---

## **PHASE 8: Full Flow Test** (20 min)

### **Complete end-to-end test:**

1. ✅ Send API request for legal vertical (5 limits)
2. ✅ Wait for 20 prospects to be processed (2-3 min)
3. ✅ Check response for 3-4 successful prospects
4. ✅ Copy a LinkedIn DM draft
5. ✅ View email subject + body
6. ✅ Check Airtable for new rows
7. ✅ Verify all fields populated

---

## **SUCCESS CRITERIA**

**Pipeline works when:**
- ✅ Scraper finds 3-5 posts from 5 attempts
- ✅ Claude analyzes each post (strengths/gaps)
- ✅ Scripts generated (60+ seconds, personalized)
- ✅ Three outreach drafts created (LinkedIn/Email/Instagram)
- ✅ Records saved to Airtable
- ✅ No errors in logs

**Expected timeline:**
- Scraping: 30-60 seconds (5 prospects)
- Analysis: 10-15 seconds (Claude)
- Script generation: 5-10 seconds
- Outreach drafts: 5-10 seconds
- **Total: ~60-100 seconds for 5 prospects**

---

## **TROUBLESHOOTING**

### **If scraper returns 0 prospects:**
```
→ Check .env has ANTHROPIC_API_KEY + ELEVENLABS_API_KEY
→ Check network (LinkedIn might be blocking)
→ Try Instagram source instead
→ Check browser console for errors
```

### **If Claude analysis fails:**
```
→ Check ANTHROPIC_API_KEY in .env
→ Check Claude API balance (free tier limit: 1M tokens/month)
→ Check API response for error message
```

### **If Airtable save fails:**
```
→ Check AIRTABLE_API_KEY + BASE_ID
→ Verify Content Analysis table exists
→ Check column names match expected schema
```

### **If 11Labs fails:**
```
→ Check ELEVENLABS_API_KEY
→ Check API balance
→ Check script length (should be 100-200 words)
```

---

## **NEXT: VIDEO RENDERING** (Coming Next)

Once scraping + analysis is working:

1. Set up Remotion locally
2. Test Remotion template rendering
3. Merge video + voiceover with FFmpeg
4. Upload final MP4 to cloud storage

**Expected time:** 2-3 hours

---

## **GO/NO-GO CHECKLIST**

After Phase 8, check:
- [ ] Scraper working (finds posts)
- [ ] Analysis working (Claude returns results)
- [ ] Scripts generated (natural language)
- [ ] Three drafts created (personalized per channel)
- [ ] Airtable records saved
- [ ] No unhandled errors

**If all checked:** ✅ Ready for Phase 2 (Video Rendering)

**If any fail:** 🔧 Debug that component before moving forward
