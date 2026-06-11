const express = require('express');
const router = express.Router();
const fs = require('fs');
const path = require('path');
const airtable = require('../lib/airtable-client');
const { findAndSaveLeads, updateLeadStatus, logOutreach } = require('../services/lead-acquisition');

// GET /api/leads/demo - Return mock leads for testing
router.get('/demo', (req, res) => {
  try {
    const mockData = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/mock-leads.json'), 'utf8'));
    const { niche, country } = req.query;

    let filtered = mockData.leads;
    if (niche) {
      filtered = filtered.filter(l => l.niche.toLowerCase() === niche.toLowerCase());
    }

    res.json({
      total: filtered.length,
      leads: filtered,
      demo: true,
      message: 'Demo mode - using mock data'
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// GET /api/leads/demo/:id - Get single lead details (mock)
router.get('/demo/:id', (req, res) => {
  try {
    const mockData = JSON.parse(fs.readFileSync(path.join(__dirname, '../data/mock-leads.json'), 'utf8'));
    const lead = mockData.leads.find(l => l.id === req.params.id);

    if (!lead) {
      return res.status(404).json({ error: 'Lead not found' });
    }

    // Generate recommended approach based on signal score
    let approach = {};
    const score = lead.signalScore;

    if (score >= 85) {
      approach = {
        tier: 'High Priority',
        angle: `${lead.company} is showing strong growth signals and actively hiring. Lead with efficiency angle.`,
        channel: 'Direct call',
        script: `Hi ${lead.title}, I've been following ${lead.company}'s growth and noticed you're expanding. We help firms like yours automate lead qualification and booking - freeing your team to focus on closing. Can I show you in 15 mins?`,
        confidence: 'Very High',
        nextAction: 'Call within 24 hours'
      };
    } else if (score >= 70) {
      approach = {
        tier: 'Medium Priority',
        angle: `${lead.company} has solid fundamentals. Lead with social proof and case study of similar business.`,
        channel: 'Personalized video + email',
        script: `Hi ${lead.title}, I watched ${lead.company}'s work and was impressed. We recently helped a similar firm reduce response time by 60%. Could we grab 15 mins to explore if it fits?`,
        confidence: 'High',
        nextAction: 'Send video + follow up in 3 days'
      };
    } else {
      approach = {
        tier: 'Nurture',
        angle: `${lead.company} has foundation for growth. Lead with problem-solving angle first.`,
        channel: 'Value-first LinkedIn + nurture sequence',
        script: `Hi ${lead.title}, I work with ${lead.niche} firms on the biggest bottleneck - lead response time. Thought you'd find this useful: [resource]. Happy to chat if helpful.`,
        confidence: 'Medium',
        nextAction: 'Send value-first message + nurture'
      };
    }

    res.json({
      ...lead,
      recommendedApproach: approach,
      demo: true
    });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// POST /api/leads/find - Find and save leads (outcome model)
router.post('/find', async (req, res) => {
  try {
    const { country, niche, limit = 50, clientAirtableBase = null } = req.body;

    if (!country || !niche) {
      return res.status(400).json({
        error: 'country and niche are required'
      });
    }

    const result = await findAndSaveLeads(country, niche, limit, clientAirtableBase);
    res.json(result);

  } catch (error) {
    console.error('Error in POST /find:', error);
    res.status(500).json({ error: error.message });
  }
});

// GET /api/leads/stream - Server-Sent Events for real-time progress
router.get('/stream/:country/:niche', (req, res) => {
  try {
    const { country, niche } = req.params;
    const { limit = 50, clientAirtableBase = null } = req.query;

    // Set up SSE headers
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    res.setHeader('Access-Control-Allow-Origin', '*');

    // Send initial connection event
    res.write('data: ' + JSON.stringify({ stage: 'connected', message: 'Stream connected' }) + '\n\n');

    // Simulate progress (in production, this would be event-driven from the service)
    let stage = 0;
    const stages = [
      { name: 'discovering', message: 'Searching for prospects...' },
      { name: 'enriching', message: 'Gathering contact information...' },
      { name: 'saving', message: 'Saving to Airtable...' }
    ];

    const progressInterval = setInterval(() => {
      if (stage < stages.length) {
        res.write('data: ' + JSON.stringify({
          stage: stages[stage].name,
          message: stages[stage].message,
          progress: ((stage + 1) / stages.length) * 100
        }) + '\n\n');
        stage++;
      } else {
        clearInterval(progressInterval);
        // Trigger actual discovery after stream is set up
        findAndSaveLeads(country, niche, parseInt(limit), clientAirtableBase)
          .then(result => {
            res.write('data: ' + JSON.stringify({
              stage: 'complete',
              message: 'Discovery complete',
              result: result
            }) + '\n\n');
            res.end();
          })
          .catch(error => {
            res.write('data: ' + JSON.stringify({
              stage: 'error',
              message: error.message
            }) + '\n\n');
            res.end();
          });
      }
    }, 1000);

    // Handle client disconnect
    req.on('close', () => {
      clearInterval(progressInterval);
    });

  } catch (error) {
    console.error('Error in GET /stream:', error);
    res.status(500).json({ error: error.message });
  }
});

// GET /api/leads - List all leads with optional filtering
router.get('/', async (req, res) => {
  try {
    const { status, source } = req.query;

    // Build Airtable filterByFormula server-side
    const formulaParts = [];
    if (status) formulaParts.push(`{Status}="${status}"`);
    if (source) formulaParts.push(`{Source}="${source}"`);

    const formula = formulaParts.length > 1
      ? `AND(${formulaParts.join(',')})`
      : formulaParts[0] || null;

    const leads = await airtable.getLeads(formula);

    res.json({
      total: leads.length,
      leads: leads
    });

  } catch (error) {
    console.error('Error in GET /leads:', error);
    res.status(500).json({ error: error.message });
  }
});

// GET /api/leads/:id - Get single lead
router.get('/:id', async (req, res) => {
  try {
    const lead = await airtable.getLead(req.params.id);
    res.json(lead);

  } catch (error) {
    console.error('Error in GET /leads/:id:', error);
    res.status(500).json({ error: error.message });
  }
});

// PATCH /api/leads/:id - Update lead status
router.patch('/:id', async (req, res) => {
  try {
    const { status } = req.body;

    if (!status) {
      return res.status(400).json({ error: 'status is required' });
    }

    const result = await updateLeadStatus(req.params.id, status);
    res.json(result);

  } catch (error) {
    console.error('Error in PATCH /leads/:id:', error);
    res.status(500).json({ error: error.message });
  }
});

// POST /api/leads/:id/outreach - Log outreach activity
router.post('/:id/outreach', async (req, res) => {
  try {
    const { leadName, type, message, status = 'Sent' } = req.body;

    if (!type || !message) {
      return res.status(400).json({
        error: 'type and message are required'
      });
    }

    const result = await logOutreach(req.params.id, leadName, type, message, status);
    res.json(result);

  } catch (error) {
    console.error('Error in POST /outreach:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
