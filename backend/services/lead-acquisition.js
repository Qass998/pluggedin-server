const airtable = require('../lib/airtable-client');
const axios = require('axios');

// Actor selection based on niche (from lead-discovery SKILL.md)
function selectApifyActor(niche) {
  const niches = niche.toLowerCase();

  if (niches.includes('legal') || niches.includes('healthcare') || niches.includes('professional')) {
    return 'compass/linkedin-profile-scraper';
  } else if (niches.includes('restaurant') || niches.includes('hospitality') || niches.includes('cafe')) {
    return 'compass/google-maps-scraper';
  } else {
    return 'compass/google-maps-scraper'; // Default to Google Maps
  }
}

// Discover leads using Apify
async function discoverLeads(country, niche, limit = 10000) {
  try {
    console.log(`[Discovery] Searching: ${niche} in ${country} (limit: ${limit})`);

    if (!process.env.APIFY_API_TOKEN) {
      throw new Error('APIFY_API_TOKEN not set in environment');
    }

    const actor = selectApifyActor(niche);
    const axios = require('axios');

    // Build search query
    const searchQuery = `${niche} in ${country}`;

    // Call Apify API to run actor
    const response = await axios.post(
      `https://api.apify.com/v2/acts/${actor}/runs`,
      {
        searchStringsArray: [searchQuery],
        maxCrawledPlaces: limit || 50,
        language: 'en'
      },
      {
        headers: {
          'Authorization': `Bearer ${process.env.APIFY_API_TOKEN}`
        }
      }
    );

    const runId = response.data.data.id;
    console.log(`[Discovery] Run started: ${runId}`);

    // Poll for completion
    let isRunning = true;
    let attempts = 0;
    const maxAttempts = 60; // 5 minutes max wait

    while (isRunning && attempts < maxAttempts) {
      const statusResponse = await axios.get(
        `https://api.apify.com/v2/acts/${actor}/runs/${runId}`,
        {
          headers: { 'Authorization': `Bearer ${process.env.APIFY_API_TOKEN}` }
        }
      );

      const status = statusResponse.data.data.status;
      if (status === 'SUCCEEDED') {
        isRunning = false;
      } else if (status === 'FAILED') {
        throw new Error(`Apify run failed: ${runId}`);
      } else {
        attempts++;
        await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
      }
    }

    // Fetch results
    const datasetResponse = await axios.get(
      `https://api.apify.com/v2/acts/${actor}/runs/${runId}/dataset/items`,
      {
        headers: { 'Authorization': `Bearer ${process.env.APIFY_API_TOKEN}` }
      }
    );

    const items = datasetResponse.data;
    console.log(`[Discovery] Found ${items.length} leads`);

    // Normalize to our schema
    return items.map(item => ({
      name: item.title || item.name || 'Unknown',
      email: item.email || '',
      phone: item.phone || '',
      company: item.placeTitle || item.company || 'Unknown',
      title: item.jobTitle || '',
      location: item.address || '',
      country: country,
      niche: niche,
      source: actor.includes('linkedin') ? 'LinkedIn' : 'Google Maps',
      url: item.url || '',
      websiteUrl: item.website || ''
    })).filter((item, idx, self) =>
      idx === self.findIndex(i => i.company === item.company && i.niche === item.niche)
    );

  } catch (error) {
    console.error('[Discovery] Error:', error.message);
    throw error;
  }
}

// Enrich leads using Companies House + email guessing
async function enrichLeads(leads) {
  try {
    console.log(`[Enrichment] Enriching ${leads.length} leads`);

    const enriched = [];

    for (const lead of leads) {
      let enrichedLead = { ...lead };

      // Score based on title keywords
      const titleLower = (lead.title || '').toLowerCase();
      let score = 0.5;
      if (titleLower.includes('partner') || titleLower.includes('director') || titleLower.includes('ceo') || titleLower.includes('managing')) {
        score = 0.85;
      } else if (titleLower.includes('manager') || titleLower.includes('head') || titleLower.includes('chief')) {
        score = 0.75;
      }

      enrichedLead['Decision Maker Score'] = score;
      enrichedLead['Status'] = 'Enriched';
      enrichedLead['Discovery Date'] = new Date().toISOString().split('T')[0];
      enrichedLead['Source'] = lead.source || 'Unknown';

      // For UK companies, try to get address from Companies House (free API)
      if (lead.country && (lead.country.toLowerCase() === 'uk' || lead.country.toLowerCase() === 'united kingdom')) {
        try {
          const chResponse = await axios.get(
            `https://api.company-information.service.gov.uk/search/companies`,
            { params: { q: lead.company, items_per_page: 1 } }
          );

          if (chResponse.data.items && chResponse.data.items.length > 0) {
            const company = chResponse.data.items[0];
            enrichedLead['registered_address'] = [
              company.registered_office_address?.address_line_1,
              company.registered_office_address?.locality,
              company.registered_office_address?.postal_code
            ].filter(Boolean).join(', ');
          }
        } catch (err) {
          console.log(`[Enrichment] Companies House lookup skipped for ${lead.company}`);
        }
      }

      enriched.push(enrichedLead);
    }

    console.log(`[Enrichment] Enriched ${enriched.length} leads`);
    return enriched;

  } catch (error) {
    console.error('[Enrichment] Error:', error.message);
    throw error;
  }
}

