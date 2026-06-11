/**
 * Content Analysis & Video Generation API
 * POST /api/content/analyze-and-create-video
 */

const express = require('express');
const router = express.Router();

// const ObscuraScraper = require('../scrapers/obscura-scraper');
// const ContentAnalyzer = require('../services/content-analyzer');
const ScriptGenerator = require('../services/script-generator');
const VideoGenerator = require('../services/video-generator');
// const OutreachDrafts = require('../services/outreach-drafts');
// const AirtableClient = require('../lib/airtable-client');

/**
 * POST /api/content/create-signal-based-outreach
 *
 * NEW SIGNAL-BASED PIPELINE:
 * Find people → Extract signals → Analyze signals → Generate personalized video → Create outreach
 */
/*
router.post('/create-signal-based-outreach', async (req, res) => {
  try {
    const {
      jobTitles = [],              // ["CMO", "VP Marketing"]
      industries = [],             // ["SaaS", "Ecommerce"]
      companySizes = [],           // [100, 5000]
      locations = ["UK"],          // ["UK", "US"]
      limit = 20,                  // number to process
      vertical = 'legal',          // business vertical
    } = req.body;

    console.log(`[API] Starting signal-based outreach pipeline...`);
    console.log(`  Job titles: ${jobTitles}, Industries: ${industries}, Limit: ${limit}`);

    const results = [];
    const errors = [];

    // Step 1: Initialize services
    const SignalAnalyzer = require('../services/signal-analyzer');
    const scraper = new ObscuraScraper({ maxConcurrent: 5 });
    const signalAnalyzer = new SignalAnalyzer();
    const scriptGen = new ScriptGenerator();
    const videoGen = new VideoGenerator();
    const draftsGen = new OutreachDrafts();
    const airtable = new AirtableClient();

    await scraper.initialize();

    try {
      // Step 2: Find LinkedIn PEOPLE matching criteria + extract SIGNALS
      const peopleWithSignals = await scraper.scrapeLinkedInPeopleWithSignals({
        jobTitles: jobTitles.length > 0 ? jobTitles : [vertical],
        industries: industries.length > 0 ? industries : [vertical],
        companySizes,
        locations,
        limit,
      });

      console.log(`[API] Found ${peopleWithSignals.length} prospects with signals`);

      // Step 3: Analyze signals + generate videos
      for (const prospect of peopleWithSignals.slice(0, limit)) {
        try {
          console.log(`[API] Processing: ${prospect.name}...`);

          // Step 3a: Analyze their SIGNALS to determine best engagement angle
          const signalResult = await signalAnalyzer.analyzeProspectSignals(prospect);

          if (!signalResult.success) {
            throw new Error('Signal analysis failed');
          }

          const signalAnalysis = signalResult.analysis;

          // Step 3b: Generate personalized script based on signals
          const { script, wordCount, estimatedSeconds } = await scriptGen.generateLinkedInScript(
            prospect,
            signalResult
          );

          // Step 3c: Generate voiceover
          const voiceoverResult = await scriptGen.generateVoiceover(script);

          // Step 3d: Generate video with embedded audio
          const videoResult = await videoGen.generateProspectVideo(
            prospect,
            signalAnalysis,
            voiceoverResult.audio
          );
          const videoUrl = `${req.protocol}://${req.get('host')}${videoResult.videoUrl}`;

          // Step 3e: Generate multi-channel outreach drafts
          const drafts = await draftsGen.generateAllDrafts(
            prospect,
            signalAnalysis,
            videoUrl,
            'linkedin'
          );

          // Step 3f: Save to Airtable
          const airtableRecord = await airtable.createContentAnalysis({
            prospect_id: `${prospect.name}`,
            source: 'linkedin-signals',
            prospect_name: prospect.name,
            title: prospect.title,
            company: prospect.company,
            location: prospect.location,
            signals: JSON.stringify(prospect.signals),
            signal_analysis: JSON.stringify(signalAnalysis),
            engagement_angle: signalAnalysis.engagement_angle,
            confidence_score: signalAnalysis.confidence_score,
            script,
            video_url: videoUrl,
            outreach_drafts: JSON.stringify(drafts),
            status: 'Ready',
          });

          results.push({
            prospect: {
              name: prospect.name,
              title: prospect.title,
              company: prospect.company,
              location: prospect.location,
            },
            signals: prospect.signals,
            analysis: signalAnalysis,
            script: {
              wordCount,
              estimatedSeconds,
            },
            video: {
              url: videoUrl,
              duration: 60,
            },
            outreach: drafts,
            airtable_id: airtableRecord.id,
            ready: true,
          });

          console.log(`  ✓ ${prospect.name} processed - angle: ${signalAnalysis.engagement_angle}`);
        } catch (error) {
          errors.push({
            prospect: prospect.name,
            error: error.message,
          });
          console.error(`  ✗ Error: ${error.message}`);
        }
      }

      // Step 4: Cleanup
      await scraper.close();

      // Response
      res.json({
        success: true,
        summary: {
          total_processed: results.length,
          total_errors: errors.length,
          job_titles: jobTitles,
          industries,
          vertical,
        },
        results,
        errors,
      });
    } catch (error) {
      await scraper.close();
      throw error;
    }
  } catch (error) {
    console.error('[API] Pipeline error:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
    });
  }
});
*/

