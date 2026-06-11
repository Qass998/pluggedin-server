const express = require('express');
const router = express.Router();
const airtable = require('../lib/airtable-client');

// GET /api/pipeline - Get pipeline metrics
router.get('/', async (req, res) => {
  try {
    const leads = await airtable.getLeads();

    // Calculate metrics by status
    const statusCounts = {};
    const statuses = ['Discovered', 'Enriched', 'Contacted', 'Replied', 'Meeting Booked', 'Proposal Sent', 'Closed Won', 'Closed Lost'];

    statuses.forEach(status => {
      statusCounts[status] = leads.filter(l => l.Status === status).length;
    });

    // Calculate conversion rates
    const discovered = statusCounts['Discovered'] || 0;
    const enriched = statusCounts['Enriched'] || 0;
    const contacted = statusCounts['Contacted'] || 0;
    const replied = statusCounts['Replied'] || 0;
    const meetingBooked = statusCounts['Meeting Booked'] || 0;
    const proposalSent = statusCounts['Proposal Sent'] || 0;
    const closedWon = statusCounts['Closed Won'] || 0;

    const conversions = {
      'Discovered to Enriched': discovered > 0 ? ((enriched / discovered) * 100).toFixed(1) : 0,
      'Enriched to Contacted': enriched > 0 ? ((contacted / enriched) * 100).toFixed(1) : 0,
      'Contacted to Replied': contacted > 0 ? ((replied / contacted) * 100).toFixed(1) : 0,
      'Replied to Meeting': replied > 0 ? ((meetingBooked / replied) * 100).toFixed(1) : 0,
      'Meeting to Proposal': meetingBooked > 0 ? ((proposalSent / meetingBooked) * 100).toFixed(1) : 0,
      'Proposal to Won': proposalSent > 0 ? ((closedWon / proposalSent) * 100).toFixed(1) : 0
    };

    res.json({
      totalLeads: leads.length,
      byStatus: statusCounts,
      conversionRates: conversions,
      pipeline: [
        { stage: 'Discovered', count: discovered },
        { stage: 'Enriched', count: enriched },
        { stage: 'Contacted', count: contacted },
        { stage: 'Replied', count: replied },
        { stage: 'Meeting Booked', count: meetingBooked },
        { stage: 'Proposal Sent', count: proposalSent },
        { stage: 'Closed Won', count: closedWon }
      ]
    });

  } catch (error) {
    console.error('Error in GET /pipeline:', error);
    res.status(500).json({ error: error.message });
  }
});

module.exports = router;