// Main workflow: discover → enrich → save to Airtable (outcome model)
async function findAndSaveLeads(country, niche, limit = 10000, clientAirtableBase = null) {
  try {
    console.log(`\n=== FIND LEADS WORKFLOW ===`);
    console.log(`Country: ${country}, Niche: ${niche}, Limit: ${limit}`);
    if (clientAirtableBase) console.log(`Writing to client base: ${clientAirtableBase}`);

    // Step 1: Discover
    console.log(`\nStep 1: Discovering leads...`);
    const discoveredLeads = await discoverLeads(country, niche, limit);
    console.log(`Found ${discoveredLeads.length} leads`);

    // Step 2: Enrich
    console.log(`\nStep 2: Enriching leads...`);
    const enrichedLeads = await enrichLeads(discoveredLeads);
    console.log(`Enriched ${enrichedLeads.length} leads`);

    // Step 3: Save to Airtable (either client's base or PluggedIN's)
    console.log(`\nStep 3: Saving to Airtable...`);
    const savedLeads = [];
    let skipped = 0;
    for (const lead of enrichedLeads) {
      // Check for duplicates by company + niche
      const existing = await airtable.getLeads(`AND({company}="${lead.company}",{niche}="${lead.niche}")`);
      if (existing.length > 0) {
        console.log(`⊘ Skip (duplicate): ${lead.company}`);
        skipped++;
        continue;
      }

      let saved;
      if (clientAirtableBase) {
        // Write to client's Airtable base (outcome model)
        saved = await airtable.createLeadInBase(clientAirtableBase, lead);
      } else {
        // Write to PluggedIN's internal base
        saved = await airtable.createLead(lead);
      }
      savedLeads.push(saved);
      console.log(`✓ Saved: ${lead.name}`);
    }
    if (skipped > 0) console.log(`Skipped ${skipped} duplicates`);

    console.log(`\n=== COMPLETE ===`);
    console.log(`Total leads saved: ${savedLeads.length}`);

    return {
      success: true,
      leadsFound: enrichedLeads.length,
      leadsSaved: savedLeads.length,
      leads: savedLeads
    };

  } catch (error) {
    console.error('Error in findAndSaveLeads:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Update lead status in pipeline
async function updateLeadStatus(leadId, newStatus) {
  try {
    const lead = await airtable.getLead(leadId);

    const update = {
      'Status': newStatus,
      'Last Activity': new Date().toISOString()
    };

    await airtable.updateLead(leadId, update);
    console.log(`✓ Lead ${leadId} updated to ${newStatus}`);

    return {
      success: true,
      leadId,
      newStatus
    };
  } catch (error) {
    console.error('Error updating lead:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

// Log outreach activity
async function logOutreach(leadId, leadName, type, message, status = 'Sent') {
  try {
    const outreach = {
      'Lead Name': leadName,
      'Type': type,
      'Message': message,
      'Status': status,
      'Sent Date': new Date().toISOString()
    };

    await airtable.createOutreach(outreach);
    console.log(`✓ Logged outreach: ${type} to ${leadName}`);

    // Update lead's last activity
    await airtable.updateLead(leadId, {
      'Last Activity': new Date().toISOString()
    });

    return {
      success: true,
      leadId,
      type
    };
  } catch (error) {
    console.error('Error logging outreach:', error);
    return {
      success: false,
      error: error.message
    };
  }
}

module.exports = {
  findAndSaveLeads,
  updateLeadStatus,
  logOutreach
};