/**
 * GET /api/content/status/:prospectId
 * Check video generation status
 */
/*
router.get('/status/:prospectId', async (req, res) => {
  try {
    const { prospectId } = req.params;
    const airtable = new AirtableClient();

    const record = await airtable.getContentAnalysis(prospectId);

    res.json({
      success: true,
      prospect_id: prospectId,
      status: record.status,
      video_url: record.video_url,
      outreach_ready: record.status === 'Ready',
    });
  } catch (error) {
    res.status(500).json({ success: false, error: error.message });
  }
});
*/

/**
 * POST /api/content/generate-video
 * Simple endpoint for dashboard video generation testing
 * No signal analysis, just raw prospect data + voiceover toggle
 */
router.post('/generate-video', async (req, res) => {
  try {
    const {
      prospectName,
      company,
      title = '',
      niche = 'General',
      interests = [],
      engagementAngle = '',
      generateVoiceover: withVoice = true,
    } = req.body;

    if (!prospectName || !company) {
      return res.status(400).json({ success: false, error: 'prospectName and company required' });
    }

    const scriptGen = new ScriptGenerator();
    const videoGen = new VideoGenerator();

    const prospect = { name: prospectName, company, title };
    const analysis = {
      interests: interests.length > 0 ? interests : [`Growing ${niche} business`],
      pain_points: [`Scaling ${company}`],
      engagement_angle: engagementAngle || `How AI agents can transform ${company}'s operations`,
      value_promise: 'Book 15 minutes to see it live',
      confidence_score: 0.85,
    };

    let voiceBuffer = null;

    // Step 1: Generate script
    const scriptResult = await scriptGen.generateLinkedInScript(prospect, { analysis });

    // Step 2: Generate voiceover (if enabled)
    if (withVoice && process.env.ELEVENLABS_API_KEY) {
      try {
        const voiceoverResult = await scriptGen.generateVoiceover(scriptResult.script);
        voiceBuffer = voiceoverResult.audio;
      } catch (error) {
        console.warn('[API] Voiceover generation failed, proceeding without audio:', error.message);
      }
    }

    // Step 3: Generate video with optional audio
    const videoResult = await videoGen.generateProspectVideo(prospect, analysis, voiceBuffer);

    res.json({
      success: true,
      videoId: videoResult.videoId,
      videoUrl: `${req.protocol}://${req.get('host')}${videoResult.videoUrl}`,
      fileSizeKB: videoResult.fileSizeKB,
      script: scriptResult.script,
      wordCount: scriptResult.wordCount,
      estimatedSeconds: scriptResult.estimatedSeconds,
      hasVoiceover: !!voiceBuffer,
    });
  } catch (error) {
    console.error('[API] Video generation error:', error.message);
    res.status(500).json({ success: false, error: error.message });
  }
});

module.exports = router;
