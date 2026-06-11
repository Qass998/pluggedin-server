const Airtable = require('airtable');

const base = new Airtable({ apiKey: process.env.AIRTABLE_API_KEY }).base(
  process.env.AIRTABLE_BASE_ACQUISITION || 'appGHRvhTGe9KlQNw'
);

const TABLES = {
  LEADS: 'Leads',
  OUTREACH: 'Outreach',
  PIPELINE: 'Pipeline',
  OPPORTUNITIES: 'Opportunities',
  CONTENT_ANALYSIS: 'Content Analysis',
  LINKEDIN_POSTS: 'LinkedIn Posts',
  GENERATED_VIDEOS: 'Generated Videos'
};

// Create a lead in PluggedIN's base
async function createLead(data) {
  return new Promise((resolve, reject) => {
    base(TABLES.LEADS).create([{ fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

// Create a lead in a client's Airtable base (outcome model)
async function createLeadInBase(clientBaseId, data) {
  return new Promise((resolve, reject) => {
    const clientBase = new Airtable({ apiKey: process.env.AIRTABLE_API_KEY }).base(clientBaseId);
    clientBase('Leads').create([{ fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

// Get all leads with optional filter
async function getLeads(filterBy = null) {
  return new Promise((resolve, reject) => {
    const options = {
      maxRecords: 1000,
      view: 'Grid view'
    };

    if (filterBy && typeof filterBy === 'string') {
      options.filterByFormula = filterBy;
    }

    let records = [];
    base(TABLES.LEADS).select(options)
      .eachPage((recs, fetchNextPage) => {
        records = records.concat(recs.map(r => ({
          id: r.id,
          ...r.fields
        })));
        fetchNextPage();
      }, (err) => {
        if (err) reject(err);
        else resolve(records);
      });
  });
}

// Get lead by ID
async function getLead(id) {
  return new Promise((resolve, reject) => {
    base(TABLES.LEADS).find(id, (err, record) => {
      if (err) reject(err);
      else resolve({ id: record.id, ...record.fields });
    });
  });
}

// Update lead
async function updateLead(id, data) {
  return new Promise((resolve, reject) => {
    base(TABLES.LEADS).update([{ id, fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

// Create outreach record
async function createOutreach(data) {
  return new Promise((resolve, reject) => {
    base(TABLES.OUTREACH).create([{ fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

// Get pipeline metrics
async function getPipelineMetrics() {
  return new Promise((resolve, reject) => {
    base(TABLES.PIPELINE).select({
      view: 'Grid view',
      maxRecords: 100
    }).all((err, records) => {
      if (err) reject(err);
      else resolve(records.map(r => ({
        id: r.id,
        ...r.fields
      })));
    });
  });
}

// Create opportunity
async function createOpportunity(data) {
  return new Promise((resolve, reject) => {
    base(TABLES.OPPORTUNITIES).create([{ fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

// Create content analysis record
async function createContentAnalysis(data) {
  return new Promise((resolve, reject) => {
    base(TABLES.CONTENT_ANALYSIS).create([{ fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

// Get content analysis record
async function getContentAnalysis(prospectId) {
  return new Promise((resolve, reject) => {
    base(TABLES.CONTENT_ANALYSIS).select({
      filterByFormula: `{prospect_id} = "${prospectId}"`,
      maxRecords: 1
    }).all((err, records) => {
      if (err) reject(err);
      else if (records.length === 0) reject(new Error('Not found'));
      else resolve({ id: records[0].id, ...records[0].fields });
    });
  });
}

// Save LinkedIn post
async function saveLinkedInPost(data) {
  return new Promise((resolve, reject) => {
    base(TABLES.LINKEDIN_POSTS).create([{ fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

// Save generated video
async function saveGeneratedVideo(data) {
  return new Promise((resolve, reject) => {
    base(TABLES.GENERATED_VIDEOS).create([{ fields: data }], (err, records) => {
      if (err) reject(err);
      else resolve(records[0]);
    });
  });
}

module.exports = {
  createLead,
  createLeadInBase,
  getLeads,
  getLead,
  updateLead,
  createOutreach,
  getPipelineMetrics,
  createOpportunity,
  createContentAnalysis,
  getContentAnalysis,
  saveLinkedInPost,
  saveGeneratedVideo,
  TABLES
};
