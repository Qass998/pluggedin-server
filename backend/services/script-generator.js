/**
 * Script Generator - Creates voiceover scripts for videos
 * Uses Claude to write natural, engaging scripts
 */

const Anthropic = require('@anthropic-ai/sdk');
const axios = require('axios');

class ScriptGenerator {
  constructor(options = {}) {
    this.claude = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    this.model = options.model || 'claude-sonnet-4-6';
    this.voiceId = options.voiceId || 'EXAVITQu4vr4xnSDxMaL'; // Default: professional male
  }

  /**
   * Generate signal-based LinkedIn script (60 seconds)
   * Uses prospect signals + engagement angle for hyper-personalization
   */
  async generateLinkedInScript(prospect, signalAnalysis) {
    const {
      name,
      title,
      company,
    } = prospect;

    const {
      interests,
      pain_points,
      engagement_angle,
      competitor_opportunities,
      value_promise,
      personalization_tactics,
    } = signalAnalysis.analysis;

    const prompt = `
Create a natural 60-second LinkedIn video script for ${name}, ${title} at ${company}.

Based on their LinkedIn signals, they care about: ${interests.join(', ')}
Their pain points: ${pain_points.join(', ')}
Best angle to reach them: ${engagement_angle}

${competitor_opportunities?.length > 0 ? `They follow competitors, so reference: ${competitor_opportunities[0]}` : ''}

Create a natural, conversational script (60 seconds ≈ 150 words):

1. [0-5s] Personalized greeting: "Hi ${name}, I noticed you're focused on [their interest]"
2. [5-15s] Show you understand their world: reference company/competitor/topic they care about
3. [15-35s] Specific insight: "Here's what [competitor/company] is doing that works"
4. [35-50s] Value: "We help ${title}s like you do this too. Results: [specific outcome]"
5. [50-60s] Soft CTA: "Worth 15 minutes to see how?"

Requirements:
- Sound like you actually analyzed them (reference their interests)
- Conversational, confident, no marketing speak
- Specific to THEM, not generic
- End with curiosity, not pushiness
- NEVER mention pricing

Return ONLY the script text, no meta commentary.
`;

    try {
      const response = await this.claude.messages.create({
        model: this.model,
        max_tokens: 300,
        messages: [{ role: 'user', content: prompt }],
      });

      const script = response.content[0].text.trim();
      return {
        script,
        wordCount: script.split(/\s+/).length,
        estimatedSeconds: Math.round((script.split(/\s+/).length / 150) * 60),
        personalized: true,
      };
    } catch (error) {
      console.error('[ScriptGenerator] Error generating signal-based script:', error.message);
      return this._defaultScript();
    }
  }

  /**
   * Generate Instagram video improvement script (45 seconds)
   */
  async generateInstagramScript(creator, analysis) {
    const prompt = `
Create a 45-second conversational voiceover script for a video about improving an Instagram creator's content.

The creator: ${creator.authorUsername}
Caption: "${creator.caption}"
Analysis:
- Strengths: ${analysis.strengths?.join(', ') || 'visual appeal'}
- Gaps: ${analysis.gaps?.join(', ') || 'hook timing'}

Script structure:
1. [0-5s] Compliment their specific video/content
2. [5-20s] Show what's working (1 strength)
3. [20-35s] Suggest 1 specific improvement + why it matters
4. [35-45s] Offer to create this + CTA

Make it sound like creator-to-creator, casual and enthusiastic.
Return ONLY the script text.
`;

    try {
      const response = await this.claude.messages.create({
        model: this.model,
        max_tokens: 250,
        messages: [{ role: 'user', content: prompt }],
      });

      const script = response.content[0].text.trim();
      return {
        script,
        wordCount: script.split(/\s+/).length,
        estimatedSeconds: Math.round((script.split(/\s+/).length / 150) * 45),
      };
    } catch (error) {
      console.error('[ScriptGenerator] Error generating Instagram script:', error.message);
      return this._defaultScript();
    }
  }

  /**
   * Convert script to voiceover audio using ElevenLabs REST API
   */
  async generateVoiceover(script, options = {}) {
    const {
      voiceId = this.voiceId,
      stability = 0.5,
      similarity = 0.75,
    } = options;

    if (!process.env.ELEVENLABS_API_KEY) {
      throw new Error('ELEVENLABS_API_KEY not set in environment');
    }

    try {
      console.log(`[ElevenLabs] Generating voiceover (${script.split(/\s+/).length} words)...`);

      const response = await axios.post(
        `https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`,
        {
          text: script,
          model_id: 'eleven_multilingual_v2',
          voice_settings: {
            stability,
            similarity_boost: similarity,
          },
        },
        {
          headers: {
            'xi-api-key': process.env.ELEVENLABS_API_KEY,
            'Content-Type': 'application/json',
          },
          responseType: 'arraybuffer',
        }
      );

      const audio = Buffer.from(response.data);
      return {
        audio,
        format: 'mp3',
        sizeBytes: audio.length,
      };
    } catch (error) {
      console.error('[ElevenLabs] Error generating voiceover:', error.message);
      throw error;
    }
  }

  /**
   * Full pipeline: script + voiceover
   */
  async generateScriptAndVoiceover(prospect, analysis, type = 'linkedin') {
    console.log(`[ScriptGenerator] Generating ${type} script and voiceover...`);

    let scriptResult;
    if (type === 'linkedin') {
      scriptResult = await this.generateLinkedInScript(prospect, analysis);
    } else if (type === 'instagram') {
      scriptResult = await this.generateInstagramScript(prospect, analysis);
    } else {
      throw new Error(`Unknown script type: ${type}`);
    }

    const voiceoverResult = await this.generateVoiceover(scriptResult.script);

    return {
      script: scriptResult.script,
      wordCount: scriptResult.wordCount,
      estimatedSeconds: scriptResult.estimatedSeconds,
      voiceover: voiceoverResult,
      ready: true,
    };
  }

  /**
   * Default fallback script
   */
  _defaultScript() {
    return {
      script: 'Hi there. I analyzed your content and found some opportunities to improve your engagement. Let\'s talk about how we can help.',
      wordCount: 26,
      estimatedSeconds: 10,
    };
  }
}

module.exports = ScriptGenerator;
