# Lead Discovery Service — Implementation Status

## ✅ COMPLETED

### 1. Fixed airtable-client.js
- ✅ Fixed broken `.where()` method in `getLeads()` → now uses `filterByFormula`
- ✅ Added `createLeadInBase()` for outcome model (write to client's Airtable base)
- ✅ Exported new function in module.exports

### 2. Real Discovery + Enrichment (lead-acquisition.js)
- ✅ Replaced mock `discoverLeads()` with real Apify integration
  - Actor selection logic based on niche (LinkedIn for legal/pro, Google Maps for others)
  - Calls Apify API, waits for completion, fetches results
  - Normalizes output to standard schema
- ✅ Replaced mock `enrichLeads()` with 3-source pipeline
  - ICP scoring based on title keywords
  - Companies House API for UK companies (free, no auth)
  - Email guessing (simple pattern-based)
- ✅ Updated `findAndSaveLeads()` to support `clientAirtableBase` parameter
  - If provided, writes to client's base (outcome model)
  - If not, writes to PluggedIN internal base

### 3. API Routes (routes/leads.js)
- ✅ Updated `POST /api/leads/find` to accept `clientAirtableBase` parameter
- ✅ Added `GET /api/leads/stream/:country/:niche` SSE endpoint for real-time progress
  - Streams progress events: discovering → enriching → saving → complete
  - Triggers actual discovery after stream connection established

---

## ⏳ REMAINING (Dashboard UI Update)

The dashboard HTML needs to be updated at lines **2260–2450** in `/dashboard/index.html`:

### Changes needed:

1. **Add input form section:**
   ```html
   <div class="form-group">
     <label>Industry:</label>
     <select id="disc-industry">
       <option value="">-- Select Industry --</option>
       <option value="Legal">Legal</option>
       <option value="Restaurant">Restaurant</option>
       <option value="Construction">Construction</option>
       <option value="Healthcare">Healthcare</option>
       <!-- More options -->
     </select>
   </div>
   <div class="form-group">
     <label>Country:</label>
     <input type="text" id="disc-country" placeholder="e.g. UK, US" value="UK">
   </div>
   <div class="form-group">
     <label>Limit:</label>
     <select id="disc-limit">
       <option value="10">10</option>
       <option value="25">25</option>
       <option value="50" selected>50</option>
     </select>
   </div>
   <button id="disc-run-btn">▶ RUN DISCOVERY</button>
   ```

2. **Replace loadLeads() function:**
   - Change endpoint from `/api/results/leads` to `/api/leads`
   - Return real data from Airtable instead of falling back to demo data

3. **Add progress display:**
   - Connect to `GET /api/leads/stream/:country/:niche` SSE
   - Show live progress: discovering (●) → enriching (○) → saving (○)
   - Update counts dynamically

4. **Wire button click handler:**
   ```js
   document.getElementById('disc-run-btn').addEventListener('click', async () => {
     const industry = document.getElementById('disc-industry').value;
     const country = document.getElementById('disc-country').value;
     const limit = document.getElementById('disc-limit').value;

     // Validate
     if (!industry || !country) {
       alert('Please select industry and country');
       return;
     }

     // Show progress
     // Connect to SSE stream
     const eventSource = new EventSource(`/api/leads/stream/${country}/${industry}?limit=${limit}`);
     
     eventSource.onmessage = (event) => {
       const data = JSON.parse(event.data);
       updateProgress(data);
     };

     // Fetch results when complete
     eventSource.addEventListener('complete', () => {
       loadLeads(); // This will now hit /api/leads (no demo fallback)
       eventSource.close();
     });
   });
   ```

5. **Remove demo data fallback:**
   - Keep demo data as fallback ONLY when API returns no results
   - Once working, demo data should only appear for demo purposes

---

## Testing Checklist

Before deploying:

- [ ] Set `APIFY_API_TOKEN` in `.env`
- [ ] `POST /api/leads/find` with `{ country: "UK", niche: "Legal", limit: 10 }`
  - Expect: 10 real UK legal leads saved to Airtable
- [ ] Open dashboard → Find Leads section
  - Enter: Industry = Legal, Country = UK, Limit = 10
  - Click "Run Discovery"
  - Watch progress update in real-time
  - See real leads appear (with Decision Maker Scores, etc.)
  - Verify leads appear in Airtable Leads table
- [ ] Test `clientAirtableBase` parameter:
  - `POST /api/leads/find` with `{ country: "UK", niche: "Legal", limit: 5, clientAirtableBase: "app..." }`
  - Verify leads appear in client's Airtable base instead of PluggedIN's

---

## Environment Variables Required

```env
APIFY_API_TOKEN=<your-token>           # Required for discovery
COMPANIES_HOUSE_API_KEY=               # Optional, free API
HUNTER_API_KEY=                        # Optional, free tier 50/month
AIRTABLE_API_KEY=                      # Already set
AIRTABLE_BASE_ACQUISITION=             # Already set
```

---

## Next Steps

1. **Immediate:** Set APIFY_API_TOKEN in .env and test the API endpoints via curl/Postman
2. **Short-term:** Update dashboard HTML (Step 4)
3. **Short-term:** Test full pipeline: dashboard → API → Airtable
4. **Future:** Add real-time event emission to discovery service (currently simulated progress)
5. **Future:** Add Hunter.io integration for email verification
6. **Future:** Refine Companies House integration (currently basic)

---

## Architecture Summary

```
Dashboard Form
    ↓
POST /api/leads/find
    ├─ country, niche, limit, clientAirtableBase
    ↓
discoverLeads()
    ├─ Select Apify actor (LinkedIn or Google Maps)
    ├─ Call Apify API
    ├─ Poll for completion
    ├─ Fetch results
    └─ Return normalized leads
    ↓
enrichLeads()
    ├─ Score by title keywords
    ├─ Lookup Companies House (UK)
    ├─ Guess emails
    └─ Return enriched leads
    ↓
Save to Airtable
    ├─ If clientAirtableBase → createLeadInBase()
    └─ Else → createLead() (internal)
    ↓
Dashboard receives results
    └─ Display leads with scores, sources, emails
```

---

**Status: 75% complete. Dashboard UI remaining.**
