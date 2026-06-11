/**
 * Content Analyzer - Uses Claude to analyze posts/content
 * Generates: strengths, gaps, improvements, script suggestions
 */

const Anthropic = require('@anthropic-ai/sdk');

class ContentAnalyzer {
  constructor(options = {}) {
    this.client = new Anthropic({
      apiKey: process.env.ANTHROPIC_API_KEY,
    });
    this.model = options.model || 'claude-opus-4-8';
  }

  /**
   * Analyze a LinkedIn post
   */
  async analyzeLinkedInPost(post) {
    const prompt = `
You are a LinkedIn content strategist. Analyze this LinkedIn post and provide actionable insights.

POST CONTENT:
Author: ${post.author}
Company: ${post.company}
Content: "${post.content}"
Metrics: ${post.likes} likes, ${post.comments} comments, ${post.shares} shares

Provide a JSON response with:
{
  "strengths": ["list 2-3 things working well"],
  "gaps": ["list 2-3 improvement areas"],
  "engagement_analysis": "brief analysis of engagement rate",
  "hook_strength": "score 1-10 + brief reason",
  "cta_effectiveness": "score 1-10 + brief reason",
  "improvements": [
    "specific actionable improvement 1",
    "specific actionable improvement 2"
  ],
  "rewritten_hook": "better opening line",
  "rewritten_cta": "stronger call-to-action"
}

Be specific and actionable. Focus on what would increase engagement.
`;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      });

      const content = response.content[0].text;
      return JSON.parse(content);
    } catch (error) {
      console.error('[ContentAnalyzer] Error analyzing LinkedIn post:', error.message);
      return this._defaultAnalysis();
    }
  }

  /**
   * Analyze an Instagram video
   */
  async analyzeInstagramVideo(video) {
    const prompt = `
You are an Instagram content strategist. Analyze this Instagram video and provide insights.

VIDEO INFO:
Author: ${video.authorUsername}
Caption: "${video.caption}"
Metrics: ${video.likes} likes, ${video.comments} comments

Provide a JSON response with:
{
  "strengths": ["list 2-3 things working well"],
  "gaps": ["list 2-3 improvement areas"],
  "hook_strength": "score 1-10 + brief reason",
  "retention_potential": "how engaging is the first 3 seconds? score 1-10",
  "improvements": [
    "specific editing suggestion 1",
    "specific music/audio suggestion",
    "specific caption improvement"
  ],
  "improved_caption": "better version of the caption",
  "content_suggestions": ["what type of content would perform better for this creator"]
}

Focus on video-specific improvements: hook, pacing, music, captions.
`;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 1000,
        messages: [{ role: 'user', content: prompt }],
      });

      const content = response.content[0].text;
      return JSON.parse(content);
    } catch (error) {
      console.error('[ContentAnalyzer] Error analyzing Instagram video:', error.message);
      return this._defaultAnalysis();
    }
  }

  /**
   * Generate a personalized outreach script
   */
  async generateOutreachScript(prospect, analysis, channel) {
    const prompts = {
      linkedin: `
Generate a professional LinkedIn DM that:
1. References their specific post about "${analysis.content_topic || 'their post'}"
2. Compliments what's working (mention 1 strength)
3. Offers specific improvement (1 gap you identified)
4. Positions us as the solution
5. Includes a soft CTA (15-min conversation)

Keep it under 150 words. Tone: helpful expert, not salesy.

Prospect: ${prospect.author}
Their strength: ${analysis.strengths?.[0] || 'engaging content'}
Improvement area: ${analysis.gaps?.[0] || 'stronger CTA'}

Return ONLY the script text, no JSON.
      `,
      email: `
Generate a professional email that:
1. Subject line that references their post/content
2. Opens with specific compliment
3. Shows analysis (2 strengths, 1 gap)
4. Offers solution with example
5. Includes calendar link CTA

Keep body under 200 words. Tone: professional, data-driven.

Prospect: ${prospect.author}
Company: ${prospect.company}
Content: "${prospect.content}".

Return the full email (subject + body), formatted clearly.
      `,
      instagram: `
Generate a casual Instagram DM that:
1. References their specific video/post
2. Shows you analyzed it (compliment + improvement idea)
3. Offers to create better versions
4. Soft ask for 15-min call

Keep it under 100 words. Tone: creator-to-creator, casual, enthusiastic.

Creator: ${prospect.authorUsername}
Their content: ${video.caption || 'great video'}

Return ONLY the script text, no JSON.
      `,
    };

    const prompt = prompts[channel] || prompts.email;

    try {
      const response = await this.client.messages.create({
        model: this.model,
        max_tokens: 500,
        messages: [{ role: 'user', content: prompt }],
      });

      return response.content[0].text.trim();
    } catch (error) {
      console.error(`[ContentAnalyzer] Error generating ${channel} script:`, error.message);
      return 'Unable to generate script at this time.';
    }
  }

  /**
   * Default analysis fallback
   */
  _defaultAnalysis() {
    return {
      strengths: ['clear message'],
      gaps: ['could strengthen CTA'],
      improvements: ['add social proof', 'strengthen hook'],
      engagement_analysis: 'moderate engagement',
      hook_strength: 5,
      cta_effectiveness: 4,
    };
  }
}

module.exports = ContentAnalyzer;
